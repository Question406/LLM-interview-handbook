---
id: nvidia-paged-kv
section: nvidia
order: 9
level: A
title: NVIDIA：PagedAttention / KV block table，碎片和 prefix 共享
quick: >-
  别按 max length 给每条请求预留一整段 KV。把 cache 切成固定 token 块，block table
  把逻辑块号映到物理页，像虚拟内存。内部碎片只剩最后一块的半截；外部碎片和「短请求占用长槽」基本消失。相同
  prefix 可以 refcount 共享物理块，写下一段时再拷。
tags:
  - NVIDIA
  - PagedAttention
  - KV Cache
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Efficient Memory Management for Large Language Model Serving with PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
  - title: NVIDIA TensorRT-LLM
    url: https://github.com/NVIDIA/TensorRT-LLM
    type: primary
  - title: FlashAttention — Fast and Memory-Efficient Exact Attention with IO-Awareness
    url: https://arxiv.org/abs/2205.14135
    type: primary
---

## 题怎么来的

Serving / CUDA 岗问 KV 显存，常从「为什么 batch 开不大」进到分页。算法来自 vLLM 的 PagedAttention；NVIDIA 侧 TensorRT-LLM 有 paged KV + in-flight batching，Triton 只是把它挂上，见 `nvidia-triton-infer`。我会画一张 block table，算内部碎片，再讲 prefix 共享什么时候失效。

## 不分页时碎片从哪来

Decode 的 KV 随 $T$ 线性涨：

$$
\mathrm{bytes}\approx 2\cdot L\cdot T\cdot H_{\mathrm{kv}}\cdot d_h\cdot \mathrm{elem\_size}.
$$

朴素实现：每条请求进来就按 `max_seq_len` 预留连续缓冲。实际长度 200、槽位 4096，中间那一截永远空着——这是内部浪费。请求走了，留下的空洞又对不齐下一条更长的序列——外部碎片。结果是 GPU 还有空显存，allocator 却说 OOM，batch 上不去。In-flight batching 把短、长请求混在一起，这个问题更狠。

## Block table

把 KV 切成固定 $B$ 个 token 一块（常见 16 或 32）。一块的物理形状大约 $[B, H_{\mathrm{kv}}, d_h]$（再乘层数或每层单独一池）。每条序列一张 block table：逻辑块下标 $i$ 映到物理页号。Attention kernel 不要假设 K/V 在 HBM 上连续，读的时候按 table 做 gather。这就是 PagedAttention：算法仍是 $QK^{\top}V$，索引变成间接的。

新 token 写出：落在当前逻辑块的最后一个空位；块满了，从 free list 拿一页，table 追加一行。请求结束，refcount 减到 0，页回池。调度器按「还剩多少空页」决定能不能 admit 新请求，而不是按「还有没有一条 max_len 的连续槽」。

碎片：

- 内部：只有最后一块平均空 $B/2$ 个 token。$B=16$ 时浪费可忽略；$B=256$ 时短请求开始肉疼。
- 外部：页大小一致，几乎没有。这是分页的本意。
- kernel 效率：$B$ 太小，gather 不规则，Tensor Core tile 不饱；$B$ 太大，内部碎片涨。16–64 是常见折中，要用 Nsight 看注意力 kernel 的 HBM 吞吐，不要拍脑袋。

FlashAttention 在 paged 布局上仍能做，只是 $K/V$ tile 要从非连续页装进 SRAM，实现更烦，IO 分析见 `nvidia-flash-attn`。Decode 依旧是读 KV 的带宽墙。

## Prefix 共享

系统提示、同一份 RAG 前缀、beam 的公共前缀：逻辑上前面若干块的内容相同。物理上可以让多条序列的 table 指向同一组页，refcount 大于 1。新 token 要写、而该页还被别人指着，就 copy-on-write：拷一页再写，避免污染共享前缀。

失效条件：前缀其实不一致（多一个空格、不同 system prompt）、或从中间插入。共享省的是 HBM 容量和第一次 prefill 的写；decode 时各请求的新 KV 仍然分叉，带宽按各自 $T$ 走。不要承诺「共享 prefix 之后 decode 也快一倍」。

和 GQA 叠加：页里 $H_{\mathrm{kv}}$ 已经比较小，分页管的是变长和并发，GQA 管的是每 token 字节，两者正交。head 怎么选见 `google-gqa-mqa`。

## 追问

- **block size 写成 1？** 碎片最小，kernel 退化成完全随机 gather，decode 会更慢。分页是内存管理，不是把 token 当页。
- **和 CUDA 虚拟内存 API 是一回事吗？** 想法同源，这里的「页」是应用层 KV 块，不是 `cuMemMap` 的 GPU 页。TensorRT-LLM 可以在底下再用 CUDA 虚拟内存，面试先把 block table 讲清。
- **抢页失败？** 抢占：暂停最长或优先级最低的请求，把页还回去（swap 到 CPU 或直接 kill）。这是调度策略，不是 attention 公式。
- **多 LoRA 的 KV 能共享 prefix 吗？** 权重不同，同一段 token 的 K/V 一般不同，不能因为字符串相同就共享。Adapter 见 `nvidia-lora-serve`。

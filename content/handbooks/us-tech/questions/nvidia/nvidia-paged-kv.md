---
id: nvidia-paged-kv
section: nvidia
order: 9
level: A
title: NVIDIA：PagedAttention / KV block table，碎片和 prefix 共享
quick: "把 KV cache 切成固定 token 块，用 block table 将每条序列的逻辑块映射到物理块，请求增长时再分配。这样不用按最大长度预留连续显存，内部浪费主要留在最后一个块；相同前缀可以共享物理块，写入共享块前先复制，避免改坏其他请求的缓存。"
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

PagedAttention 用固定大小的 KV 块和一张映射表来管理变长请求。比如请求实际只有 200 个 token，如果按 4096 的上限预留连续空间，会空出很大一段；分页后只为已经使用的块分配显存，增长时再拿新块。下面先算这笔空间，再讲共享前缀时如何避免互相覆盖。

这个算法来自 vLLM。TensorRT-LLM 也提供 paged KV 和 in-flight batching，Triton 可以通过后端接入，见 `nvidia-triton-infer`。

Decode 的 KV 随 $T$ 线性涨：

$$
\mathrm{bytes}\approx 2\cdot L\cdot T\cdot H_{\mathrm{kv}}\cdot d_h\cdot \mathrm{elem\_size}.
$$

朴素实现会在请求到达时按 `max_seq_len` 预留连续缓冲。实际长度 200、槽位 4096，中间那一截永远空着，这是内部浪费。请求走了，留下的空洞又对不齐下一条更长的序列，这是外部碎片。结果是 GPU 还有空显存，allocator 却说 OOM，batch 上不去。In-flight batching 把短、长请求混在一起，这个问题更狠。

## Block table

把 KV 切成固定 $B$ 个 token 一块（常见 16 或 32）。一块的物理形状大约 $[B, H_{\mathrm{kv}}, d_h]$（再乘层数或每层单独一池）。每条序列一张 block table：逻辑块下标 $i$ 映到物理页号。Attention kernel 不要假设 K/V 在 HBM 上连续，读的时候按 table 做 gather。PagedAttention 保持原来的注意力计算，这里用 $QK^{\top}V$ 示意，改变的是读取 K/V 时要经过映射表。

新 token 先写到当前逻辑块下一个空位；块满后从 free list 取一页，在 table 追加映射。请求结束时减少 refcount，减到 0 才把页还回池。调度器就能按空页数量决定是否接收请求，不必找到一整条 max_len 的连续空间。

空间浪费主要剩最后一个块，平均空 $B/2$ 个 token。$B=16$ 时较小，$B=256$ 时短请求的浪费就明显了。所有页同样大，也基本消除了原来长短缓冲留下的外部碎片。

块大小还影响 kernel：$B$ 太小会让 gather 更零散、Tensor Core tile 不饱，太大又增加内部浪费。16-64 是常见折中，最终用 Nsight 测注意力核的 HBM 吞吐来选。

FlashAttention 在 paged 布局上仍能做，只是 $K/V$ tile 要从非连续页装进 SRAM，实现更烦，IO 分析见 `nvidia-flash-attn`。Decode 依旧是读 KV 的带宽墙。

## Prefix 共享

系统提示、同一份 检索增强生成（RAG） 前缀、beam 的公共前缀：逻辑上前面若干块的内容相同。物理上可以让多条序列的 table 指向同一组页，refcount 大于 1。新 token 要写、而该页还被别人指着，就 copy-on-write：拷一页再写，避免污染共享前缀。

前缀多一个空格、换了 system prompt，或从中间插入，原有共享就可能失效。共享省的是 HBM 容量和第一次 输入预填充（prefill，即处理输入并建立缓存） 的写；逐 token 生成（decode） 时各请求的新 KV 仍然分叉，带宽按各自 $T$ 走。不要承诺「共享 prefix 之后 decode 也快一倍」。

和 GQA 叠加：页里 $H_{\mathrm{kv}}$ 已经比较小，分页管的是变长和并发，GQA 管的是每 token 字节，两者正交。head 怎么选见 `google-gqa-mqa`。

## 追问

**block size 写成 1？**
block size 为 1 时碎片最小，但 kernel 会变成完全随机 gather，decode 可能更慢。块大小仍要兼顾访存效率。
**和 CUDA 虚拟内存 API 是一回事吗？**
想法同源，这里的「页」是应用层 KV 块，不是 `cuMemMap` 的 GPU 页。TensorRT-LLM 可以在底下再用 CUDA 虚拟内存，面试先把 block table 讲清。
**抢页失败？**
可以抢占最长或最低优先级请求，暂停后把 KV swap 到 CPU，或终止请求并回收页。这是调度器在分配失败时的处置，注意力公式不用改变。
**多 LoRA 的 KV 能共享 prefix 吗？**
权重不同，同一段 token 的 K/V 一般不同，不能因为字符串相同就共享。Adapter 见 `nvidia-lora-serve`。

## 相关题

- [[sys-paged-attn]]：几乎是同一道题的系统版，块表、CoW、前缀共享都讲到，可以当同题复习。
- [[coding-paged-table]]：白板写 block table 和 append，验收逻辑页到物理块的映射。
- [[kv-prefix-paged-cow]]：把 refcount 共享和写时复制完整写出来，还要求分配失败时回滚。
- [[meta-vllm]]：Meta 问法，把分页和 continuous batching、GQA 放在一起讲。

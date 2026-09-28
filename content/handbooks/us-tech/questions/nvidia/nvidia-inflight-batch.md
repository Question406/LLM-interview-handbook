---
id: nvidia-inflight-batch
section: nvidia
order: 15
level: A
title: NVIDIA：in-flight batching，iteration-level 调度
quick: >-
  静态 batch 等最长那条，短请求的槽位是空洞。In-flight / continuous batching 把调度改到每个 decode
  iteration：结束的立刻腾 KV 页，waiting 里补进新请求，context 和 generation 可以同一步。吞吐来自少空等，不是更大的静态矩阵。没有
  paged KV，变长 append 会把预留打满。
tags:
  - NVIDIA
  - TensorRT-LLM
  - In-flight Batching
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: NVIDIA TensorRT-LLM Supercharges Large Language Model Inference on NVIDIA H100 GPUs
    url: https://developer.nvidia.com/blog/nvidia-tensorrt-llm-supercharges-large-language-model-inference-on-nvidia-h100-gpus/
    type: secondary
  - title: Paged Attention, IFB, and Request Scheduling — TensorRT-LLM
    url: https://nvidia.github.io/TensorRT-LLM/latest/features/paged-attention-ifb-scheduler.html
    type: primary
  - title: Orca — A Distributed Serving System for Transformer-Based Generative Models
    url: https://www.usenix.org/conference/osdi22/presentation/yu
    type: primary
  - title: Efficient Memory Management for Large Language Model Serving with PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
---

## 题怎么来的

NVIDIA 把这套叫 in-flight batching（IFB），vLLM / TGI 叫 continuous batching，论文原点是 Orca 的 iteration-level 调度。TensorRT-LLM 岗位常从「为什么静态 batch 吃不满 H100」进到这一题。我会先画一步 decode 的时间线，再补一句：没有 paged KV，inflight 只是把碎片从时间挪到显存。引擎定位见 `nvidia-trt-llm`。

## 静态 batch 的空洞

$B$ 条请求一起 generate，长度可以差一个数量级。请求级调度：凑齐、pad 到这个 batch 的 $\max T$，一起步进，直到最慢那条 EOS。三条税：

1. **Padding。** 长度 20 和 200 坐一桌，短的每步都在算废行。
2. **队头阻塞。** 先结束的行仍占计算槽和按 `max_seq_len` 预留的 KV，等到整桌散场。
3. **Prefill 霸占。** 一条 8k prompt 进来，整个静态 batch 要么等它算完，要么根本不和 decode 混。

GPU 看起来在做 $[B, D]\times[D, D]$，有的行已经 mask 掉。LLM 生成长度方差远大于分类模型，这个税更重。Triton 那种等几毫秒拼 `preferred_batch_size` 的动态 batch，解决的是「形状相同的一次 launch」，不是「每步换人」，见 `nvidia-triton-infer`。

## Iteration-level 在换什么

把「一条请求」拆成一串 iteration。每步 scheduler 看当前还活着的序列：

1. 刚 EOS 的，立刻从 batch 拿掉，KV 页 refcount 减到 0 回池。
2. waiting 里能 admit 的新请求（显存还够、`max_batch_size` / `max_num_tokens` 没打满）插进来。新来的先走 context，老的走 generation。
3. 组一次 ragged batch：packed token，不再为对齐 pad 到全局 max。Attention plugin 用 block table 做 gather，见 `nvidia-paged-kv`。

吞吐涨的原因是 SM 和 HBM 对着「这一步还活着的 token」，不是矩阵变大了。静态 $B=32$ 里可能只有 8 条真在写；inflight 的瞬时 $B$ 一直贴着 KV 水位。NVIDIA 博客写过真实流量上 IFB 加 kernel 优化，H100 吞吐可以翻倍量级；面试用数量级，不要背具体倍数。

Context 和 generation 同一步：prefill 是算力墙，decode 是带宽墙。混在一起能填 decode 的计算空洞，但一条超长 context 仍可能把这一步的墙钟拉长，TPOT 出尖刺。这就是 chunked prefill 要切 prompt 的原因，见 `nvidia-chunked-prefill`。IFB 解决「人进出」；chunking 解决「一次 context 太大」。

## 调度器和显存是一对

Admit 看的是空页，不是「还有没有一条 max_len 的连续槽」。`max_num_tokens` 限制每步算多少 token（context 块 + decode 各 1）。`max_batch_size` 限制同时在飞的请求数。两个一起才构成水位。只开 IFB、KV 仍按 max length 预留，空洞从时间变成显存，batch 照样上不去。

CUDA Graph 喜欢固定 $B$，IFB 每步 $B$ 在变：要么 pad 到下一个已捕获的 batch size，要么这步不走 graph。这是和 `nvidia-cuda-graph` 的接缝，不是二选一。

## 追问

- **和动态 padding 是一回事吗？** 不是。Padding 还是请求级；IFB 是每步改成员。Ragged + paged 才把洞填实。
- **完成的请求 KV 能留着做 prefix？** 可以 refcount 共享，写下一段再 copy-on-write。这是分页功能，调度只决定谁在飞。
- **max_num_tokens 开极大？** 一步塞进超长 prefill，decode 的 TPOT 尖刺回来。水位是 SLA 旋钮，不是越大越好。
- **多 LoRA 同服务？** IFB 的 batch 里可能混多种 adapter，底座 GEMM 仍一次，瘦 GEMM 要 grouped。别为每个 LoRA 复制一份引擎，见 `nvidia-lora-serve`。

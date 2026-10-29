---
id: nvidia-inflight-batch
section: nvidia
order: 15
level: A
title: NVIDIA：in-flight batching，iteration-level 调度
quick: "In-flight batching 每个 decode iteration 都重新安排请求：结束的释放 KV 页，新请求有资源就补进来。静态 batch 要等最长请求结束，短请求留下的计算和显存空位就浪费了；IFB 要配合分页 KV 才能把这些资源利用起来。"
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

In-flight batching（IFB）按生成的每一步重新安排 batch 成员，已经完成的请求马上退出，有资源的新请求马上进入。NVIDIA 使用 IFB 这个名字，vLLM / TGI 称为 continuous batching，论文起点是 Orca 的 iteration-level 调度。它还要配合 paged KV，否则计算空位补上了，显存预留造成的浪费仍会限制 batch。引擎定位见 `nvidia-trt-llm`。

## 为什么要在每一步换请求

$B$ 条请求一起 generate，长度可能相差一个数量级。请求级调度先凑齐请求，pad 到 batch 的 $\max T$，再一起步进到最慢那条 EOS，因此会留下这些开销：

1. **Padding。** 长度 20 和 200 坐一桌，短的每步都在算废行。
2. **队头阻塞。** 先结束的行仍占计算槽和按 `max_seq_len` 预留的 KV，等到整桌散场。
3. **Prefill 霸占。** 一条 8k prompt 进来，整个静态 batch 要么等它算完，要么根本不和 decode 混。

GPU 看起来在做 $[B, D]\times[D, D]$，有的行已经 mask 掉。LLM 生成长度方差远大于分类模型，这类开销更明显。Triton 那种等几毫秒拼 `preferred_batch_size` 的动态 batch，解决的是「形状相同的一次 launch」，不是「每步换人」，见 `nvidia-triton-infer`。

实际调度时，把一条请求拆成连续的 iteration 来处理。

每步 scheduler 都检查还在生成的序列：

1. 刚 EOS 的，立刻从 batch 拿掉，KV 页 refcount 减到 0 回池。
2. waiting 里能 admit 的新请求（显存还够、`max_batch_size` / `max_num_tokens` 没打满）插进来。新来的先走 context，老的走 generation。
3. 组一次 ragged batch：packed token，不再为对齐 pad 到全局 max。Attention plugin 用 block table 做 gather，见 `nvidia-paged-kv`。

throughput 提高，是因为 SM 和 HBM 主要处理这一步仍然有效的 token。静态 $B=32$ 里可能只有 8 条真在写；inflight 的瞬时 $B$ 一直贴着 KV 水位。NVIDIA 博客写过真实流量上 IFB 加 kernel 优化，H100 throughput 可以翻倍量级；面试用数量级，不要背具体倍数。

Context 和 generation 同一步：输入 prefill 是算力墙，decode 是带宽墙。混在一起能填 decode 的计算空洞，但一条超长 context 仍可能把这一步的实际耗时拉长，每个 token 的生成间隔突然变长。这就是 chunked prefill 要切 prompt 的原因，见 `nvidia-chunked-prefill`。IFB 解决「人进出」；chunking 解决「一次 context 太大」。

## 调度预算怎么和显存配合

Admit 看的是空页，不是「还有没有一条 max_len 的连续槽」。`max_num_tokens` 限制每步算多少 token（context 块 + decode 各 1）。`max_batch_size` 限制同时在飞的请求数。两个一起才构成水位。只开 IFB、KV 仍按 max length 预留，空洞从时间变成显存，batch 照样上不去。

CUDA Graph 喜欢固定 $B$，IFB 每步 $B$ 在变：要么 pad 到下一个已捕获的 batch size，要么这步不走 graph。这是和 `nvidia-cuda-graph` 的接缝，不是二选一。

## 追问

- **和动态 padding 是一回事吗？** 不是。Padding 还是请求级；IFB 是每步改成员。Ragged + paged 才把洞填实。
- **完成的请求 KV 能留着做 prefix？** 可以 refcount 共享，写下一段再 copy-on-write。这是分页功能，调度只决定谁在飞。
- **max_num_tokens 开极大？** 一步塞进超长 prefill，decode 的 TPOT 尖刺回来。水位是 SLA 旋钮，不是越大越好。
- **多 LoRA 同服务？** IFB 的 batch 里可能混多种 adapter，底座 GEMM 仍一次，瘦 GEMM 要 grouped。别为每个 LoRA 复制一份引擎，见 `nvidia-lora-serve`。

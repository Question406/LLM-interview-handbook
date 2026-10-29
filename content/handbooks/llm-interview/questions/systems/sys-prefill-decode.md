---
id: sys-prefill-decode
section: systems
order: 7
level: S
title: Prefill 为什么更 Compute-Bound，Decode 为什么更 Memory-Bound？
quick: >-
  假设用户输入一篇长文档，再让模型逐 token 回答。处理输入时，很多 tokens 可以一起参与矩阵计算；生成时，每一步通常只推进少量新
  tokens，却仍需读取大量权重和历史 KV。
tags:
  - Serving
  - Inference
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: '2026-10-28'
sources:
  - title: >-
      DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large
      Language Model Serving
    url: 'https://arxiv.org/abs/2401.09670'
    type: primary
---

## 回答思路

> **问题与场景：** 假设用户输入一篇长文档，再让模型逐 token 回答。
>
> **做法与原因：** 因此 prefill 与 decode 往往受不同瓶颈影响：前者更容易充分利用计算，后者更容易受 memory access 限制。
>
> **检查与取舍：** 优化时我会分别看首个 token 等待时间和后续 token 的间隔。

## 可以这样回答

假设用户输入一篇长文档，再让模型逐 token 回答。处理输入时，很多 tokens 可以一起参与矩阵计算；生成时，每一步通常只推进少量新 tokens，却仍需读取大量权重和历史 KV。

因此 prefill 与 decode 往往受不同瓶颈影响：前者更容易充分利用计算，后者更容易受 memory access 限制。这是常见情况，需要结合 batch size、模型与硬件测量。

优化时我会分别看首个 token 等待时间和后续 token 的间隔。不能只提高总 throughput，就默认用户看到的两段 latency 都改善了。

## 技术备查

Prefill 能把同一份权重用于整段输入，计算量相对读取量更大，所以通常受算力限制。Decode 每条序列每步只生成一个 token，却仍要读取权重和历史 KV，所以通常受带宽限制。用 Roofline 分析时，比较的是算术强度，也就是 FLOPs / 字节。下面把两种阶段的矩阵形状写出来，就能看到差别。

## 从矩阵形状看读取成本

线性层权重大约 $[d,d]$，读一次权重的字节量与 $d^2$ 成正比。

- **Prefill：** 输入是整段 prompt，形如 $[T,d]\times[d,d]$（或 batched $[B T,d]$）。$T$ 常是成百上千。一次读权重，对 $T$ 个 token 做乘加，强度随 $T$ 涨，容易把 Tensor Core 喂饱，受算力限制。
- **Decode：** 每条序列每步只追加 $1$ 个 token，形如 $[B,d]\times[d,d]$。$B$ 往往远小于 $T_{\mathrm{prompt}}$。每步仍要把**整份权重**从 HBM 读进计算单元，再读历史 K/V 做 attention。FLOPs 按 $d^2$ 量级，流量却几乎是整模型加整段 KV，强度接近 $O(1)$，落在带宽墙。

Attention 同理。Prefill 的 $QK^\top$ 是 $[T,d]\times[d,T]$，有 $T^2$ 项可算；逐 token 生成（decode） 只有新 query 对历史 $T$ 行 K/V，计算薄、读 KV 厚。上下文越长，decode 的 KV 流量线性涨，权重流量不变，更偏 memory-bound。

设 $d=4096$，权重一份约 $2d^2$ FLOPs（乘加），读 BF16 权重约 $2d^2$ 字节。Prefill $T=2048$ 时，线性层强度大约再乘 $T$，远高于 GPU 的「算力/带宽」拐点；decode $B=8$ 时强度只有个位数到几十，典型 GPU 拐点在几百，于是停在 HBM。

这条判断主要适用于长上下文、中小 batch 的 serving。极大 `batch`、极短 context 或极低 bit 的权重量化，都可能让 decode 转而被算力或调度卡住。

同一 GPU 上混跑时，一条 $T=8\mathrm{k}$ 的 输入 prefill 会占满 SM 几十毫秒到数百毫秒，正在进行的 decode batch 被打断，TPOT 出现尖刺。这里的原因是 prefill 占用了计算资源，打断了 decode 原本连续的带宽流水。

## 调度时怎样利用这个差别

- **Continuous batching：** decode 步之间插入已结束序列的空位，提高 $B$，抬 GEMM 效率。
- **Chunked prefill：** 把超长 prompt 切块，避免一条 prefill 独占、饿死 decode。
- **KV 压缩 / 量化 / paging：** 专打 decode 的 KV 流量与碎片。
- **Prefill/decode 分离（DistServe）：** 两类算子的有效 throughput（goodput）曲线不同。混部时，算力型 prefill 会打断带宽型 decode 的流水，首个 token 的等待时间（TTFT） 与 TPOT 互相伤害。拆到不同池，才能各自扩容：prefill 池堆算力，decode 池堆带宽与 KV 容量。

## 追问

**Batch 增大会让 decode 不再 memory-bound 吗？**
算术强度随 $B$ 提高，可能滑向 compute-friendly；但权重每步仍要读一遍，长 KV 流量也在。最终取决于模型、$T$、$B$ 和芯片的算力/带宽比，不是「batch 大了就一定算力瓶颈」。
**TTFT 和 TPOT 分别受什么影响？**
TTFT（首 token）主要是排队加 prefill；TPOT（后续 token）主要是 decode 调度、有效 batch、权重与 KV 带宽。分离部署后两套指标才比较好独立调。
**Chunked prefill 为什么能改善尾延迟？**
大 prefill 不再一次占满 SM，decode 可以按步插入，P99 TPOT 不会被单条长 prompt 打穿。

---
id: sys-prefill-decode
section: systems
order: 7
level: S
title: Prefill 为什么更 Compute-Bound，Decode 为什么更 Memory-Bound？
quick: >-
  Prefill 一次处理很多 tokens，GEMM 大、算术强度高。Decode 每 step 每 sequence 只新增 1 个
  token，却要读大量模型权重和历史 KV，矩阵瘦、算术强度低，所以常被显存带宽卡住。
tags:
  - Serving
  - Inference
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: 'DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving'
    url: https://arxiv.org/abs/2401.09670
    type: primary
---

这块容易背一句「prefill 算力、decode 带宽」却画不出矩阵形状。Roofline 看的是**算术强度**（FLOPs / 字节），不是「有没有 attention」。同一套权重，prompt 阶段和生成阶段落在曲线两边。

## 1. 把 GEMM 形状写出来

线性层权重大约 $[d,d]$，读一次权重的字节量与 $d^2$ 成正比。

- **Prefill：** 输入是整段 prompt，形如 $[T,d]\times[d,d]$（或 batched $[B T,d]$）。$T$ 常是成百上千。一次读权重，对 $T$ 个 token 做乘加，强度随 $T$ 涨，容易把 Tensor Core 喂饱，受算力限制。
- **Decode：** 每条序列每步只追加 $1$ 个 token，形如 $[B,d]\times[d,d]$。$B$ 往往远小于 $T_{\mathrm{prompt}}$。每步仍要把**整份权重**从 HBM 读进计算单元，再读历史 K/V 做 attention。FLOPs 按 $d^2$ 量级，流量却几乎是整模型加整段 KV，强度接近 $O(1)$，落在带宽墙。

Attention 同理。Prefill 的 $QK^\top$ 是 $[T,d]\times[d,T]$，有 $T^2$ 项可算；decode 只有新 query 对历史 $T$ 行 K/V，计算薄、读 KV 厚。上下文越长，decode 的 KV 流量线性涨，权重流量不变，**更 memory-bound**。

## 2. 一个数量级对照

设 $d=4096$，权重一份约 $2d^2$ FLOPs（乘加），读 BF16 权重约 $2d^2$ 字节。Prefill $T=2048$ 时，线性层强度大约再乘 $T$，远高于 GPU 的「算力/带宽」拐点；decode $B=8$ 时强度只有个位数到几十，典型 GPU 拐点在几百，于是停在 HBM。

这不是绝对定理：极大 `batch`、极短 context、权重量化到极低 bit，decode 也可能被算力或调度卡住。我会说**默认长上下文、中小 batch 的 serving** 才是这条判断。

同一 GPU 上混跑时，一条 $T=8\mathrm{k}$ 的 prefill 会占满 SM 几十毫秒到数百毫秒，正在进行的 decode batch 被打断，TPOT 出现尖刺。这就是「算力型作业饿死带宽型作业」：不是 decode 突然变 compute-bound，而是调度把带宽流水拆碎了。

## 3. 为什么引出一堆 serving 技术

- **Continuous batching：** decode 步之间插入已结束序列的空位，提高 $B$，抬 GEMM 效率。
- **Chunked prefill：** 把超长 prompt 切块，避免一条 prefill 独占、饿死 decode。
- **KV 压缩 / 量化 / paging：** 专打 decode 的 KV 流量与碎片。
- **Prefill/decode 分离（DistServe）：** 两类算子的有效吞吐（goodput）曲线不同。混部时，算力型 prefill 会打断带宽型 decode 的流水，TTFT 与 TPOT 互相伤害。拆到不同池，才能各自扩容：prefill 池堆算力，decode 池堆带宽与 KV 容量。

## 追问

- **Batch 增大会让 decode 不再 memory-bound 吗？** 算术强度随 $B$ 提高，可能滑向 compute-friendly；但权重每步仍要读一遍，长 KV 流量也在。最终取决于模型、$T$、$B$ 和芯片的算力/带宽比，不是「batch 大了就一定算力瓶颈」。
- **TTFT 和 TPOT 分别受什么影响？** TTFT（首 token）主要是排队加 prefill；TPOT（后续 token）主要是 decode 调度、有效 batch、权重与 KV 带宽。分离部署后两套指标才比较好独立调。
- **Chunked prefill 为什么能改善尾延迟？** 大 prefill 不再一次占满 SM，decode 可以按步插入，P99 TPOT 不会被单条长 prompt 打穿。

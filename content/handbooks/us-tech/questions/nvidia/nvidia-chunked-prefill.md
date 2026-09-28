---
id: nvidia-chunked-prefill
section: nvidia
order: 20
level: A
title: NVIDIA：chunked prefill 把长 prompt 切开和 decode 混部
quick: >-
  一条 8k prompt 整段 prefill 会把正在飞的 decode 卡住，TPOT 出尖刺。Chunked prefill 按 token
  budget 把 prompt 切成块，每步一块 context 加上这一步的 decode。算力墙和带宽墙在同一步里互相填。TensorRT-LLM
  叫 chunked context，块大小要对齐 KV page。这不是把 prefill 和 decode 拆到两台机器。
tags:
  - NVIDIA
  - Chunked Prefill
  - TensorRT-LLM
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: SARATHI — Efficient LLM Inference by Piggybacking Decodes with Chunked Prefills
    url: https://arxiv.org/abs/2308.16369
    type: primary
  - title: Taming Throughput-Latency Tradeoff in LLM Inference with Sarathi-Serve
    url: https://arxiv.org/abs/2403.02310
    type: primary
  - title: Long Sequences — TensorRT-LLM
    url: https://nvidia.github.io/TensorRT-LLM/latest/features/long-sequence.html
    type: primary
  - title: Paged Attention, IFB, and Request Scheduling — TensorRT-LLM
    url: https://nvidia.github.io/TensorRT-LLM/latest/features/paged-attention-ifb-scheduler.html
    type: primary
---

## 题怎么来的

In-flight 解决「人进出」，见 `nvidia-inflight-batch`。长 prompt 进来之后，一步里的 token 数仍可能被单条 context 打满。vLLM 叫 chunked prefill，TensorRT-LLM 叫 chunked context。论文是 Sarathi / Sarathi-Serve 的 stall-free batching。NVIDIA 岗要听 token budget 和 KV page 对齐，不要只说「把 prompt 切开」。

## 整段 prefill 为什么卡住 decode

Prefill：一条序列的 $Q,K,V$ 都是 $[T_{\mathrm{in}}, D]$，GEMM / FMHA 算术强度随 $T$ 涨，算力墙，墙钟可以到几十到几百毫秒。Decode：每条 $Q$ 长度 1，反复读权重和历史 KV，带宽墙，一步往往一两毫秒量级，见 `nvidia-flash-attn`。

IFB 若仍「新请求的整段 context 必须在一步里做完」，那一步的墙钟跟最长 prompt 走。正在飞的 decode 全部停等，TPOT / TBT 出现尖刺。更糟：`max_num_tokens` 必须不小于最长 prompt，这个预算从 KV 池里抢 HBM，并发反而下降。短请求的 TTFT 也可能被排队抬起来。不是模型慢，是队头一条长 context。

## 切块以后一步里有什么

设每步 token 预算 $U$（TRT-LLM 的 `max_num_tokens`）。Scheduler 典型顺序（Sarathi-Serve）：

1. 先把正在 decode 的请求各放 1 个 token 进这一批（保 TPOT）。
2. 若有半截 prefill，继续啃它的下一块，块长不超过 $U - B_{\mathrm{decode}}$。
3. 还有空位再 admit 新请求，新 prompt 同样只吃一块。

Attention：这一块的 $Q$ 只覆盖新 token，形状大约 $[B_{\mathrm{mix}}, T_{\mathrm{chunk}}, \ldots]$；$K,V$ 是前缀 cache 加上当前块。因果仍成立，因为前缀已经在 paged KV 里。除最后一块外，TRT-LLM 要求 chunk 长度是 KV block size（常见 64）的整数倍，否则对不齐 page，见 `nvidia-paged-kv`。

混部的 roofline：decode 行提供 HBM 流量和瘦 GEMM；chunk 提供能喂满 Tensor Core 的 $T_{\mathrm{chunk}}$。同一步里两堵墙都有东西吃，GPU 利用率比纯 decode 高，又不会像整段 8k prefill 那样把步长拉到几百毫秒。$U$ 太大：步长又被 chunk 主导，stall 回来。$U$ 太小：prefill 切太碎，TTFT 变差、kernel 变短、CUDA Graph 更难套，见 `nvidia-cuda-graph`。

显存：每步工作集跟 $U$ 走，不再跟「本服务支持的最大 prompt」走。于是 `max_num_tokens` 可以远小于 128k，省下的 HBM 给 KV，inflight 并发上去。这是官方 long-sequence 文档强调的第二点。

代价：幸运的那条短 prompt 本来一步就能出首 token，现在可能被切、被 decode 同行稀释，平均 TTFT 往往更好，某几条「本来能秒出」的 TTFT 可能变差。NVIDIA 文档把这句写进了推荐理由：生产看排队和最坏 TTFT，不看幸运样本。

## 不是分离部署

Chunked prefill 仍在同一张 GPU、同一个 iteration 里混 context 和 generation。Prefill / decode 分池是把两阶段拆到两套机器，KV 要跨机搬。混部切块是调度；分池是拓扑。面试问「长 prompt 怎么办」先答 chunk；问「prefill 机器和 decode 机器」再答搬 KV。引擎怎么挂进 Triton 见 `nvidia-trt-llm`、`nvidia-triton-infer`。

## 追问

- **chunk 写成 1 行不行？** 等于把 prefill 退化成逐步 decode，算术强度塌掉，TTFT 极差。chunk 要大到 GEMM 饱和，又小到步长满足 TBT SLO。
- **和 CUDA Graph？** 混合步的 token 数在变，整图难捕获；常 decode-only 走 graph，带 chunk 的步 eager 或 piecewise。
- **必须 paged KV 吗？** 实际要。切块 + inflight 让每条序列的 KV 间断增长，连续预留又回到碎片。
- **只服务长文档、没有交互 decode？** 切块仍能降低峰值工作集；混部收益小。那时更该把 $U$ 开大，或直接上分离 prefill 池。

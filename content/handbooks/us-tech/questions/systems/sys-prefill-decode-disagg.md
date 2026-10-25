---
id: sys-prefill-decode-disagg
section: systems
order: 8
level: S
title: 系统：prefill/decode 分离部署，KV 搬运成本
quick: "Prefill 主要吃算力，decode 主要吃带宽和 KV 容量，拆成两个池能分别扩容、减少长输入打断生成。代价是传输和重新分片 KV，要先用 KV 字节数与链路带宽估算开销；短输入或卡少时，单池加 chunked prefill 往往更合适。"
tags:
  - Serving
  - NVIDIA
  - DistServe
  - vLLM
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: "DistServe: Disaggregating Prefill and Decoding for Goodput-optimized LLM Serving"
    url: https://arxiv.org/abs/2401.09670
    type: primary
  - title: "Splitwise: Efficient Generative LLM Inference Using Phase Splitting"
    url: https://arxiv.org/abs/2311.18677
    type: primary
  - title: Mastering LLM Techniques — Inference Optimization
    url: https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization/
    type: secondary
  - title: Disaggregated Serving — TensorRT-LLM
    url: https://nvidia.github.io/TensorRT-LLM/latest/features/disagg-serving.html
    type: secondary
---

Prefill / decode 分离是为了让两阶段分别使用适合的资源，同时避免长输入打断正在生成的请求。是否值得拆，要看隔离带来的收益能否盖过 KV 传输和两套调度的成本。

Prefill 一次处理完整 prompt，矩阵形状为 $[T,d]\times[d,d]$，$T$ 越长算术强度越高，容易用满 Tensor Core。Decode 每条序列每步只新增一个 token，却要读完整权重和历史 KV，更受 HBM 带宽与 KV 容量限制。例如一条 $T=8\mathrm{k}$ 的 prefill 占满 SM 几十到几百毫秒，会使同卡 decode batch 暂停，token 间隔突然变长。这是调度干扰，decode 的工作本身没有因此变成 compute-bound。

拆开后，prefill 池可以用更高 TP 和大 GEMM，不必给 KV 留大半 HBM；decode 池可以用较低 TP、较高 `mem_fraction`，配 continuous batching 提高有效 $B$。两池分别扩容，才能分别调 TTFT 和 TPOT。DistServe 关注的是满足 SLO 的 goodput，Splitwise、TensorRT-LLM / Dynamo 的分离服务也在处理这类资源差异。相关算术强度问题见 `openai-prefill-decode`。

短请求、短 prompt 或卡很少时，两阶段差异不明显，传 KV 和额外调度反而可能增加耗时。可以先用 chunked prefill，把长输入分块，在块间插入 decode，避免跨机传 KV。长上下文、两阶段流量比例变化大，或想使用不同并行度时，再考虑分离。

## 先算 KV 传输量

单请求 KV 大约占：

$$
2 \cdot L \cdot n_{\mathrm{kv}} \cdot d_h \cdot T \cdot b
$$

K 和 V 各一份，$b$ 是每个元素的字节数。GQA 减少 $n_{\mathrm{kv}}$，KV 量化可把 $b$ 从 2 降到 1 或更低，见 `sys-kv-quant`。Llama-70B 量级、8k 上下文时，单请求 KV 可能是 GB 级；NVLink 传得快，跨节点 RDMA 的传输时间却可能接近重新 prefill，抵消调度收益。

传输还受布局和失败恢复影响。同步等全部 KV 到齐会增加 TTFT；流水传输、边传边 decode 前几层可以减少等待，但实现复杂。Prefill TP$=8$、decode TP$=4$ 时要 reshard KV，不能直接 memcpy。Prefix cache 在 prefill 池命中后，decode 池仍需拿到 KV，可以传输，也可以保留一份前缀页，用显存换网络。Prefill 成功而传输失败时，还得明确重传或重算，以及如何计入 SLO。

选 NCCL/NVSHMEM、GPU Direct RDMA 或先压成 FP8 传输前，先写出这笔体积和时间账。

## 追问

**短 prompt 高并发要拆吗？**
通常先不拆。Decode 主导时搬运只增加开销，先用 chunked prefill 和 continuous batching。

**GQA / MQA 为什么有帮助？**
KV 头数减少，搬运体积随之线性下降，分离更容易划算。

**TTFT 一定改善吗？**
不一定。Prefill 池拥堵再加搬运，TTFT 可能更差，要一起看队列。

**分离后还需要 continuous batching 吗？**
需要。分离决定池间部署，池内仍要 iteration-level 调度，见 `sys-cont-batch`。

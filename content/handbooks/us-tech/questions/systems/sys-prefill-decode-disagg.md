---
id: sys-prefill-decode-disagg
section: systems
order: 8
level: S
title: 系统：prefill/decode 分离部署，KV 搬运成本
quick: >-
  Prefill 吃算力、decode 吃带宽和 KV 容量，混部时一条长 prompt 会打断 decode 流水。拆到两个池才能各自扩容。
  代价是把 KV 从 prefill 池搬到 decode 池：体积跟层数、KV 头、序列长度、字节宽成正比，网络不够时搬一次接近再算一遍。
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

## 题怎么来的

DistServe、Microsoft Splitwise、NVIDIA TensorRT-LLM / Dynamo 的分离服务，都在答同一件事：prefill 和 decode 的 roofline 不同，混在一张卡上会互相伤害。OpenAI 风格问 TTFT 和 TPOT 为什么不能一起调（见 `openai-prefill-decode`）；NVIDIA 问 KV 怎么搬、搬得过算吗。算术强度对比可以先说「prefill 大 GEMM、decode 反复读权重和 KV」，本题落到部署和搬运成本。

## 为什么要拆

Prefill 一次吃整段 prompt，$[T,d]\times[d,d]$，算术强度随 $T$ 涨，容易喂饱 Tensor Core，受算力限制。Decode 每步每条序列只多一个 token，却要读整份权重和历史 KV，强度低，受 HBM 带宽和 KV 容量限制。同一 GPU 上混跑：一条 $T=8\mathrm{k}$ 的 prefill 占满 SM 几十到几百毫秒，正在飞的 decode batch 被打断，TPOT 出尖刺。这不是 decode 突然变 compute-bound，是调度把带宽流水拆碎了。

拆开之后：

- Prefill 池堆算力（可以更高 TP、更大 GEMM、不必为 KV 留出大半 HBM）。
- Decode 池堆带宽和 KV 容量（更低 TP、更高 `mem_fraction` 给 cache、continuous batching 吃满有效 $B$）。
- TTFT 和 TPOT 才能独立扩容。DistServe 优化的是 goodput（SLO 内的有效吞吐），不是瞬时 tokens/s。

短请求、prompt 很短、卡很少时别拆：多一次 KV 传输和两套调度，角色不对称不明显，墙钟往往更差。单池折中是 chunked prefill：长 prompt 切块，块之间插入 decode，不传跨机 KV。长上下文、流量里 prefill 和 decode 比例漂移大、两阶段想用不同并行度时，再上分离。

## KV 搬运要算字节

一份 KV 大约：

$$
2 \cdot L \cdot n_{\mathrm{kv}} \cdot d_h \cdot T \cdot b
$$

K 和 V 各一份，$b$ 是每元素字节。GQA 让 $n_{\mathrm{kv}}$ 小于查询头，搬运已经比 MHA 轻一截；再叠 KV 量化（见 `sys-kv-quant`）把 $b$ 从 2 打到 1 或更低。Llama-70B 量级、8k 上下文，单请求 KV 可以到 GB 级。走 NVLink 还好；走跨节点 RDMA，有时搬运墙钟已经接近这段 prefill 本身。那时「分离」赚的调度，会被网络吐回去。

工程上还会踩：

- **同步 vs 异步传输：** 等 KV 到齐再开始 decode，TTFT 含搬迁；流水起来可以边传边 decode 前几层，但实现复杂。
- **并行度不一致：** Prefill 用 TP$=8$，decode 用 TP$=4$，KV 布局要 reshard，不是 memcpy。
- **Prefix cache：** 命中发生在 prefill 池；decode 池仍要这份 KV，要么传、要么 decode 侧也留一份前缀页，显存和网络是交换。
- **失败语义：** Prefill 成功、传输失败，请求要重算还是重传，超时怎么算进 SLO。

NVIDIA 岗可能问 NCCL/NVSHMEM 搬 KV 还是走 GPU Direct RDMA、要不要压成 FP8 再传。先写体积公式，再选链路，不先报产品名。

## 追问

- **短 prompt 高并发要不要拆？** 通常不要。Prefill 很短，decode 主导，搬运是纯税。先 chunked prefill 和 continuous batching。
- **GQA / MQA 对搬运意味着什么？** KV 头变少，体积线性下降，分离更划算。这也是长上下文 serving 爱 GQA 的原因之一。
- **TTFT 拆完一定更好吗？** Prefill 池不排队时更好；若 prefill 池更挤，再加上搬 KV，TTFT 可能更差。要看队列，不要假设拓扑一定赢。
- **和 continuous batching 冲突吗？** 不冲突。分离是池之间；池内仍要 iteration-level 调度，见 `sys-cont-batch`。

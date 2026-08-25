---
id: nvidia-megatron-cp
section: nvidia
order: 18
level: S
title: NVIDIA：Megatron context parallel，环上传 KV
quick: >-
  Megatron CP 每卡只常驻一段 $T/\mathrm{CP}$ 的激活和 KV。注意力时 Q 不动，K/V 沿 CP 组环状
  P2P；概念上的 all-gather / reduce-scatter 被收成点对点。因果 mask 让靠后的 rank 活多，Megatron 用
  zigzag（一头一尾两块）把负载拉平，并直接调 FlashAttention / cuDNN 核。
tags:
  - NVIDIA
  - Megatron
  - Context Parallel
  - Ring Attention
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Ring Attention with Blockwise Transformers for Near-Infinite Context
    url: https://arxiv.org/abs/2310.01889
    type: primary
  - title: Context Parallelism — Megatron-LM User Guide
    url: https://github.com/NVIDIA/Megatron-LM/blob/main/docs/user-guide/features/context_parallel.md
    type: primary
  - title: Context Parallelism — NVIDIA NeMo Framework User Guide
    url: https://docs.nvidia.com/nemo-framework/user-guide/25.11/longcontext/contextparallel.html
    type: secondary
  - title: Reducing Activation Recomputation in Large Transformer Models
    url: https://arxiv.org/abs/2205.05198
    type: primary
---

## 题怎么来的

`nvidia-context-parallel` 把 CP 和 TP / SP 的通信对象分开了。NVIDIA 训练岗会往下挖：Megatron-Core / NeMo 到底怎么传 KV、因果 mask 为什么会偏负载。论文对照是 Ring Attention；Megatron 的差是 (1) 复用现成 FlashAttention / cuDNN 核，(2) 去掉下三角上的废算并做负载均衡。`--context-parallel-size`、P2P 通信类型是开关，不是答案。

## 环上搬什么

CP 组大小 $N$。序列切成块，每卡前向只存自己那一段的 KV，激活也按 $T$ 分片，所以 Linear / LN 不用改。注意力：本地 $Q_i$ 必须见到全部 $K,V$。朴素 all-gather 会让每卡瞬时再持有一份完整 KV，把省下的激活吐回去。Megatron 把这次 all-gather（反向对应 reduce-scatter）收成环：

1. 用当前手里的 KV 块和本地 $Q$ 做一块 FlashAttention，在线 softmax 累加输出。
2. 非阻塞把当前 KV 发给下一个 rank，同时收上一个 rank 的 KV。
3. 转 $N-1$ 圈，每卡的 $Q$ 都见过全序列。反向再聚集一次 KV 来算梯度。

通信发生在「一张卡和它在其他 TP 组里的对端」之间。文档例子：$T=8\mathrm{k}$，每卡 4k；GPU0 与 GPU2 组成 CP 组互换 KV，GPU1 与 GPU3 另一组——因为 TP=2 时相邻卡先组成 TP，CP 跨过去。总卡数 $\mathrm{TP}\times\mathrm{CP}\times\mathrm{PP}\times\mathrm{DP}$。KV 体积跟 $H_{\mathrm{kv}}$ 走，GQA / MQA 直接减通信量，见 `google-gqa-mqa`。

Overlap：第 $k$ 块的 FA 和下一跳 P2P 叠。块太小，核启动和延迟吃掉重叠；块太大，单卡又放不下。这是 CP 的 MFU 旋钮，不是 TP 那两次 all-reduce 的旋钮，见 `nvidia-tensor-parallel`、`nvidia-nccl-allreduce`。

## 因果 mask 和 zigzag

Decoder 下三角：排在序列前面的 $Q$ 有效 KV 短，排在后面的 $Q$ 有效 KV 长。若按连续段切，rank 0 几乎全是 mask，rank $N-1$ 几乎满算，环上最慢的那张卡决定一步时间。

Megatron 的修法：把序列切成 $2N$ 块，每张卡拿一块靠前 + 一块靠后（zigzag / 头尾配对）。每卡看到的 mask 比例接近，负载拉平。代价是本地 $Q$ 不再是一段连续 $T$，mask 逻辑要知道「哪一块 Q 对哪一块远程 KV 合法」；有的子块直接跳过。面试说「开了环就负载均匀」是错的——均匀来自切块方式，不是来自 P2P。

和 Ring Attention 原论文的差别：Megatron 强调用现成 FA 核，而不是自己写一套 blockwise 注意力；并且明确要砍掉因果下的废 FLOPs。数值上仍是精确注意力，在线 softmax 把各 KV 块的统计合起来，和 FlashAttention 的 tile 是同一件事，见 `nvidia-flash-attn`。

正向每卡只留本地 KV 块，反向再 gather：用通信换激活。这和 checkpoint 正交；长上下文两者常一起开。万亿 3D 并行里 CP 是第四维，见 `nvidia-trillion-train`。

## 和 SP、推理切块不要并句

SP 仍只切 LN / Dropout，GEMM 前要把 $T$ 拼回，见 `nvidia-context-parallel`。训练 CP 是空间上切开一条序列。Serving 的长 prompt 更常走 chunked prefill 或 prefill / decode 分池，那是时间上切开，见 `nvidia-chunked-prefill`。推理引擎里也可以对 prefill 做 context parallel，KV 再汇到 decode 池，那是另一张部署图。

## 追问

- **不用 P2P 行不行？** 可以 all-to-all / all-gather 变体（Ulysses 那类换 head 和 $T$）。环适合大块带宽重叠；all-to-all 对某些 $N$ 和拓扑更简单。没 profile 过不要说谁一定快。
- **CP 能不能跨机？** 能，KV 块是带宽项。仍要看一步 FA 是否长过 P2P。TP 的 all-reduce 跨机通常更伤，所以先把 TP 留在节点内。
- **$N$ 开到和 $T$ 一样？** 每卡一段极短，FA 核和 P2P 延迟把 MFU 打穿。CP 是为了放得下，不是越大越好。
- **MoE 呢？** 专家并行切的是 expert，通信是 token all-to-all，见 `nvidia-moe-gemm`。和 CP 叠是四维以上，路由不均会和环负载再耦合，先把 dense CP 讲清。

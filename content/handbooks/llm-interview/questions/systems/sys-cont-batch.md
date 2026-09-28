---
id: sys-cont-batch
section: systems
order: 9
level: A
title: Continuous Batching 为什么提升吞吐？
quick: >-
  不同请求生成长度差很多。Static batch 里短的已经 EOS，槽位还在空等最长那条。Continuous batching 在
  token 或请求完成时立刻补进新请求，GPU 空等少了，吞吐才上去。调大静态 batch 消不掉这笔税。
tags:
  - Serving
  - Scheduling
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: 'Orca: A Distributed Serving System for Transformer-Based Generative Models'
    url: https://www.usenix.org/conference/osdi22/presentation/yu
    type: primary
  - title: vLLM PagedAttention
    url: https://arxiv.org/abs/2309.06180
    type: primary
---

错法：「把 batch size 调大」。Static 大 batch 仍然按 **整条请求** 对齐：短的已经 EOS，槽位空等最长那条，GPU 在算 padding。Continuous batching（Orca 的 iteration-level scheduling）把调度粒度改成 **每个 decode step**：完成的序列立刻移出，waiting 队列里的新请求补入。吞吐来自 **减少空等**，不是来自更大的静态矩阵。把 `max_num_seqs` 开大只是给连续调度更多候选，本身不会消除静态对齐的税；没有 iteration-level 调度，大 batch 只是更贵的空等。LLM 生成长度方差远大于分类模型，RL 组内 $n$ 条更甚，所以这题和「为什么 rollout 要用 vLLM」是同一套调度故事。

## Static batch 空在哪

$B$ 条请求一起 generate，长度 $T_1,\ldots,T_B$ 可差一个数量级。静态实现 pad 到 $\max T_i$，先结束的行仍占着整行 KV 和计算槽，直到最慢那条写完。有效 token/s 被最长尾部决定，算术上看着在做 $[B,d]\times[d,d]$，实际有的行已经是 mask 掉的废计算。LLM 生成长度方差大（聊天几十字、CoT 几千字），这个税比分类模型严重得多。RL 的组内 $n$ 条同样长短不齐，所以 rollout 也吃这套调度，见 `sys-rl-why-vllm-rollout`。

## 每步重选 active 集合

Serving scheduler 每个 decode iteration：

1. 把本步已 EOS 的序列移出，释放 KV 页（PagedAttention 让释放立刻可复用，而不是按 max length 预留）。
2. 若还有槽位和 KV 容量，从 waiting 队列插入新请求，先做它们的 prefill（或 chunked prefill）。
3. 对仍在生成的集合做一步 decode。

于是 GPU 上的有效 $B$ 维持在高位，decode 的瘦 GEMM 被喂得更满，同时 HBM 上的死 KV 变少。Orca 强调 iteration-level；vLLM 用分页 KV 把「插入新请求」从内存形状上做可行。没有 paging，按最大长度预留，连续补位很快 OOM，调度器有策略也没地方放。插入新请求时通常要先 prefill：这一步是 compute-bound，会短暂打断 decode 的带宽流水。所以工程上还有 chunked prefill：把大 prompt 切块，每块之间仍插入 decode step，避免一条 8k prompt 让所有在飞请求的 TPOT 尖刺。PD 分离则把这件事做到池级别。连续 batching 是单池内的时间复用；PD 分离是跨池的空间复用。面试不要把两层说成一个开关。

## 代价不是免费

调度更复杂：KV block 分配、碎片、公平性、抢占、与 latency SLO 的权衡。追求吞吐而过度 batching，单请求 TPOT 会恶化，goodput 可能下降，见 `sys-serving-metrics`。一条超长 prefill 插入 decode 批次，会打断带宽流水，所以有 chunked prefill 和 PD 分离。公平性：一直插入短请求可能饿死长请求，要有 max waiting / aging。

不要把 continuous batching 说成异步 RL。前者是引擎一步之内的请求交错；后者是 trainer 与 rollout 之间的流水线，带 policy staleness，见 `slime-async-train`。KV 碎片会把「理论上能插入」变成「页不够、只好等」：结束序列释放的页如果和后来者的块大小对不齐，利用率仍上不去。所以 paging 的块大小、preemption（把长请求踢回 CPU）和公平性策略会一起出现。过度追求吞吐把 `max_num_seqs` 开到 KV 爆边，P99 TPOT 先坏，goodput 下降。调度器目标往往是 goodput，不是瞬时 tokens/s。RL rollout 里组内 $n$ 条同时进引擎，连续 batching 让短回复立刻把页让给下一题，这是训练图静态 generate 做不到的。换引擎的收益，很大一部分就是这套调度。

## 和 paging、PD、异步的边界

Continuous batching 管时间粒度：每个 decode step 换人。PagedAttention 管内存形状：结束的 KV 按页还给后来者。没有 paging，连续调度很快在预留上 OOM；没有连续调度，paging 只是少碎片，短请求仍空等。Chunked prefill 和 PD 分离管 prefill 打断 decode：前者单池切块，后者拆成两个池。异步 RL 是 trainer 与引擎之间的流水线，带 stale，完全另一层。RL 组采样长度方差大，最吃连续调度；短而齐的 SFT 式生成看不太出差距。过调度会伤 goodput：有效 $B$ 太大，TPOT 打穿 SLO。

## 追问

- **和动态 padding 是一回事吗？** 不是。动态 padding 仍等整 batch 结束才换人；continuous batching 在每个 decode token 边界就移出 EOS、插入 waiting。粒度从请求级变成 iteration 级，这才是 Orca 的点。
- **为什么要 PagedAttention？** 结束序列的 KV 必须能按页还给后来者。按最大长度连续预留做不到细粒度回收，调度器有策略也没地方放新请求，很快 OOM。
- **batch 是不是越大越好？** 有效 $B$ 提高 decode 算术强度，但 KV 容量和 TPOT SLO 封顶。frontier 在 goodput，不在峰值 tokens/s。`max_num_seqs` 开到爆边，P99 先坏。
- **RL 组采样为什么更吃这套？** 同一 prompt 的 $n$ 条长度方差极大，静态 batch 几乎总在等最长 CoT。这正是训练图 `generate` 最不擅长的负载，见 `sys-rl-why-vllm-rollout`。
- **算异步 RL 吗？** 不算。这是引擎内部交错请求，没有 policy version 差。异步 RL 是 trainer 与引擎之间的流水线，见 `slime-async-train`。
- **和 PD 分离什么关系？** 连续 batching 是单池时间复用；PD 分离是跨池空间复用，避免大 prefill 打断 decode。chunked prefill 是单池折中。
- **没有 paging 只做连续调度行不行？** 很快 OOM：结束序列的 KV 按最大长度占着，新请求没有页可分。Orca 的调度和 vLLM 的分页是配套。
- **抢占长请求是为了什么？** 短请求一直插入会饿死长请求，P99 对长会话爆炸。aging / max waiting / 把长请求 KV 踢到 CPU 是公平性，会伤吞吐，换的是尾延迟。
- **和「把 batch 调大」差在哪？** 静态大 batch 仍等最长请求；连续 batching 在每个 decode step 换人。吞吐来自减少空等。没有 paging，连续补位会 OOM。这和异步 RL 不是一层。

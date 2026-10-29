---
id: sys-act-checkpoint
section: systems
order: 3
level: A
title: 系统：activation checkpoint 重算 vs 存，和序列并行叠
quick: >-
  Activation checkpoint 只保留 segment boundaries 激活，反向再运行段内前向，用计算换
  HBM。它能与序列并行叠加：SP 减少 LN / dropout 的复制，checkpoint 再减少反向保留的中间量，是否提速要看省下显存能否换来更合适的
  batch。
tags:
  - NVIDIA
  - Training
  - Memory
  - Checkpointing
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Training Deep Nets with Sublinear Memory Cost
    url: 'https://arxiv.org/abs/1604.06174'
    type: primary
  - title: Reducing Activation Recomputation in Large Transformer Models
    url: 'https://arxiv.org/abs/2205.05198'
    type: primary
  - title: Megatron-LM
    url: 'https://arxiv.org/abs/1909.08053'
    type: primary
  - title: Sequence Parallelism
    url: 'https://arxiv.org/abs/2105.13120'
    type: primary
---

## 可以这样回答

Activation checkpoint 是前向少存中间结果、反向按需重算，用额外计算换激活显存。比如长序列卡住 microbatch 时，省下空间后可以扩大 $B$ 或 $T$，GEMM 更饱满，整体未必更慢；本来已经 compute-bound，则更可能增加耗时。

这里讨论训练 step 内的 HBM，区别于容错时把状态写盘。NVIDIA Megatron、Google 长上下文训练、Meta FSDP 都涉及这项选择；OpenAI 白板版可见 `openai-grad-checkpoint`。配置时要明确重算便宜算子还是大 GEMM，以及是否与 FlashAttention、序列并行重复处理同一批张量。

## 技术备查

Activation checkpoint 是前向少存中间结果、反向按需重算，用额外计算换激活显存。比如长序列卡住 microbatch 时，省下空间后可以扩大 $B$ 或 $T$，GEMM 更饱满，整体未必更慢；本来已经 compute-bound，则更可能增加耗时。

这里讨论训练 step 内的 HBM，区别于容错时把状态写盘。NVIDIA Megatron、Google 长上下文训练、Meta FSDP 都涉及这项选择；OpenAI 白板版可见 `openai-grad-checkpoint`。配置时要明确重算便宜算子还是大 GEMM，以及是否与 FlashAttention、序列并行重复处理同一批张量。

不 checkpoint 时，每层把反向要用的激活留在 HBM，随层数约为 $O(L)$。Transformer 里这份东西跟 $B\cdot T\cdot L\cdot h$ 走，长序列时经常比参数还大。ZeRO 再怎么切状态也碰不到它。

做法：只在 segment boundaries 留一份激活，段内中间结果丢掉。反向进入该段，从 checkpoint locations 再 forward 一遍，恢复张量再算梯度。Chen et al. 的结论是：checkpoint placement 合适，激活显存大约 $O(\sqrt{L})$，额外计算是常数倍前向。实务很少每一算子都重算，常见是每个 Transformer block 一个 checkpoint location，或 selective：只重算便宜的 LayerNorm / dropout / attention 分数，大 GEMM 的输出该存还是存。

因此要同时量激活 HBM 降幅、额外 forward FLOPs，以及重算能否与集体通信错开。

已经 compute-bound、batch 也喂饱了，再付百分之二十到三十的 FLOPs 是纯税。本来被显存卡住、microbatch 开不大、GEMM 很瘦，用省下的显存把 $B$ 或 $T$ 加倍，算术强度提高后，实际耗时也可能缩短。是否划算，要用这个负载变化前后的 step time 来判断。

一个数量级：不 checkpoint 时激活大致跟 $B\cdot T\cdot L\cdot h$ 走；每 block 留一个 checkpoint location，激活大约按 $\sqrt{L}$ 降，前向大约再付 $1\times$。Selective 只重算 LN / dropout，额外 FLOPs 可以压到百分之十以下，显存降幅仍可观。Selective 与每层全重算的主要差别，就在于额外 FLOPs 和保存张量的取舍。

Megatron 的序列并行（见 `sys-seq-parallel`）先解决一件 TP 留下的浪费：LayerNorm、dropout 的激活在 TP 组里是复制的。SP 把它们按序列维切开，每卡只留 $T/\mathrm{TP}$。这和 checkpoint 不是替代关系：

1. SP 降低的是「TP 复制」那一份，通信从 all-reduce 改成 all-gather / reduce-scatter。
2. Checkpoint 降低的是段内还要为反向留着的大张量，通常是 MLP 中间 $[B,T,4h]$ 一类。
3. FlashAttention 已经不把 $[B,H,T,T]$ 分数矩阵写回 HBM，再 checkpoint「attention 分数」就是在打空靶。

Korthikanti 的 selective recomputation 正是这个组合：SP 切序列局部激活，selective 重算便宜 op，昂贵 GEMM 能存就存。三件一起开时，峰值常出现在 FSDP all-gather 权重和重放本段激活叠在同一窗口。Schedule 要把 prefetch 和 recompute 错开，否则省显存的开关把实际耗时拉长，Nsight 上 SM 在等通信。

和 PP 一起用要注意：重算拉长每个 stage 的计算，1F1B 的气泡公式要重算一遍。只在某个 stage 开激进 checkpoint，负载会更不齐。

这不会省掉 decode 下一步需要的历史 KV，activation checkpoint 作用于训练图的正反向。状态侧的分片见 `sys-zero-stages`。

## 追问

**每层都 checkpoint 好不好？**
显存最省，计算接近再付一次前向。目标是刚好放下目标 $B\times T$，不是越大越好。
**和 CPU offload 怎么选？**
Offload 走 PCIe；checkpoint 留在 GPU 上重算。带宽差的机器优先 checkpoint。优化器太大才轮到 ZeRO offload。
**为什么有时开了更快？**
之前被显存卡住。省下的激活换成更大 batch，把额外 forward 赚回来。已经喂满 Tensor Core 再开就是税。
**FSDP + checkpoint 峰值在哪？**
常在某层权重 gather 齐、同时重放该段激活。错开 prefetch。

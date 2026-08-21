---
id: sys-checkpoint
section: systems
order: 5
level: A
title: Activation Checkpointing 的 Compute–Memory Tradeoff 是什么？
quick: >-
  前向只保存少量 checkpoint activations，反向需要时重算被丢弃的中间激活；显存显著下降，代价是额外 forward compute
  和更复杂 schedule。
tags:
  - Training
  - Memory
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: Training Deep Nets with Sublinear Memory Cost
    url: https://arxiv.org/abs/1604.06174
    type: primary
  - title: ZeRO
    url: https://arxiv.org/abs/1910.02054
    type: primary
---

陷阱是说「checkpoint 更省计算」或把它和 **权重 checkpoint 落盘** 混为一谈。Activation checkpointing（gradient checkpointing）卖的是 **显存**：前向丢掉中间激活，反向从边界重放。FLOPs 一定增加（多一段 forward），换来的是更大 batch / 更长序列。整体吞吐升还是降，取决于你是不是本来被显存卡住。落盘的 weight checkpoint 管容错与恢复；activation checkpoint 管这一步 HBM 里留多少中间张量。两个英文词撞车，面试先划清。先诊断卡住的是激活、优化器还是 KV，再用对药；用错会把 FLOPs 税加在已经喂饱的模型上。

## 存什么、重算什么

不 checkpoint 时，每层都把给反向用的激活留在 HBM：Transformer 里大约随层数、序列长度、$d$、batch 线性涨，往往比参数本身还大。Checkpoint 只在段边界留一份激活，段内中间结果丢弃。反向进入该段时，从边界再 forward 一遍，恢复被丢的张量再算梯度。

Chen et al. 指出，合理选边界可以把激活显存从 $O(L)$ 降到大约 $O(\sqrt{L})$，代价是额外常数倍计算。极端 full recompute：几乎只留输入，显存最省，计算最多（接近再付一次前向）。实务是每几层、或每个 Transformer block 一个 checkpoint，而不是每一算子都重算。

面试写清两笔账：

- **省：** 激活显存（常是训练峰值的大头）。
- **付：** 额外 forward FLOPs，以及重算与通信如何重叠。本来 compute-bound 的大 GEMM 上，再加 20–30% FLOPs 会直接打吞吐；本来 memory-bound、batch 开不大，用省下的显存把 batch 加倍，有效 MFU 反而可能上去。

## 何时整体更快

看模型是 compute-bound 还是 memory-bound、通信能不能 overlap。长上下文、大 batch 的激活先爆时，checkpoint 是换吞吐的正操作：没有它你只能把 $B$ 或 $T$ 砍掉，流水线气泡更大。短序列、已经喂满 Tensor Core 时，再重算就是纯税。

和 ZeRO / FSDP 正交：ZeRO 分的是 **参数、梯度、优化器状态**；checkpoint 分的是 **激活生命周期**。两边一起开很常见，但峰值仍可能出现在 all-gather 权重和重算激活叠在同一段。Schedule 要把通信与重算错开，否则「省显存」的开关把墙钟拉长，MFU 数字很难看，见 `infra-rl-mfu-6nd`。

RL 里还有一次「假 checkpoint」：rollout 的 KV 不能靠重算随便扔，decode 下一步还要用。Activation checkpoint 只作用于训练图的正反向，不要说成也能省 KV。长序列时激活随 $T$ 涨得比参数快，checkpoint 几乎是必开；短 SFT 已经喂满算力时可以少开，把 FLOPs 留给有效 token。选边界的经验是：优先砍激活最大的块（MLP 中间、attention 的大张量），不要在已经很小的 layernorm 上重算。和 pipeline 一起用时，重算会拉长每个 stage 的计算，气泡公式要重算一遍。面试被问「你开了多少」时，报的是「每 block 一次、能把峰值显存压到刚好放下目标 $B\times T$」，而不是一个魔法比例。

## 和重算 logp 不是一件事

HybridEngine / 采样后再用训练图算 $\log\pi_\theta$，是为了数值对齐，不是为了省激活显存。面试把 activation checkpoint、weight offload、recompute logp 画成三件：一件管训练激活、一件管参数驻留、一件管 ratio 的图。混成「都是 recompute」会被追问拆穿。ZeRO-3 / FSDP 已经在反向前后 gather/scatter 参数，再叠 full activation recompute，墙钟税是相加的，MFU 看起来会很差。这时要问：显存是被激活卡住还是被优化器状态卡住。前者才值得加 checkpoint；后者应上 ZeRO 分片或 offload，见 ZeRO 论文。两味药对两类病，不要因为「都和内存有关」就一起加到最大。

## 先诊断卡住的是哪类内存

显存账本拆成参数、梯度、优化器状态、激活、KV。Activation checkpoint 只打激活这一项。优化器太大应对 ZeRO/FSDP 分片或 offload；KV 太大应对 paging、更小的 `rollout.n`、更短的生成。用错药会把 FLOPs 税加在已经 compute-bound 的模型上，MFU 更差、峰值却没下来。选边界按 block，目标是「刚好放下目标 $B\times T$」，不是越大越好。和通信重叠：FSDP all-gather 与重放叠在同一段会制造新峰值，要错开 prefetch。和落盘 checkpoint、recompute logp 三件重算必须分清。长上下文几乎必开；短序列喂满 Tensor Core 时可以少开。面试报的是「为了放下多大的 batch、付了多少额外 forward」，而不是「我们开了 checkpoint」。

先诊断卡住的是激活、优化器还是 KV，再用 checkpoint、ZeRO 或 paging。Activation checkpoint 只打激活，FLOPs 一定增加，整体是否更快取决于你是不是本来被显存卡住。和落盘 ckpt、recompute logp 三件重算分清。长上下文几乎必开；短序列喂满 Tensor Core 时可以少开。报的是「为了放下多大的 $B\times T$、付了多少额外 forward」，而不是「我们开了 checkpoint」。

## 追问

- **为什么有时开了反而更快？** 省下的激活换成更大 batch / 更长序列，算术强度上去，把额外 forward 赚回来。前提是你之前被显存卡住、GEMM 喂不饱。已经 compute-bound 再重算就是纯税。
- **和 CPU offload 怎么选？** Offload 走 PCIe，延迟高；checkpoint 留在 GPU 上重算。带宽差的机器优先 checkpoint，而不是把激活甩到 CPU。优化器状态太大才轮到 ZeRO offload。
- **每层都 checkpoint 好不好？** 显存最省，计算接近再付一次前向。通常按 Transformer block 选边界，目标是刚好放下目标 $B\times T$，不是越大越好。
- **FSDP + checkpoint 峰值在哪？** 常在某层 all-gather 齐权重、同时重放该段激活。要错开 prefetch，否则「省显存」的开关把墙钟拉长，MFU 很难看。
- **和落盘 checkpoint、recompute logp 是一件事吗？** 不是。落盘管容错；activation checkpoint 管训练激活生命周期；recompute logp 管 ratio 的数值图。三件重算混说会被拆穿。
- **能不能省 KV？** 不能。Decode 下一步还要用历史 KV，activation checkpoint 只作用于训练图正反向。KV 要用 paging 和更小的 inflight 集合来管。
- **和 pipeline 一起开要注意什么？** 重算拉长每个 stage 的计算，气泡公式要重算。别只在一个 stage 开激进 checkpoint，负载会更不齐。
- **20–30% 额外 FLOPs 一定亏吗？** 若因此 batch 加倍、算术强度上去，有效吞吐可能更好。用「能不能放下目标 $B\times T$」判断，不要用额外 FLOPs 百分比当否决。
- **和 ZeRO 怎么分工？** ZeRO/FSDP 分参数、梯度、优化器；checkpoint 分激活生命周期。激活爆了才加 checkpoint，优化器爆了才加分片或 offload。两味药对两类病。和落盘 ckpt、recompute logp 也不是一件事：一件管容错，一件管训练激活，一件管 ratio 的图。

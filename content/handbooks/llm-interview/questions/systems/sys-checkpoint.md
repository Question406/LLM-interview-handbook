---
id: sys-checkpoint
section: systems
order: 5
level: A
title: Activation Checkpointing 的 Compute–Memory Tradeoff 是什么？
quick: >-
  前向只保留 segment boundaries 的激活，反向需要段内结果时再 forward 重算，用额外计算换显存。省出的空间能让 batch
  或序列变大时，整体 throughput 可能提高；已经受算力限制时，重算通常会拖慢训练。
tags:
  - Training
  - Memory
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: '2026-10-28'
sources:
  - title: Training Deep Nets with Sublinear Memory Cost
    url: 'https://arxiv.org/abs/1604.06174'
    type: primary
  - title: ZeRO
    url: 'https://arxiv.org/abs/1910.02054'
    type: primary
---

## 可以这样回答

Activation checkpointing（gradient checkpointing）用额外 forward 换激活显存：前向只留 segment boundaries，反向再重算段内结果。比如激活让目标 batch 放不下，省出的显存可能允许更大的 batch 或更长序列，整体 throughput 就有机会提高。它管理当前 step 的 HBM；落盘的 weight checkpoint 管容错恢复。使用前先确认显存主要被激活、优化器还是 KV 占用。

## 技术备查

Activation checkpointing（gradient checkpointing）用额外 forward 换激活显存：前向只留 segment boundaries，反向再重算段内结果。比如激活让目标 batch 放不下，省出的显存可能允许更大的 batch 或更长序列，整体 throughput 就有机会提高。它管理当前 step 的 HBM；落盘的 weight checkpoint 管容错恢复。使用前先确认显存主要被激活、优化器还是 KV 占用。

不 checkpoint 时，每层都把给反向用的激活留在 HBM：Transformer 里大约随层数、序列长度、$d$、batch 线性涨，往往比参数本身还大。Checkpoint 只在 segment boundaries 留一份激活，段内中间结果丢弃。反向进入该段时，从 checkpoint locations 再 forward 一遍，恢复被丢的张量再算梯度。

Chen et al. 指出，合理选择 checkpoint locations 可以把激活显存从 $O(L)$ 降到大约 $O(\sqrt{L})$，代价是额外常数倍计算。极端 full recompute：几乎只留输入，显存最省，计算最多（接近再付一次前向）。实务是每几层、或每个 Transformer block 一个 checkpoint，而不是每一算子都重算。

计算这笔取舍时，要同时看节省的显存和增加的计算：

**省：**
激活显存（常是训练峰值的大头）。
**付：**
额外 forward FLOPs，以及重算与通信如何重叠。本来 compute-bound 的大 GEMM 上，再加 20% 到 30% FLOPs 会直接打 throughput；本来 memory-bound、batch 开不大，用省下的显存把 batch 加倍，有效 MFU 反而可能上去。

看模型是 compute-bound 还是 memory-bound、通信能不能 overlap。长上下文、大 batch 的激活先爆时，checkpoint 是换 throughput 的正操作：没有它你只能把 $B$ 或 $T$ 砍掉，流水线气泡更大。短序列、已经喂满 Tensor Core 时，再重算就是纯税。

和 ZeRO / FSDP 正交：ZeRO 分的是 **参数、梯度、优化器状态**；checkpoint 分的是 **激活生命周期**。两边一起开很常见，但峰值仍可能出现在 all-gather 权重和重算激活叠在同一段。Schedule 要把通信与重算错开，否则「省显存」的开关把实际耗时拉长，MFU 数字很难看，见 `infra-rl-mfu-6nd`。

RL 的 sampling 轨迹（rollout）还会占用 KV，但逐 token 生成（decode）的下一步要继续读取历史 KV，不能用训练图的 activation checkpoint 随意丢弃。Activation checkpoint 只作用于训练图的正反向，不要说成也能省 KV。长序列时激活随 $T$ 涨得比参数快，checkpoint 几乎是必开；短 SFT 已经喂满算力时可以少开，把 FLOPs 留给有效 token。选择 checkpoint locations 时我优先砍激活最大的块（MLP 中间、attention 的大张量），不会在已经很小的 layernorm 上重算。和 pipeline 一起用时，重算会拉长每个 stage 的计算，气泡公式要重算一遍。配置可以按每 block 一次起步，目标是让峰值显存刚好放下所需的 $B\times T$。

HybridEngine / sampling 后再用训练图算 $\log\pi_\theta$，是为了数值对齐，不是为了省激活显存。activation checkpoint 管训练激活，weight offload 管参数驻留，recompute logp 管 ratio 使用的计算图，需要分别配置和验证。ZeRO-3 / FSDP 已经在反向前后 gather/scatter 参数，再叠 full activation recompute，实际耗时税是相加的，MFU 看起来会很差。这时要问：显存是被激活卡住还是被优化器状态卡住。前者才值得加 checkpoint；后者应上 ZeRO 分片或 offload，见 ZeRO 论文。先按显存组成确定配置，避免两边一起开到最大却没有额外收益。

显存账本拆成参数、梯度、优化器状态、激活、KV。Activation checkpoint 只打激活。优化器太大用 ZeRO/FSDP 或 offload；KV 太大用 paging、更小的 `rollout.n`、更短生成。用错会把 FLOPs 税加在已经 compute-bound 的模型上。checkpoint locations 按 block 选择，目标是刚好放下 $B\times T$。FSDP all-gather 与重放叠在同一段会造新峰值，要错开 prefetch。实际验证时，要报告能放下多大的 $B\times T$，以及为此付出了多少额外 forward。

## 追问

**为什么有时开了反而更快？**
省下的激活换成更大 batch / 更长序列，算术强度上去，把额外 forward 赚回来。前提是你之前被显存卡住、GEMM 喂不饱。已经 compute-bound 再重算就是纯税。
**和 CPU offload 怎么选？**
Offload 走 PCIe，延迟高；checkpoint 留在 GPU 上重算。带宽差的机器优先 checkpoint，而不是把激活甩到 CPU。优化器状态太大才轮到 ZeRO offload。
**每层都 checkpoint 好不好？**
显存最省，计算接近再付一次前向。通常按 Transformer block 选择 checkpoint locations，目标是刚好放下目标 $B\times T$，不是越大越好。
**FSDP + checkpoint 峰值在哪？**
常在某层 all-gather 齐权重、同时重放该段激活。要错开 prefetch，否则「省显存」的开关把实际耗时拉长，MFU 很难看。
**和落盘 checkpoint、recompute logp 是一件事吗？**
分别解决不同的问题：落盘管容错，activation checkpoint 管训练激活生命周期，recompute logp 管 ratio 的数值图。
**能不能省 KV？**
不能。Decode 下一步还要用历史 KV，activation checkpoint 只作用于训练图正反向。KV 要用 paging 和更小的 inflight 集合来管。
**和 pipeline 一起开要注意什么？**
重算拉长每个 stage 的计算，气泡公式要重算。别只在一个 stage 开激进 checkpoint，负载会更不齐。
**20% 到 30% 额外 FLOPs 一定亏吗？**
若因此 batch 加倍、算术强度上去，有效 throughput 可能更好。用「能不能放下目标 $B\times T$」判断，不要用额外 FLOPs 百分比当否决。
**和 ZeRO 怎么分工？**
ZeRO/FSDP 分参数、梯度、优化器；checkpoint 分激活生命周期。激活爆了才加 checkpoint，优化器爆了才加分片或 offload。和落盘 ckpt、recompute logp 也分得开：一件管容错，一件管训练激活，一件管 ratio 的图。

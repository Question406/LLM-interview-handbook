---
id: tencent-beyond-deepspeed
section: systems
order: 211
level: A
title: 腾讯混元：除了 DeepSpeed，训练还能靠哪些优化？
quick: >-
  并行切 Megatron 式 TP/PP/SP；内存切 activation checkpoint、CPU/NVMe
  offload、LoRA；算子切 FlashAttention / fused kernel；框架切 FSDP2。先说瓶颈是算力、显存还是通信，再点名对应手段。
tags:
  - Tencent
  - Hunyuan
  - Training Systems
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 腾讯-混元大模型面经-华5硕
    url: https://www.nowcoder.com/feed/main/detail/692fed73109e4d31915e46d34d27c762
    type: candidate-first-hand
  - title: Megatron-LM
    url: https://arxiv.org/abs/1909.08053
    type: primary
  - title: ZeRO
    url: https://arxiv.org/abs/1910.02054
    type: primary
---

我会按瓶颈答，不报框架名单。这块容易把 DeepSpeed 当成「训练优化」的同义词，然后背 ZeRO-1/2/3。DeepSpeed 主要管**数据并行下的状态分片**；放不下、算不满、跨节点慢、微调划不来，对应的手段不在同一层。我先说量到的是显存峰值、MFU 还是通信等待，再点名一两个真用过的。混元这种稠密大模型，常见组合是 Megatron TP/PP + ZeRO-1/2，而不是一上来 ZeRO-3 打天下。分片表见 `tencent-zero-123`，72B 估算见 `tencent-zero3-qwen72b-mem`。

## 真题记录

- 公司：腾讯 · 混元
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“除了 DeepSpeed 还有哪些训练优化？”**

## 先按瓶颈分层

- **放不下**：ZeRO / FSDP 分状态；activation checkpoint 用重算换显存；CPU / NVMe offload；减序列或开序列并行 / 上下文并行。ZeRO 不切 activation，长序列仍会 OOM，见 `sys-memory`。把「开了 ZeRO-3」当成显存问题的终点，下一问 8k SFT 仍会炸。
- **算不满**：FlashAttention、fused softmax / LayerNorm、更大有效 micro-batch、通信重叠。MFU 低先看是否在等 all-reduce、是否被 padding 稀释、data loader 是否 stall。算子优化改变的是同一层算得快不快，不是切参数。
- **跨节点慢**：减 PP bubble（1F1B、更合理的 micro-batch 数）、TP size 不要跨过节点、小模型别过早上 ZeRO-3（每层 gather 比计算还贵）。通信是瓶颈时再堆分片会更慢。
- **微调场景**：LoRA / QLoRA 往往比再堆并行更划算。可训参数掉两个数量级，优化器状态跟着掉。底座冻结后，DeepSpeed 可能根本不是第一杠杆。

点名 Megatron-LM（TP/PP）、PyTorch FSDP2、Megatron-DeepSpeed 混合即可，不会装四套都操过。重点是 DeepSpeed 不是全集，不是做框架导购。SFT 参数量和利用率怎么估，见 `tencent-sft-parameter-gpu-utilization`。

## 并行、内存、算子不要混着报

并行切的是**计算图**：TP 切隐层矩阵，PP 切层，SP/CP 切序列，EP 切专家。内存切的是**存什么**：checkpoint、offload、分片、冻结底座。算子切的是**同一层算得快不快**：FlashAttention、MoE permute 融合。把「开了 ZeRO-3」说成算子优化，下一问通信量会对不上。把 FlashAttention 说成并行策略，下一问「那 TP 还要不要」会乱。混元面试常和 ZeRO 分档连问：先画 1/2/3 分什么，再说「除了 DeepSpeed」还有 Megatron 切图、checkpoint 切激活、LoRA 切可训参数。三句话分属三层，不要揉成「我们还用了很多优化」。没 profile 就报名单，不如承认「我只深用过其中一层」。

落到混元这种稠密大模型，优先级通常是：先把 TP 和 PP 配到计算图能跑，再用 ZeRO-1/2 把 Adam 放下，长序列再上 checkpoint 或 SP，算不满再上 FlashAttention 和更大有效 batch。微调则把 LoRA 提前，可能整段并行都不必上到 3。我会按这条优先级讲。若对方追「你实际用过哪几个」，只深讲自己做过的那一层，其余点名即可。没有测量就说「我们还开了 offload 和 ZeRO-3 和 FlashAttention」，下一问「哪一个解决了你当时的瓶颈」会对不上。先瓶颈、后手段、再承认没做过的层。72B 全参和 72B LoRA 不是同一套答案，先问清再点名。

## 追问

- **为什么不先上 ZeRO-3？** 能放下就停在 1/2，少付每层 all-gather。单卡参数 + Adam 已经爆再升 3。小 batch 升 3 常更慢。
- **FlashAttention 算哪一类？** 算子 / 激活峰值，不是并行策略。它降 $T^2$ 工作区，不切参数，也不替代 ZeRO。
- **LoRA 还要不要 DeepSpeed？** 底座冻结时优化器很小，FSDP / 单机往往够；只有底座也在算、显存仍紧才叠分片。
- **SP 和 ZeRO 能互相替代吗？** 不能。SP 切的是序列激活，ZeRO 切的是参数状态。长上下文两者经常要一起上。
- **怎么证明你不是在报名单？** 先说瓶颈指标（峰值显存、MFU、step time 里通信占比），再点一个对应手段和你用过的规模。
- **和「72B 单卡估算」怎么衔接？** 先分片表，再代入 $N$ 和是否 LoRA。估算卡是 `tencent-zero3-qwen72b-mem`，本卡只负责「DeepSpeed 之外还有哪几层」。
- **offload 算哪一类？** 内存类：把优化器甚至参数放到 CPU / NVMe，换的是速度。显存极紧、吞吐要求不高的微调才优先；预训练很少把这当第一杠杆。
- **1F1B 解决什么？** PP 的气泡，不是 ZeRO 的分片。跨节点慢时才提，别和 all-gather 混在一句里。
- **没有测量能不能报三层？** 能点名，不能假装都操过。先说当时瓶颈是显存、MFU 还是跨节点，再深讲自己做过的那一层。
- **预训练和微调的优先级差在哪？** 预训练少不了切图和分状态；微调先问能不能 LoRA。把 72B 全参的答案套到 LoRA 上，会无谓地升到 ZeRO-3。
- **和分档题连问时先画什么？** 先画 ZeRO 1/2/3 分什么，再点 Megatron、checkpoint、LoRA。表内是 DeepSpeed，表外才是这题要的「还有哪些」。

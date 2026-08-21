---
id: tencent-zero-123
section: systems
order: 210
level: A
title: 腾讯混元：ZeRO-1 / 2 / 3 各分什么，什么时候升到 3？
quick: >-
  ZeRO-1 只分优化器；2 再分梯度；3 连参数也分，前向 all-gather、反向 reduce-scatter。单卡放不下模型或全参
  Adam 时升 3；能放下就停在 1/2，少付通信。72B 估算见另一张显存卡，这里先把分片表讲清。
tags:
  - Tencent
  - Hunyuan
  - ZeRO
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 腾讯-混元大模型面经-华5硕
    url: https://www.nowcoder.com/feed/main/detail/692fed73109e4d31915e46d34d27c762
    type: candidate-first-hand
  - title: ZeRO
    url: https://arxiv.org/abs/1910.02054
    type: primary
---

陷阱是把 ZeRO 说成「越高级越省、所以上 3」。ZeRO 切的是**参数 / 梯度 / 优化器状态**，不是 activation；升一级就多一类集体通信。能放下就停在 1/2。和「72B 单卡估算」连问时，先画分片表再代入 $N$，不要先报一个 GB。FSDP 的 `fully_shard` 对应的是 ZeRO-3 这一档，不要把名字换了就当另一种算法。bytes/param 总账见 `sys-memory`，代入 72B 见 `tencent-zero3-qwen72b-mem`，DeepSpeed 之外的手段见 `tencent-beyond-deepspeed`。

## 真题记录

- 公司：腾讯 · 混元
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“ZeRO-1、2、3 有什么区别？”**

## 三张分片表

| Stage | 参数 | 梯度 | 优化器 |
| --- | --- | --- | --- |
| DP | 复制 | 复制 | 复制 |
| ZeRO-1 | 复制 | 复制 | 分片 |
| ZeRO-2 | 复制 | 分片 | 分片 |
| ZeRO-3 | 分片 | 分片 | 分片 |

Adam 状态通常是大头（FP32 $m/v$ + master，约 $12$ bytes/param），所以 ZeRO-1 往往就能把单卡从「Adam 爆」救回来，参数仍复制、前向通信少。ZeRO-2 在反向做 reduce-scatter，梯度不再每卡一份，反向峰值下降。ZeRO-3 前向按层 all-gather 参数、用完丢掉，反向再 gather 一次并 reduce-scatter 梯度。单卡参数占用约 $/D$，但每层都有通信与气泡。Activation、临时 buffer **都不在这张表里**，长序列 OOM 升 3 没用，要 checkpoint / SP / 减 $T$。面试把「稳态占用」和「all-gather 峰值」分开说：ZeRO-3 的 `nvidia-smi` 对不上 $16N/D$ 是正常的。小模型、小 batch 时计算喂不饱，升 3 会让 MFU 掉，看起来像「优化了反而慢」。

## 什么时候升到 3

升 3 的信号：BF16 参数 + 全参 Adam 已超单卡，或要开更大 batch / 序列、复制份已经装不下。72B BF16 权重约 $144\,\mathrm{GB}$，未分片 Adam 状态再乘好几倍，单卡不可能复制参数，必须 3 或 TP/PP 把 $N$ 切开。代价是每层 gather。LoRA 微调 72B 往往不必上 3：可训参数是 adapter，底座可冻结甚至 offload。能用 ZeRO-2 + 适度 TP 放下，就不要为了「用过 3」去付通信。和 TP 叠用时：TP 切计算图和激活，ZeRO 切 DP 维上的状态，两层不是替代关系。混元稠密大模型常见 TP + ZeRO-1/2；只有 DP 维已经很大、单卡仍放不下完整分片参数，才把 ZeRO 推到 3。先问清全参还是 LoRA、有没有 TP，再决定升不升。口诀可以记成：1 救 Adam，2 再削梯度峰值，3 才动参数、开始按层通信。不要跳级。7B 全参在 8×80GB 上经常 1 就够；13B–32B 看序列和 batch，2 往往是甜点；72B 全参几乎必然要 3 或把 $N$ 切开。面试被追「为什么不直接 3」时，答通信：每层 all-gather 在小 batch、小模型上会比计算还贵，MFU 掉下来，看起来像优化失败。被追「为什么升 3 还 OOM」时，答激活：表上三列都不含 $B\cdot T$，8k SFT 要 checkpoint 或 SP。把这两问挡住，分档就讲清楚了。和「除了 DeepSpeed」连问时，升 3 只是内存层的一档，不是训练优化的全集。

把表讲给人听时，用手指出「刚被切开的那一列」：从 DP 到 1 切的是优化器，从 1 到 2 切的是梯度，从 2 到 3 切的是参数。每一刀都换一类通信，所以不是免费的。7B 常常切一刀就够，72B 全参必须切到参数或把模型用 TP 切开。LoRA 把优化器那一列变小，可能让你停在 1 甚至不分。面试被追「最佳实践」时拒绝给唯一答案，改口「取决于哪一列还在爆」。爆 Adam 升 1，爆梯度峰值升 2，单卡放不下权重才升 3，爆激活则不要升 ZeRO。和混元「除了 DeepSpeed」连问时强调：这张表只覆盖状态分片，FlashAttention、checkpoint、序列并行、LoRA 都不在三列里。把表外的手段说成 ZeRO-4，当场穿帮。准备时用 7B / 13B / 72B 三个规模各举一次「停在哪一档」，比背定义更像训过。小模型小 batch 升 3 会让 MFU 掉，要主动承认「更省稳态、更亏吞吐」。长序列升 3 仍 OOM，要主动改口去 checkpoint。两句挡掉最常见的追问，这张表就算讲完了。

## 追问

- **ZeRO-1 为什么常常够？** 优化器是 12 bytes/param 量级，切掉它，参数仍复制、前向干净。7B 全参在 8×80GB 上经常 1 就够。
- **升 3 一定更省吗？** 稳态占用省，峰值有 all-gather；小模型 / 小 batch 更慢。省的是复制的参数，不是激活。
- **和 TP 怎么叠？** TP 切矩阵和激活，ZeRO 切 DP 维状态。72B 常见 TP + ZeRO-1/2，而不是只靠 3。
- **FSDP 对应哪一档？** `fully_shard` ≈ ZeRO-3；`shard_grad_op` ≈ ZeRO-2。名字不同，分的东西同类。
- **activation 谁来切？** 不是 ZeRO。checkpoint、序列并行、减 micro-batch。升 3 解决不了 8k SFT 的激活。
- **LoRA 72B 还要 3 吗？** 常常不要。优化器只挂 adapter，底座冻结。这是「除了 DeepSpeed」那题里微调更划算的原因。
- **和 72B 估算怎么衔接？** 先画这张表，再代入 $N$、$D$、是否 LoRA，见 `tencent-zero3-qwen72b-mem`。不要先报 GB。
- **口诀？** 1 救 Adam，2 削梯度，3 动参数并开始按层通信。能停就停，跳级是为了「用过」不是为了快。
- **为什么升 3 还可能 OOM？** 激活和 all-gather 峰值不在表里。长序列要 checkpoint / SP，不是再找一个 ZeRO-4。

- **7B / 13B / 72B 各停哪一档？** 7B 全参在 8×80GB 上常常 1 就够；13B–32B 看序列，2 是甜点；72B 全参必须 3 或把 $N$ 用 TP 切开。LoRA 把档位整体降一档。举三个规模比背定义更像训过。
- **什么叫「表外的手段」？** FlashAttention、checkpoint、SP、LoRA 都不在参数/梯度/优化器三列里。把它们说成 ZeRO-4，分档就讲穿了。
- **为什么拒绝给「最佳实践」？** 取决于哪一列还在爆。爆 Adam 升 1，爆梯度峰值升 2，放不下权重升 3，爆激活去 checkpoint。唯一答案一定会被改规模打穿。
- **和小模型升 3 为什么会更慢？** 每层 all-gather 在计算喂不饱时占比上升，稳态占用降了，step time 却变长。要主动承认「更省稳态、更亏吞吐」，不要把升档当成单调变好。
- **本卡和估算卡怎么分工？** 本卡把列切对，估算卡把 $N$ 和 $D$ 代进去。不要在本卡报 GB。
- **口诀再收一次？** 1 救 Adam，2 削梯度，3 动参数并开始按层通信。能停就停。激活不在表上，长序列去 checkpoint，不要找 ZeRO-4。
- **先画表再代入。** 和 72B 估算连问时不要先报 GB。

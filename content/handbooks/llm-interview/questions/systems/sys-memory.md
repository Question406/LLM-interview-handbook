---
id: sys-memory
section: systems
order: 3
level: S
title: Adam 训练一个 7B 模型为什么远不止 14GB？
quick: >-
  BF16 参数 2 bytes/param 只是权重本身。训练还要存梯度、FP32 master、Adam m/v，以及 activation
  与临时 buffer。经典 mixed-precision Adam 的参数状态约 16 bytes/param，$7\mathrm{B}$ 量级约
  $112\,\mathrm{GB}$，还没算 activation。ZeRO/FSDP 分的是状态，不是激活。
tags:
  - Memory
  - Optimizer
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: 'ZeRO: Memory Optimizations Toward Training Trillion Parameter Models'
    url: https://arxiv.org/abs/1910.02054
    type: primary
---

白板陷阱是把「$7\mathrm{B}\times 2\,\mathrm{B}=14\,\mathrm{GB}$」当成训练显存。那只是一份 BF16 权重，推理或冻结前向才够。Adam 训练要把**参数副本、梯度、优化器状态**和 **activation** 分开列，数字才能对上。

## 1. 先按 bytes/param 拆参数状态

经典 mixed-precision Adam（BF16 算、FP32 更新）常见五份：

| 张量 | dtype | bytes/param | 作用 |
| --- | --- | --- | --- |
| 计算用参数 | BF16 | $2$ | 前向 / 反向里的 $W$ |
| 梯度 | BF16 | $2$ | $\nabla W$；有的实现是 FP32 则改 $4$ |
| FP32 master weights | FP32 | $4$ | 小学习率下累加更新，避免 BF16 抹掉增量 |
| Adam 一阶矩 $m$ | FP32 | $4$ | 梯度指数滑动平均 |
| Adam 二阶矩 $v$ | FP32 | $4$ | 梯度平方的滑动平均 |

相加：$2+2+4+4+4=16$ bytes/param。若梯度走 FP32、或没有 master、或 fused Adam 把 master 与 $m/v$ 叠在一起，总数会落到约 $12$–$18$。不要背死「永远 16」，要能指出**哪一份可以省、哪一份不能省**。

对 $7\times 10^9$ 参数：

$$
7\times 10^9 \times 16\,\mathrm{B} \approx 112\,\mathrm{GB}.
$$

这只是**未分片**时参数侧的量级：一张 80GB 卡装不下完整 Adam 状态。LoRA 只训低秩矩阵时，这份账按可训练参数算，底座仍可能占一份 BF16。

## 2. Activation 是另一本账

Activation 与 `batch`、序列长 $T$、`hidden`、层数、是否重算成正比，**不是** $16$ bytes/param 的一部分。Attention 中间量大致随 $B\cdot T\cdot d$ 或 $B\cdot H\cdot T^2$ 涨；长上下文时它会反超参数状态。

Activation checkpointing（gradient checkpointing）用重算换显存：只留若干层边界，反向时重做前向。序列并行 / 上下文并行再把 $T$ 切开。面试若只答「用 ZeRO」却不提 activation，长序列一上来仍会 OOM。

临时通信 buffer、softmax 工作区、MoE dispatch 缓冲也要另计，峰值往往高于「稳态占用」。

## 3. ZeRO / FSDP 分的是哪几份

ZeRO 针对的是上一节的参数 / 梯度 / optimizer，不是 activation：

1. **ZeRO-1**：只切 $m,v$（以及 master）。每卡参数与梯度仍完整，通信主要在 step 时。
2. **ZeRO-2**：再切梯度。反向一边 reduce-scatter，一边释放。
3. **ZeRO-3 / FSDP**：再切参数。前向 / 反向按层 all-gather，用完丢掉。单卡参数占用约除以卡数，但集体通信变重。

$7\mathrm{B}$ 在 8 卡 ZeRO-3 上，参数状态可落到十几 GB/卡量级，**activation 仍按本地 micro-batch 全量存在**。所以还要叠 TP（切隐层矩阵）、PP（切层）、CP（切序列）和 checkpoint。

口诀：**14GB 是权重；112GB 是未分片 Adam 状态；真正 OOM 经常是 activation 或通信缓冲。**

## 追问

- **没有 FP32 master 行不行？** 可以纯 BF16 Adam，状态少 $4$ bytes/param，但小 $\eta$ 下更新可能被舍入吃掉，大模型少见。
- **ZeRO-3 为什么有时更慢？** 每层 gather 参数，算力没喂饱时通信占比上升；小模型 / 小 batch 更明显。
- **推理 7B 为什么远小于 14GB 的「训练直觉」？** 推理无 grad / Adam，还可量化；但 decode 另有一份随 $T$ 涨的 KV Cache。

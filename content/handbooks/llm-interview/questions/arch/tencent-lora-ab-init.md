---
id: tencent-lora-ab-init
section: arch
order: 200
level: A
title: 腾讯混元：LoRA 的 A/B 矩阵如何初始化？还有哪些初始化？
quick: >-
  常见做法：$A$ 高斯随机、$B$ 全零，使训练开始时 $\Delta W=BA=0$，不破坏预训练输出。也可用 Kaiming
  等初始化 $A$，或探讨 PiSSA / 正交初始化等变体，但面试先把“零起步残差”讲清楚。
tags:
  - Tencent
  - Hunyuan
  - LoRA
  - 2025-2026
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 腾讯-混元大模型面经
    url: https://www.nowcoder.com/feed/main/detail/19561cb3bcbf4a519766f61d6414a44c
    type: candidate-first-hand
  - title: LoRA
    url: https://arxiv.org/abs/2106.09685
    type: primary
---

## 真题记录

- 公司：腾讯 · 混元
- 原始措辞：**“知道 LoRA 的原理吗，A 和 B 两个矩阵怎么初始化，有了解过其他的初始化方法吗”**

陷阱是两边都全零（适配器冻死）或两边都随机（第一步就扰动基座）。LoRA 要的是 **零起步残差**：$\Delta W$ 初始为 0，前向等于预训练，同时至少一侧非零才能把梯度送进另一侧。挂载点见 `sensetime-lora-where`、`meituan-lora-not-after-ln`；本题聚焦初始化。快手同构题见 `kuaishou-lora-ab-init`。

## 标准：$A$ 随机、$B$ 全零

$$
W'=W+\frac{\alpha}{r}BA,\qquad B\in\mathbb{R}^{d\times r},\; A\in\mathbb{R}^{r\times k}.
$$

常见实现：$A$ 高斯或 Kaiming，$B$ 全零（PEFT 默认）。则 $BA=0$，起步不改输出。梯度 $\partial L/\partial B \propto (\partial L/\partial\Delta W)A^\top$，$A$ 非零所以 $B$ 能被拉离原点；之后 $\Delta W$ 才非零。对调「$B$ 随机 $A$ 全零」在乘积为零的意义上也可，但梯度路径对偶，框架里不常见。$\alpha/r$ 是有效步长，改 $r$ 时要一起说 $\alpha$，见 `arch-lora`。

**两边都全零**：$BA=0$ 且 $\partial L/\partial A$、$\partial L/\partial B$ 都乘到零侧，适配器学不到东西。**两边都随机**：第一步就改变基座行为，loss 尖刺，破坏「从原模型出发」的假设。这不是风格问题，是残差分支的可启动性。

## 其他初始化：了解即可，稳定优先

面试官问「还有哪些」时，点名即可，不要假装都实现过：

- **PiSSA / 主成分**：用 $W$ 的主奇异方向初始化 $A,B$，让适配器从「已有重要子空间」起步，收敛有时更快，但不再严格 $\Delta W=0$，要接受起步就微扰。
- **正交 / 谱**：约束 $A$ 行正交，改善初期条件数。
- **自适应秩 / AdaLoRA**：训练中改有效秩，不是初始化本身，但常被连问。

重点仍是：能否 merge 回 $W$、多 adapter 路由、以及和量化（QLoRA）共存时的数值，见 `arch-qlora`。rank 过大易过拟合且显存升；过小欠拟合。混元若追「和全参比」，落到数据量与可回滚，见 `tencent-lora-vs-full-exp`。

## 追问

- **为什么不能 $A=B=0$？** 前向是 0，两边梯度常因乘零消失，等于没插适配器。必须一侧随机提供非零方向。
- **Kaiming 和正态差在哪？** 都是让 $A$ 有尺度合理的随机方向；$B=0$ 才是零残差的关键。不要把初始化分布说成算法本体。
- **PiSSA 还算 LoRA 吗？** 还是 $BA$ 低秩，但起步 $\Delta W\neq 0$。要报「牺牲零起步换更快对齐主方向」。
- **merge 后对不齐？** 查 $\alpha/r$、是否重复 merge、dtype、是否在错误模块上挂了过大 lr。见美团卡 `meituan-lora-not-after-ln`。
- **插哪？** 通常 q/k/v/o 与 MLP Linear，不插 LayerNorm。本题若已被问初始化，挂载点一句话带过即可。

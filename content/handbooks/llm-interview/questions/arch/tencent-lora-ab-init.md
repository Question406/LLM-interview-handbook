---
id: tencent-lora-ab-init
section: arch
order: 200
level: A
title: 腾讯混元：LoRA 的 A/B 矩阵如何初始化？还有哪些初始化？
quick: 假设要调整一个很大的线性层，但希望只训练少量参数。LoRA 不直接训练整张 weight matrix，而是用两个较小矩阵的乘积表示更新。
tags:
  - Tencent
  - Hunyuan
  - LoRA
  - 2025-2026
  - 口述改写 2026-10-28
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: 腾讯-混元大模型面经
    url: 'https://www.nowcoder.com/feed/main/detail/19561cb3bcbf4a519766f61d6414a44c'
    type: candidate-first-hand
  - title: LoRA
    url: 'https://arxiv.org/abs/2106.09685'
    type: primary
---

## 回答思路

> **问题与场景：** 假设要调整一个很大的线性层，但希望只训练少量参数。
>
> **做法与原因：** 常见初始化是一边随机、一边为零，使初始更新为零，保留原模型输出，同时让非零那一边为另一边提供初始 gradient。
>
> **检查与取舍：** Low rank 是对更新结构的约束，不是说原权重本身一定 low rank。

## 可以这样回答

假设要调整一个很大的线性层，但希望只训练少量参数。LoRA 不直接训练整张 weight matrix，而是用两个较小矩阵的乘积表示更新。

常见初始化是一边随机、一边为零，使初始更新为零，保留原模型输出，同时让非零那一边为另一边提供初始 gradient。若两边都为零，普通乘积参数化下双方最初的 gradients 都可能为零。

Low rank 是对更新结构的约束，不是说原权重本身一定 low rank。我会比较不同 rank 的任务表现、训练成本和部署方式。

## 技术备查

## 真题记录

- 公司：腾讯 · 混元
- 原始措辞：**“知道 LoRA 的原理吗，A 和 B 两个矩阵怎么初始化，有了解过其他的初始化方法吗”**

标准做法是 $A$ 随机、$B$ 全零。LoRA 要的是零起步残差：$\Delta W$ 一开始为 0，前向和预训练模型一样；同时至少有一侧非零，梯度才能传进另一侧。两边都全零，适配器学不到东西；两边都随机，第一步就扰动了基座。别的初始化方法我会点名 PiSSA、正交初始化，再顺带提 AdaLoRA。挂载点见 `sensetime-lora-where`、`meituan-lora-not-after-ln`，快手的同类题见 `kuaishou-lora-ab-init`，这里只讲初始化。

## 标准做法：$A$ 随机、$B$ 全零

$$
W'=W+\frac{\alpha}{r}BA,\qquad B\in\mathbb{R}^{d\times r},\; A\in\mathbb{R}^{r\times k}.
$$

常见实现里，$A$ 用高斯或 Kaiming，$B$ 全零（PEFT 默认就是这样）。这时 $BA=0$，起步不改变输出。梯度 $\partial L/\partial B \propto (\partial L/\partial\Delta W)A^\top$，$A$ 非零，所以 $B$ 能被拉离原点，之后 $\Delta W$ 才开始非零。反过来「$B$ 随机、$A$ 全零」，乘积同样为零，也可以，只是梯度路径对偶过来，框架里不常见。$\alpha/r$ 是有效步长，改 $r$ 时要一起交代 $\alpha$，见 `arch-lora`。

两边都全零时，$BA=0$，$\partial L/\partial A$ 和 $\partial L/\partial B$ 又都乘到了为零的那一侧，适配器学不到东西。两边都随机，第一步就改变了基座的行为，loss 可能突然升高，「从原模型出发」的前提也被破坏了。这是残差分支能不能启动的问题，和风格偏好无关。

## 其他初始化：知道就行，稳定优先

面试官问「还有哪些」时，点名就够了，别假装都实现过。PiSSA 用 $W$ 的主奇异方向初始化 $A,B$，让适配器从「已有的重要子空间」起步，有时收敛更快，但起步就不再严格满足 $\Delta W=0$，要接受一开始就有微扰。正交 / 谱初始化约束 $A$ 的行正交，改善训练初期的条件数。AdaLoRA 这类自适应秩的方法在训练中调整有效秩，本身不算初始化，但常被连着问。

重点仍然是能不能 merge 回 $W$、多个 adapter 怎么路由，以及和量化（QLoRA）共存时的数值，见 `arch-qlora`。rank 过大容易 overfitting，显存也上去；过小又会 underfitting。混元如果追问「和全参比怎么样」，就落到数据量和能不能回滚上，见 `tencent-lora-vs-full-exp`。

## 追问

**为什么不能 $A=B=0$？**
前向输出是 0，两边的梯度又都因为乘到零而消失，等于没插适配器。必须有一侧随机，提供非零的方向。

**Kaiming 和正态分布差在哪？**
两者都是让 $A$ 有一个尺度合理的随机方向；零残差的关键在 $B=0$。别把初始化的分布说成算法本体。

**PiSSA 还算 LoRA 吗？**
算，还是 $BA$ 低秩，只是起步时 $\Delta W\neq 0$。要说清它是「牺牲零起步，换来更快对齐主方向」。

**merge 之后数值对不齐怎么办？**
查 $\alpha/r$、是否重复 merge、dtype，以及是不是在错误的模块上挂了过大的 lr，见美团那张卡 `meituan-lora-not-after-ln`。

**挂在哪？**
通常是 q/k/v/o 和 MLP 的 Linear，不插 LayerNorm。这题主要问初始化，挂载点一句话带过就行。

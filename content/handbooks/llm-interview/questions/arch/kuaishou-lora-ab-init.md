---
id: kuaishou-lora-ab-init
section: arch
order: 121
level: A
title: 快手：LoRA 的 A/B 矩阵一般怎么初始化，能否都全零？
quick: >-
  标准做法是 $A$ 高斯或 Kaiming、$B$ 全零，保证训练起点等于原权重。两矩阵都全零则更新恒为
  0，低秩适配器学不到东西；$A$、$B$ 都随机则起步就扰动基座，容易不稳。
tags:
  - Kuaishou
  - LoRA
  - Initialization
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 快手大模型算法二面-实习面经
    url: https://www.nowcoder.com/feed/main/detail/ca3fe5949e0b4ddbb7807e43380ab7a6
    type: candidate-first-hand
  - title: LoRA
    url: https://arxiv.org/abs/2106.09685
    type: primary-paper
---

## 真题记录

- 公司：快手
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习；二面
- 面试时间：原帖未披露；帖子发布于 2026-01-08
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“讲一下 LoRA ，两个权重矩阵一般怎么初始化，能都全0吗”**

常见误区是：只记得「一边随机一边为零」，说不清为什么两边不能都零、也不能都随机。LoRA 把更新写成

$$
W'=W+\frac{\alpha}{r}BA,
$$

训练开始时应有 $\Delta W=0$，前向与原模型一致，只在微调过程中注入低秩方向。这和基座用不用 SwiGLU、RoPE、MoE 无关：挂的是线性层 $W$，不是 Norm 或旋转。

## 标准初始化

常见实现：$A\in\mathbb{R}^{r\times k}$ 用高斯 / Kaiming，$B\in\mathbb{R}^{d\times r}$ 全零（或反过来保持乘积为零）。前向 $\Delta W=0$，但对非零侧的梯度可以从 损失（loss） 回传，$B$ 被拉离零点后 $\Delta W$ 才非零。$\alpha/r$ 相当于步长缩放，$r$ 过小欠拟合、过大接近全参扰动。

两边都随机：第一步就改变基座行为，初始 loss 可能突然升高，也破坏「从原模型出发」的假设。对已经校准过的 RMSNorm 后激活尤其危险。
## 为什么不能都全零

$B=0,A=0$ 时前向是 $0$。链式法则里 $\partial\mathcal{L}/\partial A$ 含 $B$ 的因子，$\partial\mathcal{L}/\partial B$ 含 $A$ 的因子，两侧都零则梯度也常为零，适配器无法更新，等于没有训练。这是乘积结构的死区，不是实现 bug。少数变体用正交或谱初始化，但仍会保证起步 $\Delta W\approx 0$。

合并权重后应做一次和未合并推理的数值对齐；$\alpha/r$、重复 merge、dtype 是合并后数值异常的常见原因，见 `meituan-lora-not-after-ln`。

## 追问

- **$A$ 零 $B$ 随机可以吗？** 乘积仍可为零，但哪一侧接输入会影响梯度尺度；跟框架默认走，不要自己对调完不验 loss。
- **QLoRA 初始化一样吗？** 一样。变的是冻结 $W$ 用 NF4 存，不是 $A/B$ 的零点约定。
- **挂在 MoE 专家上要注意什么？** 每个专家一份 $A,B$，冷专家更新少，看起来像「没训」，其实是路由没点到。

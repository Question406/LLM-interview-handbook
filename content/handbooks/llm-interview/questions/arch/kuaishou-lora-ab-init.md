---
id: kuaishou-lora-ab-init
section: arch
order: 121
level: A
title: 快手：LoRA 的 A/B 矩阵一般怎么初始化，能否都全零？
quick: 假设要调整一个很大的线性层，但希望只训练少量参数。LoRA 不直接训练整张 weight matrix，而是用两个较小矩阵的乘积表示更新。
tags:
  - Kuaishou
  - LoRA
  - Initialization
  - 口述改写 2026-10-28
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: 快手大模型算法二面-实习面经
    url: 'https://www.nowcoder.com/feed/main/detail/ca3fe5949e0b4ddbb7807e43380ab7a6'
    type: candidate-first-hand
  - title: LoRA
    url: 'https://arxiv.org/abs/2106.09685'
    type: primary-paper
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

- 公司：快手
- 团队 / 岗位：大模型算法实习
- 届别 / 流程：实习；二面
- 面试时间：原帖未披露；帖子发布于 2026-01-08
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“讲一下 LoRA ，两个权重矩阵一般怎么初始化，能都全0吗”**

一般是 $A$ 随机、$B$ 全零，两边不能都是零，也不建议都随机。LoRA 把更新写成

$$
W'=W+\frac{\alpha}{r}BA,
$$

训练开始时要有 $\Delta W=0$，前向和原模型一致，低秩方向在微调过程中再慢慢注入。两边都零，适配器学不动；两边都随机，起点就偏离了原模型。这跟基座用不用 SwiGLU、RoPE、MoE 无关，LoRA 挂的是线性层 $W$，不碰 Norm，也不碰旋转。

## 标准初始化

常见实现里，$A\in\mathbb{R}^{r\times k}$ 用高斯 / Kaiming，$B\in\mathbb{R}^{d\times r}$ 全零（或者反过来，只要乘积为零）。前向时 $\Delta W=0$，但非零那一侧的梯度可以从损失（loss）回传，$B$ 被拉离零点之后，$\Delta W$ 才开始非零。$\alpha/r$ 相当于步长缩放；$r$ 太小会 underfitting，太大就接近全参扰动。

## 为什么不能都全零

$B=0,A=0$ 时前向输出是 $0$。按链式法则，$\partial\mathcal{L}/\partial A$ 里有 $B$ 的因子，$\partial\mathcal{L}/\partial B$ 里有 $A$ 的因子，两边都是零，梯度通常也是零，适配器根本更新不了，等于没训。这是乘积结构自带的死区，和实现 bug 无关。少数变体会用正交或谱初始化，但仍会保证起步时 $\Delta W\approx 0$。

两边都随机也有问题：第一步就改变了基座的行为，初始 loss 可能突然升高，也破坏了「从原模型出发」这个前提。对已经 calibration 过的 RMSNorm 后激活来说尤其危险。

训完合并权重时，要拿合并后和未合并的推理结果做一次数值对齐。合并后数值异常，常见原因是 $\alpha/r$、重复 merge 和 dtype，见 `meituan-lora-not-after-ln`。

## 追问

**$A$ 全零、$B$ 随机可以吗？**
乘积同样是零，可以。但哪一侧接输入会影响梯度的尺度，跟框架默认走就好，自己对调了要验一下 loss。

**QLoRA 的初始化一样吗？**
一样。变的是冻结的 $W$ 用 NF4 存，$A/B$ 的零点约定不变。

**挂在 MoE 专家上要注意什么？**
每个专家各有一份 $A,B$。冷门专家更新得少，看上去像「没训」，其实是路由没点到它。

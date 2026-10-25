---
id: meituan-attention-scale-dk
section: fundamentals
order: 140
level: A
title: 美团：Attention 为什么要除以 $\sqrt{d_k}$？
quick: "除以 $\\sqrt{d_k}$ 是为了数值稳定：$QK^\\top$ 每个元素的方差随 $d_k$ 线性增大，不缩放时 softmax 进入饱和区，梯度几乎消失。除 $\\sqrt{d_k}$ 把点积标准差拉回常数级，训练才稳，张量的维度一个都没删。"
tags:
  - Meituan
  - Attention
  - Softmax
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 美团大模型算法岗完整面经（一面+二面）
    url: https://www.nowcoder.com/feed/main/detail/b264abf14d4d4c44bc022c9ea1dce981
    type: candidate-first-hand
  - title: Attention Is All You Need
    url: https://arxiv.org/abs/1706.03762
    type: primary-paper
---

## 真题记录

- 公司：美团
- 团队 / 岗位：大模型算法
- 届别 / 流程：原帖未披露；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：“Attention机制中为什么需要去除DK相关计算维度，核心作用是什么？”

除以 $\sqrt{d_k}$ 是为了数值稳定：$q\cdot k$ 的方差随维度 $d_k$ 线性增长，不缩放的话点积很大，softmax 被推进饱和区，梯度几乎消失。原帖说的「去除 $d_k$ 相关计算维度」，意思是用 $d_k$ 做缩放因子，张量里哪一轴都没删。光背「除一下比较好」不够，面试官要听你把方差推出来。

## 方差怎么推

设 $q,k\in\mathbb{R}^{d_k}$，各维独立、均值为 $0$、方差约 $1$，则

$$
\mathrm{Var}(q\cdot k)=\mathrm{Var}\Big(\sum_{i=1}^{d_k}q_i k_i\Big)=d_k,
$$

标准差约 $\sqrt{d_k}$。$d_k$ 到 $64$ 或 $128$ 时，点积的绝对值经常很大。Softmax $e^{z_i}/\sum e^{z_j}$ 在 $z$ 差距大时接近 one-hot：最大项概率 $\approx 1$，其余 $\approx 0$，对非最大 key 的梯度几乎为 $0$，叠了多层以后很难学到均匀一些的对齐。除以 $\sqrt{d_k}$ 后点积方差回到 $O(1)$，注意力还能在多个 key 之间分配质量。

不缩放会怎样也可以说具体：深层的注意力迅速变成 one-hot，残差学到的几乎是离散路由，梯度穿过 softmax 变得极小，训练表现为 loss 难以下降，或者对位置极敏感。这是优化问题，光用 fp16 overflow 解释不了。

它和温度 $T$ 是一类东西。$\mathrm{softmax}(z/T)$ 里 $T$ 变大等价于压平分布，$\sqrt{d_k}$ 相当于按维度选好的固定温度，不是训练超参。QK-Norm 把 $q,k$ 先拉回单位尺度，是同一家族的稳定手段，可以和除 $\sqrt{d_k}$ 并存。

## 白板和实现

手写时写 `q @ k.T / math.sqrt(d_k)`（`pdd-attention-handwrite`）。Multi-head 里每个 head 的 $d_k=d_{\mathrm{model}}/h$，缩放用的是 head 维度，拿 $d_{\mathrm{model}}$ 做分母就错了。实现里常见写法是 `scores = q @ k.transpose(-2,-1) * (d_k ** -0.5)`，也有人把系数预计算进 $W_Q$ 的初始化，效果等价，但白板上仍应写出除 $\sqrt{d_k}$。拼多多也常问同一点，公式要能在白板上推出来。

FlashAttention 用 online softmax 减显存，数学上仍是同一个 $\mathrm{softmax}(QK^\top/\sqrt{d_k})$，内核融合没有省掉这个除法（`ant-flash-attention`）。

最常见的三种错答是：把缩放说成「除一下让数值变小好看」；用 $d_{\mathrm{model}}$ 做分母；以为 FlashAttention 可以省略缩放。

## 追问

**不除会怎样？**
Softmax 变尖、梯度消失、深层对齐学不成。单纯的 overflow 解释不了这个现象。

**和温度、QK-Norm 什么关系？**
都在管点积进入 softmax 之前的尺度。温度是推理旋钮，缩放是结构常数。

**分母用 $d_k$ 还是 $d_{\mathrm{model}}$？**
用 $d_k$。每个 head 的点积维度是 $d_k$。

**FlashAttention 还要除吗？**
要。它加速的是实现，公式没变。

**原帖说「去除维度」，怎么圆？**
说成用 $d_k$ 缩放、没有删轴，再补一句方差推导，比争用词更稳。

相关：`baichuan-attn-vs-selfattn`（QKV 从哪来）、`ali-attention-math`（矩阵形状）、`fund-softmax-nll`（softmax 饱和）。

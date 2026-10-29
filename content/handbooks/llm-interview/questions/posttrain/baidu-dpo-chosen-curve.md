---
id: baidu-dpo-chosen-curve
section: posttrain
order: 205
level: A
title: 百度文心：DPO 对齐训练曲线长什么样？正例概率一定会上升吗？
quick: 假设一对回答里 A 比 B 好。DPO 要让 A 相对 B、相对 reference 的优势增加，不是单独最大化 A 的绝对概率。
tags:
  - Baidu
  - DPO
  - 2025-2026
  - 口述改写 2026-10-28
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: 腾讯/百度/minimax 大模型算法面经总结帖
    url: 'https://www.nowcoder.com/feed/main/detail/8cab51ef9458459595cf81fda43da279'
    type: candidate-first-hand
  - title: Direct Preference Optimization
    url: 'https://arxiv.org/abs/2305.18290'
    type: primary
---

## 回答思路

> **问题与场景：** 假设一对回答里 A 比 B 好。
>
> **做法与原因：** 因此 A 和 B 的概率都下降，但 B 降得更多，也可能让这一对的 loss 变小。
>
> **检查与取舍：** 我会一起检查 chosen/rejected 的相对变化、loss、生成质量和能力保留。

## 可以这样回答

假设一对回答里 A 比 B 好。DPO 要让 A 相对 B、相对 reference 的优势增加，不是单独最大化 A 的绝对概率。

因此 A 和 B 的概率都下降，但 B 降得更多，也可能让这一对的 loss 变小。仅看 chosen probability 下降，不能立刻认定训练实现错了。

我会一起检查 chosen/rejected 的相对变化、loss、生成质量和能力保留。如果相对排序改善却真实回答变差，还要检查数据分布与过度优化。

## 技术备查

## 真题记录

- 公司：百度 · 文心一言（总结帖收录）
- 原始措辞：**“DPO 对齐训练的曲线是怎么样的，正例的概率会提升吗？”**

不一定会上升。DPO 的损失只看 chosen 和 rejected 之间的间隔，正例的 $\log\pi(y_w)$ 可以和负例一起往下走，只要间隔在拉大、胜率在涨，这条曲线就可能是健康的。

容易出错的地方是拿 SFT 的眼光读 DPO 曲线，以为 chosen 的似然必须单调上升，一降就是训练失败。DPO 是从 reverse KL 约束下的最优策略反解出来的，允许概率质量整体搬家，见 `fund-kl-directions`。所以现场我先写间隔公式，再说要同时画四条曲线：margin、chosen/rejected 的绝对 logp、平均长度、对 ref 的 KL。只报一条「正例概率」，追问一下就站不住。

核心项是

$$
\Delta=\beta\log\frac{\pi_\theta(y_w\mid x)}{\pi_{\mathrm{ref}}(y_w\mid x)}-\beta\log\frac{\pi_\theta(y_l\mid x)}{\pi_{\mathrm{ref}}(y_l\mid x)},
$$

损失 $\mathcal{L}=-\log\sigma(\Delta)$。梯度鼓励拉大 $\Delta$，不保证 $\pi(y_w)$ 上升，更不保证它比 SFT 时高。常见的健康现象是：chosen 和 rejected 的绝对 log-prob 一起降，但 $\Delta$ 在升、离线胜率在升、对 ref 的 reverse KL 缓慢上升。这就是 mode-seeking，两边都让出一点质量，间隔拉开了，这比「正例越来越像 SFT」常见得多。$\beta$ 大，$\Delta$ 难拉开，更贴 ref；$\beta$ 小，间隔涨得快，KL 也涨得快。

病态曲线也要能认出来，常见有三种。只压 $y_l$、不抬 $y_w$ 的质量，间隔被刷大了，用户侧观感没变。靠拉长回答堆总 logp，长度和 $\Delta$ 一起涨，这是长度 bias。overfitting 偏好噪声，离线胜率涨了，线上或留出集变差。这三种都不是一句「正例概率没升」能概括的。

所以监控要同时画 $\Delta$、chosen/rejected 的平均 logp、平均长度、重复 n-gram、$D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$ 和下游 winrate。KL 的方向仍是反向，别改成对 ref 的 cross entropy loss（CE），否则曲线的含义全变了，见 `ant-kl-vs-ce`。回答过长可以用长度归一、SimPO、显式长度惩罚，或者在标注时写明「短而对优于长而对」，见 `baidu-simpo-vs-dpo-length`。光加 $\beta$ 不行，$\beta$ 管的是贴 ref 的幅度，不直接控制 token 数。后面如果切到 GRPO，间隔健康也不代表有效组够：组内全是「长而对」时，优势照样可能塌成零，或者被长度尾巴拽走，见 `sys-rl-group-n`。

## 追问

**正例 logp 下降，是不是训废了？**
不一定。看 $\Delta$、KL 和 holdout 胜率，三个一起掉才是崩；只掉绝对 logp 可能是健康的 seeking。

**和 SFT 的曲线差在哪？**
SFT 的正向 CE 会推高示范的似然，DPO 可以两边一起降。按 SFT 的标准读 DPO 曲线，会把健康的 run 误杀。

**过长怎么缓解？**
平均 logp、SimPO、长度惩罚或者控长标注。只加 $\beta$ 或只加学习率都没用。

**要不要做 online DPO？**
线上分布漂了就该刷新 pair。那已经接近偏好版的 on-policy，算力账又回到了 RL，不再是「再训一晚 DPO」。

**rejected 也在降，会不会把有用的说法一起忘掉？**
会。硬负样本要覆盖「看着像对的错法」，别拿随机垃圾当 $y_l$，不然模型很容易拉大间隔，却可能丢掉有用的能力。

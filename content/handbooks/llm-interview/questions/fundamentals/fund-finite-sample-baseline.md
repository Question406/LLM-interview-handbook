---
id: fund-finite-sample-baseline
section: fundamentals
order: 148
level: S
title: 组均值含当前样本、Leave-one-out、batch 标准化，有限样本下谁还无偏？
quick: "只有 leave-one-out 是严格无偏的，因为无偏要求 baseline 不依赖当前样本。组均值含 $r_i$，会把优势缩成 $(G-1)/G$ 倍；RLOO 只用其余 $G-1$ 条算 baseline；batch 均值的偏差随 batch 变大而消失，但除 $\\sigma$ 不管在组内还是全局都在改权重。"
tags:
  - RL
  - Baseline
  - GRPO
  - RLOO
  - Bias-Variance
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Back to Basics — REINFORCE Leave-One-Out (RLOO)
    url: https://arxiv.org/abs/2402.14740
    type: primary
  - title: DeepSeekMath / GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
  - title: REINFORCE++
    url: https://arxiv.org/abs/2501.03262
    type: secondary
---
严格无偏的只有 leave-one-out（RLOO）。恒等式 $\mathbb{E}_a[\nabla\log\pi\,b(s)]=0$ 里的 $b(s)$ 不能是当前这条 $a$ 的函数，而有限样本里，组均值、batch 均值、组标准差都「看见」了当前的 $r_i$，所以「减了均值就无偏」不能直接从期望公式搬到大小为 $G$ 的一组样本上，得重新算。和 `pt-rloo-vs-grpo` 的区别是，那题比算法选型，这题只解释有限样本偏差从哪来。

## 组均值含自身：偏差是 $1/G$

对同一输入提示采样 $G$ 条回答，得到 $r_1,\ldots,r_G$。GRPO 常用

$$
\bar r=\frac{1}{G}\sum_{j=1}^G r_j,\qquad \hat A_i=r_i-\bar r=\frac{G-1}{G}\Big(r_i-\frac{1}{G-1}\sum_{j\neq i}r_j\Big).
$$

$\bar r$ 里含着 $r_i$，等于先对 leave-one-out 中心化，再把优势乘上 $(G-1)/G$。$G=2$ 时收缩最明显，两条的优势是 $\pm(r_1-r_2)/2$，幅度减半。$G\to\infty$ 时它和真正的 $b(s)=\mathbb{E}[r\mid s]$ 一致，偏差消失，所以「GRPO 无偏」只在大组极限下近似成立。全对 / 全错时 $\hat A=0$，那是组内没有相对信号，跟偏差无关，见 `pt-grpo-variance`。

## RLOO：当前样本不进 $b$

$$
b_i=\frac{1}{G-1}\sum_{j\neq i}r_j,\qquad \hat A_i=r_i-b_i.
$$

给定其余样本，$b_i$ 和当前动作独立，是 REINFORCE control variate 的有限样本版：期望上不改梯度，只降方差。$G=2$ 时优势就是两条之差，没有 $(G-1)/G$ 的收缩。RLOO 通常也不再除组 $\sigma$，尺度保持原始奖励分数（reward）的尺度；跨题幅度不可比，但不会因为「这题大家都差不多对」就把微小分差放大。

白板上用 $G=2$、$r=(1,0)$ 走一遍最清楚：GRPO 得到 $A=(+0.5,-0.5)$（如果再除 $\sigma$ 还会再缩放），RLOO 得到 $A=(+1,-1)$。能说清「含不含自身」，比背论文名字重要。

## Batch 标准化：偏差随 batch 消失，除 $\sigma$ 另算

REINFORCE++ 一类做法把 baseline 换成全局 batch 均值，可选地再除全局 $\sigma$。相比输入提示（prompt）级的小 $G$，batch 往往大几十倍，$O(1/N)$ 的偏差可以忽略，论文因此说「effective unbiased」。它解决的是「别在 8 条样本里估 $\sigma$」，并没有证明除标准差是无偏的。

除 $\sigma$ 不管在组内还是全局，都是依赖数据的重加权：方差小的切片有效学习率变大。Dr.GRPO 批评的 question-level reweighting 就是组内这一层，见 `pt-drgrpo`、`fund-adv-norm-bias`。全局 $\sigma$ 把不同输入提示的样本放在同一个尺度下，偏差的形式不一样：不再按题放大，但 batch 组成一变，同一条轨迹的 $A$ 含义就跟着变。归纳一下，减均值（常数 baseline）还在无偏族里，除 $\sigma$ 是在改目标。

## 追问

**$G$ 多大可以当作无偏？**
没有魔法数。$G=8$ 时 $(G-1)/G=0.875$，幅度偏差已经不大；更伤的是再除以一个噪声很大的 $\sigma$，以及零方差组。加大 $G$ 降的是 baseline 的方差，几乎不改目标，往往比把 $\lambda$ 拧到 0 更干净。

**含自身的组均值，能不能乘回 $G/(G-1)$ 纠正？**
能，乘回去就从 GRPO 的中心化回到了 RLOO 的尺度。多数实现不乘，等于默认接受这层收缩。

**Value 用当前的 $G_t$ 拟合，再拿来减，有问题吗？**
是同一类问题。同一条轨迹既当回归标签又当 baseline，有限样本下两者相关。价值评估模型（critic）要对 $G_t$ 做 stop-gradient，或者用旧策略上的回报来拟合。

**和 PPO 的 critic 比，谁更无偏？**
Critic 是函数近似，又常配 GAE bootstrap，期望上是有偏的，但能处理 $G=1$。组方法在大 $G$、可验证奖励上更接近无偏的 control variate，代价是生成成本。

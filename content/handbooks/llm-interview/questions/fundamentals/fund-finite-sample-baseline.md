---
id: fund-finite-sample-baseline
section: fundamentals
order: 148
level: S
title: 组均值含当前样本、Leave-one-out、batch 标准化，有限样本下谁还无偏？
quick: >-
  教科书 baseline 要求 $b$ 不依赖当前动作。组均值 $\bar r$ 含 $r_i$，有限 $G$ 下自己抵消自己，是
  $O(1/G)$ 偏差；RLOO 用其余 $G-1$ 条，是无偏 control variate。全局 batch 减均值在 batch
  变大时偏差消失；再除 $\sigma$ 则改题目权重，不是「更无偏」。
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

错法：减均值所以无偏，把期望公式直接搬到大小为 $G$ 的同一组样本。恒等式 $\mathbb{E}_a[\nabla\log\pi\,b(s)]=0$ 里的 $b(s)$ 不能是当前这条 $a$ 的函数。有限样本里，组均值、batch 均值、组标准差都看见了当前 $r_i$，无偏性要重新算。和 `pt-rloo-vs-grpo` 的差别：那题比算法选型；本题只钉有限样本偏差从哪来。

## 含自身的组均值：偏差是 $1/G$

同一 prompt 采 $G$ 条，$r_1,\ldots,r_G$。GRPO 常用

$$
\bar r=\frac{1}{G}\sum_{j=1}^G r_j,\qquad \hat A_i=r_i-\bar r=\frac{G-1}{G}\Big(r_i-\frac{1}{G-1}\sum_{j\neq i}r_j\Big).
$$

$\bar r$ 含 $r_i$，等于把优势乘了 $(G-1)/G$，再对 leave-one-out 中心化。$G=2$ 时最狠：两条优势是 $\pm(r_1-r_2)/2$，幅度被腰斩。$G\to\infty$ 时与真正的 $b(s)=\mathbb{E}[r\mid s]$ 一致，偏差消失。所以「GRPO 无偏」只在大组极限下近似成立。全对 / 全错时 $\hat A=0$，不是偏差，是组内没有相对信号，见 `pt-grpo-variance`。

## RLOO：当前样本不进 $b$

$$
b_i=\frac{1}{G-1}\sum_{j\neq i}r_j,\qquad \hat A_i=r_i-b_i.
$$

$b_i$ 与当前动作独立（给定其余样本），是 REINFORCE control variate 的有限样本版：期望上不改梯度，只降方差。$G=2$ 时优势就是两条之差，没有 $(G-1)/G$。RLOO 通常不再除组 $\sigma$，尺度仍是原始 reward；跨题幅度不可比，但不会因为「这题大家都差不多对」就把微小分差放大。

白板用 $G=2$、$r=(1,0)$ 走一遍：GRPO 得 $A=(+0.5,-0.5)$（若再除 $\sigma$ 还会再缩放）；RLOO 得 $A=(+1,-1)$。听到「含不含自身」比背论文名字重要。

## Batch 标准化：偏差随 batch 消失，除 $\sigma$ 是另一回事

REINFORCE++ 一类做法把 baseline 改成全局 batch 均值，再可选地除全局 $\sigma$。相对 prompt 级小 $G$，batch 往往大几十倍，$O(1/N)$ 偏差可以忽略，论文因此说「effective unbiased」。这解决的是「不要在 8 条里估 $\sigma$」，不是证明除标准差无偏。

除 $\sigma$ 无论组内还是全局，都在做数据依赖的重加权：方差小的切片有效学习率变大。Dr.GRPO 批评的 question-level reweighting 就是组内这层，见 `pt-drgrpo`、`fund-adv-norm-bias`。全局 $\sigma$ 把不同 prompt 混在同一个尺度里，偏差形式不同：不再按题放大，但 batch 组成一变，同一条轨迹的 $A$ 含义就变。减均值（常数 baseline）仍在无偏族；除 $\sigma$ 是改目标。

## 追问

- **$G$ 多大可以假装无偏？** 没有魔法数。$G=8$ 的 $(G-1)/G=0.875$，幅度偏差已经不大；真正伤的是再除噪 $\sigma$，以及零方差组。加大 $G$ 降的是 baseline 方差，几乎不改目标，往往比把 $\lambda$ 拧到 0 更干净。
- **含自身能不能「乘回 $G/(G-1)$」纠正？** 能，那就是从 GRPO 中心化回到 RLOO 尺度。多数实现不乘，等于默认接受这层收缩。
- **Value 用当前 $G_t$ 拟合再减回去？** 同类问题。同一条轨迹既当回归标签又当 baseline，有限样本相关；critic 应对 $G_t$ stop-gradient，或用旧策略上的回报。
- **和 PPO critic 比谁更无偏？** Critic 是函数近似 + 常配合 GAE bootstrap，期望上偏，但能处理 $G=1$。组方法在大 $G$、可验证奖励上更接近无偏 control variate，付的是生成成本。

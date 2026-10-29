---
id: fund-wis-ess
section: fundamentals
order: 149
level: S
title: Self-normalized IS 为什么有偏？ESS 怎么读？
quick: >-
  self-normalized IS 要除以随机的 $\sum w_j$，分子分母相关，所以有限样本下有偏，换来的是方差更小。ESS
  $\approx(\sum w)^2/\sum w^2$ 表示这批样本等效还剩几个，接近 1 说明少数权重主导了估计。
tags:
  - Importance Sampling
  - Bias-Variance
  - Off-policy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: Doubly Robust Policy Evaluation and Learning
    url: 'https://arxiv.org/abs/1103.4601'
    type: primary
  - title: Offline Reinforcement Learning — Tutorial
    url: 'https://arxiv.org/abs/1909.03623'
    type: secondary
---

Self-normalized IS（WIS）有偏，是因为它除的 $\sum_j w_j$ 本身也是随机量，分子分母相关，有限样本下期望就对不上真值；换来的好处是方差几乎总是更小。ESS 衡量这批加权样本等效还剩多少个独立样本，接近 1 就说明估计被一两个权重主导了。

先放基础恒等式（见 `fund-is`）：$\mathbb{E}_p[f]=\mathbb{E}_q[(p/q)f]$。记 $w_i=p(x_i)/q(x_i)$，样本来自 proposal $q$。面试里常见的坑是把 PPO 里的 $\rho_t$ 直接叫「无偏 IS」，却说不清普通 IS、self-normalization、截断这三个估计器在偏差和方差上各差在哪。

举个例子：一小批样本里有一条的 $w$ 远大于其他几条。普通 IS 的平均几乎就等于这一条的 $w f$，方差很大；WIS 先 normalization，这一条拿到接近全部权重，数值稳住了，可这批样本也只剩一条的信息量，ESS 会掉到接近 1。

## 三个估计器

$$
\hat\mu_{\mathrm{IS}}=\frac1n\sum_{i=1}^n w_i f(x_i),\qquad
\hat\mu_{\mathrm{WIS}}=\frac{\sum_i w_i f(x_i)}{\sum_j w_j}.
$$

$\hat\mu_{\mathrm{IS}}$ 在 support 覆盖时期望就是 $\mathbb{E}_p[f]$，所以叫无偏。可 $w$ 一旦出现极大值，这一项就独占平均，方差甚至可以没有有限二阶矩。LLM 上 $\rho$ 是 $T$ 个 token 比率的连乘，更容易出现极端值，见 `fund-token-is-var`。

$\hat\mu_{\mathrm{WIS}}$ 把权重再除以它们的和，相当于用经验分布 $\sum \tilde w_i\delta_{x_i}$，其中 $\tilde w_i=w_i/\sum w$。分子分母相关，有限 $n$ 下 $\mathbb{E}[\hat\mu_{\mathrm{WIS}}]\neq\mathbb{E}_p[f]$，这就是 self-normalized / weighted IS 的偏差。$n\to\infty$ 且权重不太病态时它是一致的。好处是估计落在 $f$ 的凸包里，对 $w$ 的公共尺度不敏感（$w$ 乘常数结果不变），实践中方差几乎总是更小。所以 OPE 里更常见的是 WIS，很少直接用未经 normalization 的 IS，见 `arl-offline-policy-evaluation`。

截断 / clip 是第三条路：$\tilde w=\mathrm{clip}(w,0,c)$。它直接引入偏差，但把二阶矩封了顶。PPO clip 的是 surrogate，并没有把真实的 $\rho$ 写进区间；CISPO、V-trace、slime `--use-tis` 才是对权重本身动手。三条路都在做 bias-variance 取舍，各自换的东西不一样，别说成同一种「IS 技巧」。

## ESS 怎么读

$$
\mathrm{ESS}\approx\frac{(\sum_i w_i)^2}{\sum_i w_i^2}=n\cdot\frac{(\bar w)^2}{\overline{w^2}}.
$$

所有 $w$ 相等时 $\mathrm{ESS}=n$，一个 $w$ 独占时 $\mathrm{ESS}\to 1$。它说的是这批样本还剩多少独立信息，和估计有没有偏无关。PPO 一般监控 clip fraction、approx KL，异步 RL 还应该看 ESS 或 $\rho$ 的分位数。ESS 已经掉到个位数还在报「off-policy 复用省了钱」，那估计其实已经是噪声。

读 WIS 的结果要多留个心。加权 IS 会让 ESS 看起来好一些，因为它把质量摊回单纯形；覆盖极差时，WIS 会把估计钉在行为策略附近，看着稳，对目标策略却不敏感。这是偏差，问题并没有修好。

Doubly Robust 用 $\hat Q$ 当 control variate，让权重只去修正残差：$\hat Q$ 准的话方差下降，倾向准的话仍接近无偏。不过 LLM 的开放文本动作上 $\pi(a\mid s)$ 估不准，日志里没走过的动作，DR 也救不了。

## 追问

**为什么 PPO 不写成 WIS？**
Token 级 surrogate 本身就是工程近似，再 self-normalization 会让同一 batch 里的 $\rho$ 互相耦合，梯度更难解释。实践里用 clip + 小步 on-policy，不做完整轨迹的 WIS。

**ESS 能不能当损失（loss）权重？**
可以拿来给病态 batch 降权，但 ESS 本身有偏，也会被异常的 $w$ 驱动。更干净的做法是丢掉 stale 轨迹或缩短 sync，见 `fund-onoff`。

**WIS 和 $k_3$ 像吗？**
思路不一样。$k_3$ 用 $r-1$ 当 KL 的控制变量，期望仍是 KL，是保住无偏去降方差；WIS 改的是 normalization 方式，期望一般已经不是原 IS 的值，是用偏差换方差。

**Support 不覆盖怎么办？**
任何 IS 都救不了。$q$ 在 $p$ 的重要区域为 0，权重怎么 normalization 也变不出那些样本，用 fresh sampling 轨迹（rollout）比换估计器更根本。

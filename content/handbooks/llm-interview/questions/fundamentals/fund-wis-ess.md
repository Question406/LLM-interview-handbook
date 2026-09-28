---
id: fund-wis-ess
section: fundamentals
order: 149
level: S
title: Self-normalized IS 为什么有偏？ESS 怎么读？
quick: >-
  普通 IS $\frac1n\sum w_i f_i$ 无偏，方差随 $w$ 尾部爆炸。Self-normalized（加权）IS 用
  $w_i/\sum w_j$，分母随机，有限 $n$ 有偏、大样本一致，数值更稳。ESS $\approx(\sum
  w)^2/\sum w^2$ 读的是「这批权重等效多少个独立样本」，接近 1 说明少数 $w$ 主宰了估计。
tags:
  - Importance Sampling
  - Bias-Variance
  - Off-policy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Doubly Robust Policy Evaluation and Learning
    url: https://arxiv.org/abs/1103.4601
    type: primary
  - title: Offline Reinforcement Learning — Tutorial
    url: https://arxiv.org/abs/1909.03623
    type: secondary
---

错法：把 PPO 里的 $\rho_t$ 直接叫「无偏 IS」，却说不清 普通 IS、自归一化、截断 三个估计器差在偏与方。基础恒等式见 `fund-is`：$\mathbb{E}_p[f]=\mathbb{E}_q[(p/q)f]$。记 $w_i=p(x_i)/q(x_i)$，样本来自 proposal $q$。

## 普通 IS 无偏，WIS 有限样本有偏

$$
\hat\mu_{\mathrm{IS}}=\frac1n\sum_{i=1}^n w_i f(x_i),\qquad
\hat\mu_{\mathrm{WIS}}=\frac{\sum_i w_i f(x_i)}{\sum_j w_j}.
$$

$\hat\mu_{\mathrm{IS}}$ 的期望就是 $\mathbb{E}_p[f]$（support 覆盖时），所以叫无偏。$w$ 一旦出现极大值，这一项独占平均，方差可以没有有限二阶矩。LLM 上 $\rho$ 是 $T$ 个 token 比的连乘，更容易炸，见 `fund-token-is-var`。

$\hat\mu_{\mathrm{WIS}}$ 把权重再除以它们的和，等价于用经验分布 $\sum \tilde w_i\delta_{x_i}$，$\tilde w_i=w_i/\sum w$。分子分母相关，有限 $n$ 下 $\mathbb{E}[\hat\mu_{\mathrm{WIS}}]\neq\mathbb{E}_p[f]$，这就是 self-normalized / weighted IS 的偏差。$n\to\infty$ 且权重不太病态时一致。换来的是：估计落在 $f$ 的凸包里、对 $w$ 的公共尺度不敏感（$w$ 乘常数结果不变），实践方差几乎总是更小。OPE 里更常见 WIS 而不是生 IS，见 `arl-offline-policy-evaluation`。

截断 / clip 是第三条路：$\tilde w=\mathrm{clip}(w,0,c)$。无偏性直接毁掉，但二阶矩被封顶。PPO clip 的是 surrogate 而不是把真实 $\rho$ 写进区间；CISPO / V-trace / slime `--use-tis` 才是对权重动手。三条都是 bias-variance，不要说成同一种「IS 技巧」。

## ESS：权重有多「有效」

$$
\mathrm{ESS}\approx\frac{(\sum_i w_i)^2}{\sum_i w_i^2}=n\cdot\frac{(\bar w)^2}{\overline{w^2}}.
$$

所有 $w$ 相等时 $\mathrm{ESS}=n$；一个 $w$ 独占时 $\mathrm{ESS}\to 1$。它不是无偏度，是这批样本还剩多少独立信息。PPO 监控 clip fraction、approx KL；异步 RL 还应看 ESS 或 $\rho$ 的分位数。ESS 已经接近个位数还在报「off-policy 复用省了钱」，估计已经是噪声。加权 IS 会让 ESS 看起来好一些，因为它把质量摊回单纯形；覆盖极差时，WIS 会把估计钉在行为策略附近，稳，但不敏感。那是偏差，不是修好了。

Doubly Robust 用 $\hat Q$ 当 control variate，倾向只修正残差：$\hat Q$ 对了则方差掉，倾向对了则仍接近无偏。LLM 开放文本动作上 $\pi(a\mid s)$ 估不准，DR 救不了「日志里没走过的动作」。

## 追问

- **为什么 PPO 不写 WIS？** Token 级 surrogate 已经是工程近似；再自归一化会让同一 batch 里的 $\rho$ 互相耦合，梯度更难解释。实践用 clip + 小步 on-policy，而不是完整轨迹 WIS。
- **ESS 能不能当 loss 权重？** 可以降权病态 batch，但它本身有偏、且会被异常 $w$ 驱动。更干净的是丢掉 stale 轨迹或缩短 sync，见 `fund-onoff`。
- **和 $k_3$ 像吗？** $k_3$ 用 $r-1$ 当 KL 的控制变量，期望仍是 KL。WIS 改的是归一化方式，期望一般不是原 IS。一个保无偏降方差，一个用偏差换方差。
- **Support 不覆盖呢？** 任何 IS 都救不了。$q$ 在 $p$ 重要区域为 0，权重再怎么归一化也变不出那些样本。Fresh rollout 比换估计器更根本。

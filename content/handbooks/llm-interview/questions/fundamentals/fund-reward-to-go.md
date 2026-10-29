---
id: fund-reward-to-go
section: fundamentals
order: 154
level: S
title: Reward-to-go 为什么仍无偏？为什么比整段回报方差更小？
quick: "$t$ 步之前的奖励不依赖 $a_t$，乘进 $\\nabla\\log\\pi(a_t\\mid s_t)$ 的期望是 0，只贡献噪声。换成从 $t$ 起的 $G_t=\\sum_{k\\ge 0}\\gamma^k r_{t+k}$，期望不变，去掉了与当前动作无关的和项，方差通常更小。这是 REINFORCE 相对「整段 $R$ 乘所有 score」的第一步降方差，仍完全无偏。"
tags:
  - Policy Gradient
  - REINFORCE
  - Bias-Variance
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Simple Statistical Gradient-Following Algorithms for Connectionist Reinforcement Learning (REINFORCE)
    url: https://link.springer.com/article/10.1007/BF00992696
    type: primary
  - title: Policy Gradient Methods for Reinforcement Learning with Function Approximation
    url: https://proceedings.neurips.cc/paper/1999/hash/464d828b85b0bed98e80ade0a5c43b0f-Abstract.html
    type: primary
---

Reward-to-go 无偏，是因为过去的奖励和当前动作的 score $\nabla\log\pi(a_t\mid s_t)$ 不相关，这部分乘进去的期望本来就是 0；把它删掉，期望不变，还少乘了一截噪声，所以方差通常更小。它是因果性允许的无偏收缩，没有做任何近似；可它也远没把方差降到能训 LLM 的程度。完整目标见 `fund-pg-theorem`。

## 过去的奖励为什么贡献 0

轨迹回报 $R=\sum_{k=0}^T\gamma^k r_k$。对数导数把梯度写成

$$
\nabla_\theta J=\mathbb{E}\Big[\Big(\sum_{t=0}^T\nabla_\theta\log\pi_\theta(a_t\mid s_t)\Big)R\Big]
=\mathbb{E}\Big[\sum_{t=0}^T\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,R\Big].
$$

把 $R$ 拆成 $t$ 之前和从 $t$ 起两段。对固定的 $t$，过去那段和 $\sum_{k\lt t}\gamma^k r_k$ 在 $s_t$ 之前就已经实现了，不依赖 $a_t$。于是

$$
\mathbb{E}\big[\nabla_\theta\log\pi_\theta(a_t\mid s_t)\cdot(\text{past})\big]
=\mathbb{E}\Big[\mathbb{E}\big[\nabla_\theta\log\pi_\theta(a_t\mid s_t)\mid s_t\big]\cdot(\text{past})\Big]=0,
$$

因为 $\sum_a\nabla\pi(a\mid s)=0$。所以把系数换成

$$
G_t=\sum_{k=0}^{T-t}\gamma^k r_{t+k}
$$

不改期望。带着「这个动作好不好」信息的，只有未来的奖励。

## 方差为什么通常更小

$\mathrm{Var}(\nabla\log\pi\cdot R)=\mathrm{Var}(\nabla\log\pi\cdot(G_t+\text{past}))$。past 和 $\nabla\log\pi(a_t\mid s_t)$ 不相关，可它自己的噪声还是被乘进了梯度，减掉 past，等于丢掉一项均值为 0 的干扰。这里没有引入新的 $b(s)$，算不上控制变量，就是把一项纯噪声直接删了。

白板上可以用一个两步 MDP 讲：第一步的 $r_0$ 很大、和 $a_1$ 无关。用整段 $R$ 更新 $a_1$ 时，一次幸运的 $r_0$ 会让所有第二步动作都显得好；换成 $G_1$，就只剩从 $a_1$ 起的回报。LLM 里 prompt 不算动作、损失只算在回复 token 上，也是同一条因果性：别人已经吐出的 token、环境转移，都不进当前的 score。

它解决不了稀疏终局奖励。如果只有 $r_T$ 非零，$G_t=\gamma^{T-t}r_T$，每个前缀 token 仍然乘同一个随机变量，方差随 $T$ 涨，见 `fund-pg-horizon-var`。下一步要减 $V(s_t)$ 或组 baseline，见 `fund-optimal-baseline`。

## 追问

**$\gamma\lt 1$ 算 reward-to-go 吗？**
不算，两者管的是不同的东西。$\gamma$ 定义任务里「多远的奖励还算数」，改的是 $J$ 本身；reward-to-go 是估计器的选择，用 $G_t$ 还是 $R$。别把折扣说成因果性，见 `fund-gamma-vs-lambda`。

**只拿最后一步的 $r_T$ 乘所有 token，行不行？**
行，那是稀疏奖励下 $G_t$ 的特例（$\gamma=1$），仍然无偏，方差最大，也谈不上另一种算法。

**和 GAE 是什么关系？**
Reward-to-go 是 $\lambda=1$、不 bootstrap 的 MC 优势的分子。GAE 再用 $V$ 截断未来，从那里开始有偏。

**未来的奖励依赖 $a_t$ 吗？**
依赖，所以 $G_t$ 不能删，能删的只有过去那段。

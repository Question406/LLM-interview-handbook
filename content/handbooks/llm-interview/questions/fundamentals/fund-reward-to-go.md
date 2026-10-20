---
id: fund-reward-to-go
section: fundamentals
order: 154
level: S
title: Reward-to-go 为什么仍无偏？为什么比整段回报方差更小？
quick: >-
  $t$ 步之前的奖励不依赖 $a_t$，乘进 $\nabla\log\pi(a_t\mid s_t)$ 仍无偏，但是纯噪声。换成从 $t$
  起的 $G_t=\sum_{k\ge 0}\gamma^k r_{t+k}$，期望不变，去掉了与当前动作无关的和项，方差通常更小。这是
  REINFORCE 相对「整段 $R$ 乘所有 score」的第一步降方差，仍完全无偏。
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

常见误区是：reward-to-go 是「有偏的因果近似」，或反过来以为它已经把方差降到能训 LLM。它只是因果性允许的无偏收缩：过去的奖励与当前 $\nabla\log\pi$ 不相关，乘进去期望仍对，但多乘了一截噪声。完整目标见 `fund-pg-theorem`。

## 过去的 $r$ 对当前 score 的贡献期望是 0

轨迹回报 $R=\sum_{k=0}^T\gamma^k r_k$。对数导数把梯度写成

$$
\nabla_\theta J=\mathbb{E}\Big[\Big(\sum_{t=0}^T\nabla_\theta\log\pi_\theta(a_t\mid s_t)\Big)R\Big]
=\mathbb{E}\Big[\sum_{t=0}^T\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,R\Big].
$$

把 $R$ 拆成 $t$ 之前和从 $t$ 起。对固定 $t$，过去和 $\sum_{k\lt t}\gamma^k r_k$ 在 $s_t$ 之前已经实现，不依赖 $a_t$。于是

$$
\mathbb{E}\big[\nabla_\theta\log\pi_\theta(a_t\mid s_t)\cdot(\text{past})\big]
=\mathbb{E}\Big[\mathbb{E}\big[\nabla_\theta\log\pi_\theta(a_t\mid s_t)\mid s_t\big]\cdot(\text{past})\Big]=0,
$$

因为 $\sum_a\nabla\pi(a\mid s)=0$。所以把系数换成

$$
G_t=\sum_{k=0}^{T-t}\gamma^k r_{t+k}
$$

不改期望。未来的奖励才携带「这个动作好不好」的信息。

## 方差为什么更小（通常）

$\mathrm{Var}(\nabla\log\pi\cdot R)=\mathrm{Var}(\nabla\log\pi\cdot(G_t+\text{past}))$。past 与 $\nabla\log\pi(a_t\mid s_t)$ 不相关，但它自己的噪声仍被乘进梯度。减掉 past，相当于丢掉一项均值为 0 的干扰。这不是控制变量（没引入新的 $b(s)$），是把恒为噪声的和项直接删掉。

白板用两步 MDP：第一步 $r_0$ 很大、与 $a_1$ 无关。用整段 $R$ 更新 $a_1$ 时，幸运的 $r_0$ 会让所有第二步动作看起来都好；用 $G_1$ 则只剩从 $a_1$ 起的回报。LLM 里 输入提示（prompt） 不是动作、只在回复 token 上计算损失，是同一条因果性：别人已经吐出的 token、环境转移，都不进当前 score。

它没有解决稀疏终局奖：若只有 $r_T$ 非零，$G_t=\gamma^{T-t}r_T$，每个前缀 token 仍乘同一个随机变量，方差随 $T$ 涨，见 `fund-pg-horizon-var`。下一步才是减 $V(s_t)$ 或组 baseline，见 `fund-optimal-baseline`。

## 追问

- **$\gamma\lt 1$ 算 reward-to-go 吗？** $\gamma$ 定义的是任务里「多远的奖励还算数」，改的是 $J$ 本身。Reward-to-go 是估计器：用 $G_t$ 还是 $R$。不要把折扣说成因果性。见 `fund-gamma-vs-lambda`。
- **能不能只用最后一步的 $r_T$ 乘所有 token？** 那是稀疏奖励下 $G_t$ 的特例（$\gamma=1$），仍无偏，方差最大。不是又一种算法。
- **和 GAE 什么关系？** Reward-to-go 是 $\lambda=1$、不 bootstrap 的 MC 优势的分子。GAE 再用 $V$ 截断未来，开始有偏。
- **未来奖励依赖 $a_t$ 吗？** 依赖。所以不能把 $G_t$ 也删掉。只能删 past。

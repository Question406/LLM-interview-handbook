---
id: fund-pg-theorem
section: fundamentals
order: 3
level: S
title: Policy Gradient Theorem / REINFORCE 怎么从目标函数推出来？
quick: >-
  目标是 $J(\theta)=\mathbb{E}_{\tau\sim\pi_\theta}[R(\tau)]$。用 $\nabla\pi=\pi\nabla\log\pi$
  把对分布的梯度变成对 $\log\pi$ 的期望，得到 $\nabla J=\mathbb{E}[R\nabla\log\pi]$；因果性允许把整段回报换成从 $t$
  往后的 $G_t$。这就是 REINFORCE，无偏但方差大。
tags:
  - RL
  - Policy Gradient
  - REINFORCE
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

后面 PPO / GRPO 的所有公式都从这一条期望梯度长出来。先把目标钉死：参数化策略 $\pi_\theta$，一条轨迹 $\tau=(s_0,a_0,\ldots,s_T,a_T)$，回报 $R(\tau)=\sum_{t=0}^T\gamma^t r_t$，优化

$$
J(\theta)=\mathbb{E}_{\tau\sim\pi_\theta}\big[R(\tau)\big]=\sum_\tau \pi_\theta(\tau)\,R(\tau).
$$

环境转移 $P$ 不含 $\theta$，所以

$$
\pi_\theta(\tau)=p(s_0)\prod_{t=0}^T \pi_\theta(a_t\mid s_t)\,P(s_{t+1}\mid s_t,a_t).
$$

## 对数导数技巧

直接对 $\pi_\theta(\tau)$ 求导不好采样。恒等式是

$$
\nabla_\theta\pi_\theta(\tau)=\pi_\theta(\tau)\,\nabla_\theta\log\pi_\theta(\tau),
$$

因为 $\nabla\log\pi=\nabla\pi/\pi$。于是

$$
\nabla_\theta J(\theta)=\sum_\tau \pi_\theta(\tau)\,R(\tau)\,\nabla_\theta\log\pi_\theta(\tau)=\mathbb{E}_{\tau\sim\pi_\theta}\big[R(\tau)\,\nabla_\theta\log\pi_\theta(\tau)\big].
$$

轨迹的 log 概率里，初始分布和转移概率对 $\theta$ 的梯度为 0，只剩策略项：

$$
\nabla_\theta\log\pi_\theta(\tau)=\sum_{t=0}^T\nabla_\theta\log\pi_\theta(a_t\mid s_t).
$$

这就是 **score-function / likelihood-ratio** 估计：环境可以不可微，只要能采样、能拿到标量回报，就能更新 $\pi$。

## 因果性：整段 $R$ 可以换成 $G_t$

$t$ 之前已经发生的奖励不依赖 $a_t$。用整段 $R$ 仍然无偏，但把与当前动作无关的噪声乘进了梯度。把 $t$ 步的系数换成从该步起的回报

$$
G_t=\sum_{k=0}^{T-t}\gamma^k r_{t+k}
$$

仍然无偏，方差通常更小：

$$
\nabla_\theta J(\theta)=\mathbb{E}\left[\sum_{t=0}^T \nabla_\theta\log\pi_\theta(a_t\mid s_t)\,G_t\right].
$$

这就是 **REINFORCE**。采样一条轨迹，每个 token / action 的梯度是 $\nabla\log\pi$ 乘「从这里往后看起来有多好」。

## 我会主动补的三句

- **无偏、高方差。** $G_t$ 是一条样本路径，不是期望。这是后面要减 baseline、上 Critic、上 group 相对优势的原因。
- **只对动作的 log 概率求导。** Prompt、环境转移、别人已经吐出的 token 都不是当前 $\pi_\theta$ 的 action。LLM 里损失只加在 response token 上，就是这条。
- **on-policy。** 期望是在 $\pi_\theta$ 自己的轨迹上取的。一旦用旧策略采样，必须再引入重要性采样，那是通往 PPO 的下一步。

推导减 baseline、再接到 PPO / GRPO，见「从 Policy Gradient 怎么一步步推到 PPO，再推到 GRPO？」。

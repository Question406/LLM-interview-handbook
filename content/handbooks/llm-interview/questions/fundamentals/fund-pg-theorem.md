---
id: fund-pg-theorem
section: fundamentals
order: 3
level: S
title: Policy Gradient Theorem / REINFORCE 怎么从目标函数推出来？
quick: "关键是对数导数技巧：目标 $J(\\theta)=\\mathbb{E}_{\\tau\\sim\\pi_\\theta}[R(\\tau)]$，用 $\\nabla\\pi=\\pi\\nabla\\log\\pi$ 把对分布的梯度变成对 $\\log\\pi$ 的期望，得到 $\\nabla J=\\mathbb{E}[R\\nabla\\log\\pi]$。再用因果性把整段回报换成从 $t$ 往后的 $G_t$，就是 REINFORCE，无偏但方差大。"
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

推导靠一个技巧：用 $\nabla\pi=\pi\nabla\log\pi$ 把「对分布求导」变成「在分布下求期望」，这样只要能 sampling 就能估梯度；再用因果性把整段回报换成从当前步往后的 $G_t$，就得到 REINFORCE。后面 PPO / GRPO 的公式都建立在这条期望梯度上。

先把目标固定下来：参数化策略 $\pi_\theta$，一条轨迹 $\tau=(s_0,a_0,\ldots,s_T,a_T)$，回报 $R(\tau)=\sum_{t=0}^T\gamma^t r_t$，优化

$$
J(\theta)=\mathbb{E}_{\tau\sim\pi_\theta}\big[R(\tau)\big]=\sum_\tau \pi_\theta(\tau)\,R(\tau).
$$

环境转移 $P$ 不含 $\theta$，所以

$$
\pi_\theta(\tau)=p(s_0)\prod_{t=0}^T \pi_\theta(a_t\mid s_t)\,P(s_{t+1}\mid s_t,a_t).
$$

## 对数导数技巧

直接对 $\pi_\theta(\tau)$ 求导，得到的东西没法靠 sampling 来估。要用的恒等式是

$$
\nabla_\theta\pi_\theta(\tau)=\pi_\theta(\tau)\,\nabla_\theta\log\pi_\theta(\tau),
$$

它成立是因为 $\nabla\log\pi=\nabla\pi/\pi$。代进去就是

$$
\nabla_\theta J(\theta)=\sum_\tau \pi_\theta(\tau)\,R(\tau)\,\nabla_\theta\log\pi_\theta(\tau)=\mathbb{E}_{\tau\sim\pi_\theta}\big[R(\tau)\,\nabla_\theta\log\pi_\theta(\tau)\big].
$$

轨迹的 log 概率里，初始分布和转移概率对 $\theta$ 的梯度都是 0，只剩策略项：

$$
\nabla_\theta\log\pi_\theta(\tau)=\sum_{t=0}^T\nabla_\theta\log\pi_\theta(a_t\mid s_t).
$$

这就是 score-function，也叫 likelihood-ratio 估计。它的好处是环境可以不可微，只要能 sampling、能拿到标量回报，就能更新 $\pi$。比如回报是「单元测试过没过」，这东西没法求导，照样能用。

## 因果性：把整段 $R$ 换成 $G_t$

$t$ 之前已经发生的奖励不依赖 $a_t$。用整段 $R$ 仍然无偏，但把和当前动作无关的噪声也乘进了梯度。把第 $t$ 步的系数换成从这一步起的回报

$$
G_t=\sum_{k=0}^{T-t}\gamma^k r_{t+k}
$$

仍然无偏，方差通常更小：

$$
\nabla_\theta J(\theta)=\mathbb{E}\left[\sum_{t=0}^T \nabla_\theta\log\pi_\theta(a_t\mid s_t)\,G_t\right].
$$

这就是 REINFORCE：sampling 一条轨迹，每个 token 或动作的梯度是 $\nabla\log\pi$ 乘上「从这里往后看起来有多好」。减 baseline、再接到 PPO / GRPO 的推导，见「从 Policy Gradient 怎么一步步推到 PPO，再推到 GRPO？」。

## 追问

**这个估计器有什么问题？**
无偏，但方差高。$G_t$ 是一条样本路径的结果，算不上期望，所以后面才要减 baseline、上 Critic、用 group 相对优势。

**LLM 里对哪些 token 求导？**
只对动作的 log 概率求导。Prompt、环境转移、别人已经吐出的 token 都不是当前 $\pi_\theta$ 的 action，LLM 里损失只加在 response token 上，说的就是这一条。

**能直接用旧策略采的样本吗？**
不能直接用，它是 on-policy 的，期望是在 $\pi_\theta$ 自己的轨迹上取的。一旦用旧策略 sampling，就必须引入 importance sampling，那是通往 PPO 的下一步。

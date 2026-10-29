---
id: fund-optimal-baseline
section: fundamentals
order: 147
level: S
title: 为什么 $V^\pi(s)$ 是最优 baseline？$V$ 估错了梯度还无偏吗？
quick: >-
  $V$ 估错了，只拿它当 baseline 减，梯度仍然无偏：只依赖 $s$ 的 $b(s)$ 不改变 policy gradient
  的期望，估错的代价是降方差的效果变差。取 $b(s)=V^\pi(s)$ 能把回报中心化，使方差接近最小。用错误的 $\hat V$ 替代未来回报做
  bootstrap，才会引入偏差。
tags:
  - RL
  - Policy Gradient
  - Baseline
  - Bias-Variance
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: >-
      Simple Statistical Gradient-Following Algorithms for Connectionist
      Reinforcement Learning (REINFORCE)
    url: 'https://link.springer.com/article/10.1007/BF00992696'
    type: primary
  - title: >-
      Policy Gradient Methods for Reinforcement Learning with Function
      Approximation
    url: >-
      https://proceedings.neurips.cc/paper/1999/hash/464d828b85b0bed98e80ade0a5c43b0f-Abstract.html
    type: primary
---

$V^\pi(s)$ 是最自然的 baseline，因为它正好是这个状态下回报的条件期望，减掉它，就把「这个状态本来就好」那部分公共噪声去掉了。$V$ 估错了要分两种用法看：只拿它当 baseline 减，梯度仍然无偏，只是方差降得少；拿它当 bootstrap 去替换还没发生的未来回报，价值评估模型（critic）的误差才会写进期望，变成偏差。

先看为什么减什么都无偏。Baseline 恒等式（见 `fund-pg-baseline`）是

$$
\mathbb{E}_{a\sim\pi(\cdot\mid s)}\big[\nabla_\theta\log\pi_\theta(a\mid s)\,b(s)\big]=b(s)\,\nabla_\theta\sum_a\pi_\theta(a\mid s)=0.
$$

所以估计器 $\nabla\log\pi\cdot(G_t-b(s_t))$ 对任意函数 $b(s)$ 都无偏，常数可以，$V$ 可以，一个乱写的 MLP 也可以，只要它不看当前 sampling 到的 $a_t$。

## 为什么最优的是 $V^\pi$

无偏只保证期望对，方差另说。比如同一道很简单的题，几乎怎么答都能拿高分，$G_t$ 就很大，可这份高分大部分来自「这个 state 本来就好」，和当前动作关系不大。$G_t$ 把这两部分混在一起，减去该 state 下回报的条件期望

$$
b^\star(s)=\mathbb{E}[G_t\mid s_t=s]=V^\pi(s)
$$

就得到 advantage $A^\pi=Q^\pi-V^\pi$，它在 $s$ 上均值为 0，公共噪声被去掉了。严格讲，最小化 $\mathrm{Var}(\nabla\log\pi\cdot(G-b(s)))$ 的 $b$ 是按 $\|\nabla\log\pi\|^2$ 加权的条件期望，不一定恰好等于 $V$；面试里说 $V$ 是自然、近优的 control variate 就够了，不必推加权式。实践中训一个 critic 去拟合 $V^\pi$，就是在估这条 baseline。

$b$ 一旦依赖当前动作，恒等式就不成立了，除非再做 importance 或 leave-one-out 修正。所以不能把一条回复自己的 reward 不加处理就当它自己的 baseline，RLOO 计算某条样本的 baseline 时也要把它自己排除掉，见 `fund-finite-sample-baseline`。

## $V$ 估错时，偏差从哪来

记 $\hat V$ 为任意函数，underfitting、滞后、甚至常数 0 都行。

用 MC advantage $\hat A_t=G_t-\hat V(s_t)$ 时，$\hat V(s_t)$ 仍然只依赖 state，期望梯度不变。估错的代价是方差减得少，甚至比不减 baseline 时噪声还大，这是方差问题，和偏差无关。

$n$-step 和 GAE 不一样，它们把 $G_t$ 里还没发生的回报换成 $\gamma^n\hat V(s_{t+n})$。$\hat V\neq V^\pi$ 时，这段替换的期望就不是真优势，偏差是从这里来的。$\lambda\to 0$ 越相信 $\hat V$，$\lambda\to 1$ 越退回 MC，见 `pt-gae`、`stepfun-gae-mc-td`。

面试官常接着问「那 critic 不准还能训吗」。能，PPO 实际训练中用的 critic 也不完全准，你接受的是 GAE 的 bootstrap 偏差，用它换方差。如果 $\hat V$ 系统性低估长 chain of thought，小 $\lambda$ 会把长思考的优势压掉，这时偏差已经占主导，该加大 $\lambda$、换成组相对优势，或者先把 value 拟合好终局，加学习率没用。

还可以补一句兼容函数近似：critic 对 $\nabla\log\pi$ 特征是线性的时候，即使 $Q$ 有近似误差，policy gradient 在投影意义下仍然是对的。LLM 里几乎没人真去构造兼容特征，别把它说成 PPO 的实现细节。

## 追问

**常数 baseline 合法吗？**
合法，全局减均值就是常数 $b$。它没有条件在 state 上，降方差的效果比 $V(s)$ 弱。

**RM 分数能当 $V$ 吗？**
不能直接代。RM 是标量 reward model，critic 估的是从这个 token 起的期望回报，见 `baidu-gae-lambda`。

**GRPO 没有 $V$，为什么也能降方差？**
同一 prompt 下多条 sampling 轨迹（rollout）的均值就是另一种 $b(s)$，只是 state 粗到了「这道题」这个粒度，见 `pt-rloo-vs-grpo`。

**$\hat V$ overfitting 当前 batch 会怎样？**
如果 $\hat V$ 偷看了 $a_t$ 或当前的 $G_t$，baseline 的条件就被破坏了，有限样本下会偏。所以 value 要 stop-gradient，也别拿同一条轨迹的 $G_t$ 既当目标又当减数而不做 LOO。

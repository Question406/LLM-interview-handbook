---
id: fund-mc-minus-v
section: fundamentals
order: 156
level: S
title: $G_t-V(s_t)$ 和 GAE 差在哪？怎样用 Critic 降方差却保持无偏？
quick: "$G_t-\\hat V(s_t)$ 只把 critic 当 baseline，$\\hat V$ 不准也无偏，只是降方差少。GAE 在 $\\lambda\\lt 1$ 时用 $\\hat V(s')$ 替代未来回报，critic 误差会进入期望，所以有偏。"
tags:
  - GAE
  - Baseline
  - Actor-Critic
  - Bias-Variance
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: High-Dimensional Continuous Control Using Generalized Advantage Estimation
    url: https://arxiv.org/abs/1506.02438
    type: primary
  - title: Q-Prop — Sample-Efficient Policy Gradient with An Off-Policy Critic
    url: https://arxiv.org/abs/1611.02247
    type: secondary
---

常见误区是：「上了 critic 所以梯度有偏」。Critic 有两种用法，偏倚来自第二种。第一种是 control variate：

$$
\hat A_t^{\mathrm{MC}}=G_t-\hat V(s_t).
$$

$G_t$ 来自真实轨迹，无偏估 $Q^\pi$；$\hat V(s_t)$ 只依赖 state。由 `fund-pg-baseline`，任意 $b(s)$ 都不改 $\mathbb{E}[\nabla\log\pi\cdot(G-b)]$。$\hat V$ 是常数、滞后、甚至乱初始化，MC 优势仍然无偏。估错的代价见 `fund-optimal-baseline`：方差减得少。

## GAE 多做的那一步：用 $V$ 代替还没发生的回报

$$
\delta_t=r_t+\gamma\hat V(s_{t+1})-V(s_t),\qquad
\hat A_t^{\mathrm{GAE}}=\sum_{l\ge 0}(\gamma\lambda)^l\delta_{t+l}.
$$

$\lambda=1$ 且不截断时，残差链在代数上回到 $G_t-V(s_t)$（$V$ 在中间项抵消）。$\lambda\lt 1$ 或 $n$-step 提前用 $\hat V(s_{t+n})$ 截断，等于声称「从那儿起的期望回报就是 $\hat V$」。若这个价值估计不准确，就会使优势估计有偏。可以这样比较：

| | 用了 $V$ 吗 | 无偏？ |
| --- | --- | --- |
| 纯 $G_t$ | 否 | 是，方差最大 |
| $G_t-\hat V(s_t)$ | 只减 | 是 |
| GAE $\lambda=1$、完整回合 | 减，中间抵消 | 是（忽略函数近似实现细节） |
| GAE $\lambda\lt 1$ / TD | 减且替换未来 | 否 |

减去只依赖状态的 $V$ 不改变期望梯度；用近似 $V$ 替代未来回报则可能引入偏差。 不要把 PPO 标配的 $\lambda=0.95$ 说成「无偏 actor-critic」。它明确用偏差换方差，见 `pt-gae`、`stepfun-gae-mc-td`。

## 想保持无偏时 价值评估模型（critic） 还能干什么

- 只当 baseline：拟合 $V^\pi$，用 $G_t-\hat V$，或 $\lambda=1$。样本仍要跑完整回合（或承认截断是另一层偏，见 `fund-term-vs-trunc`）。
- Q-Prop 一类：把 critic 当控制变量，再补一项对 critic 可微的修正，使总期望仍是 $\nabla J$。加分项，不必当默认实现。
- 不要 指望「先把 $V$ 训准，小 $\lambda$ 就近似无偏」。$V$ 准则偏差小，但「近似无偏」仍是有偏；$V$ 一滞后（策略已经走了），偏差立刻回来。

LLM 长 思维链（CoT，即分步推理过程） 很难拿到准 $V$，所以很多人宁可用组均值这种粗 baseline，也不用小 $\lambda$ 的 GAE。组均值是 $b(s)$ 的经验版，属于「减」、不是「替未来」。有限样本偏差是另一层，见 `fund-finite-sample-baseline`。

## 追问

- **PPO 的 value 损失（loss） 训歪了，policy 还能无偏吗？** 若优势是 $G-V$，可以。若优势是 GAE，不能。先问实现用的是哪条 $\hat A$。
- **$\lambda=1$ 还要 critic 吗？** 要，用来减方差。没有 $V$ 就是纯 MC。$\lambda=1$ 不是「等于没 critic」。
- **returns = adv + V 是无偏回报吗？** 那是把 $\hat A$ 加回 baseline 当 value target。$\hat A$ 若来自 GAE，这个 return 同样有偏。见 `code-gae`。
- **过程奖励还要不要 GAE？** $r_t$ 已密，可以用更小 $\lambda$。那是 crediting，不是「因此无偏」。

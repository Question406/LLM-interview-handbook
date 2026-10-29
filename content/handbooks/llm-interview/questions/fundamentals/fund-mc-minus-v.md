---
id: fund-mc-minus-v
section: fundamentals
order: 156
level: S
title: $G_t-V(s_t)$ 和 GAE 差在哪？怎样用 Critic 降方差却保持无偏？
quick: "差在 critic 的用法。$G_t-\\hat V(s_t)$ 只把 critic 当 baseline 减掉，$\\hat V$ 不准也无偏，只是降方差降得少；GAE 在 $\\lambda\\lt 1$ 时用 $\\hat V(s')$ 替代还没发生的回报，critic 误差会进入期望，所以有偏。想保持无偏，就只用 critic 当 baseline，或取 $\\lambda=1$、跑完整回合。"
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
差别在 critic 是只被「减掉」，还是被拿来「替代未来回报」。$G_t-\hat V(s_t)$ 里 critic 只是个 baseline，再不准也不影响无偏；GAE 在 $\lambda\lt 1$ 时用 $\hat V$ 顶替还没发生的回报，critic 的误差就进了期望。所以「上了 critic 梯度就有偏」这句话不准，偏差只来自第二种用法。第一种是 control variate：

$$
\hat A_t^{\mathrm{MC}}=G_t-\hat V(s_t).
$$

$G_t$ 来自真实轨迹，是 $Q^\pi$ 的 unbiased estimate；$\hat V(s_t)$ 只依赖 state。由 `fund-pg-baseline`，任何 $b(s)$ 都不改变 $\mathbb{E}[\nabla\log\pi\cdot(G-b)]$。所以 $\hat V$ 是常数、滞后，甚至是乱初始化的，MC 优势照样无偏，估错的代价只是方差减得少，见 `fund-optimal-baseline`。

举个例子，critic 刚初始化，对所有状态都输出 0，这时 $G_t-\hat V(s_t)$ 就退化成纯 MC 回报，方差大但期望没错；同一个 critic 放进 $\lambda=0.5$ 的 GAE，就等于宣称「从下一步起的期望回报是 0」，优势直接被带偏。

## GAE 多做的那一步：用 $V$ 代替还没发生的回报

$$
\delta_t=r_t+\gamma\hat V(s_{t+1})-V(s_t),\qquad
\hat A_t^{\mathrm{GAE}}=\sum_{l\ge 0}(\gamma\lambda)^l\delta_{t+l}.
$$

$\lambda=1$ 且不截断时，残差链在代数上回到 $G_t-V(s_t)$，中间各项的 $V$ 互相抵消。$\lambda\lt 1$，或者 $n$-step 提前用 $\hat V(s_{t+n})$ 截断，等于声称「从那儿起的期望回报就是 $\hat V$」，价值估计不准，advantage estimation 就有偏。放在一起比较：

| | 用了 $V$ 吗 | 无偏？ |
| --- | --- | --- |
| 纯 $G_t$ | 否 | 是，方差最大 |
| $G_t-\hat V(s_t)$ | 只减 | 是 |
| GAE $\lambda=1$、完整回合 | 减，中间抵消 | 是（忽略函数近似实现细节） |
| GAE $\lambda\lt 1$ / TD | 减且替换未来 | 否 |

减去只依赖状态的 $V$ 不改变期望梯度，用近似的 $V$ 替代未来回报才可能引入偏差。PPO 标配的 $\lambda=0.95$ 是明确地用偏差换方差，别把它说成「无偏的 actor-critic」，见 `pt-gae`、`stepfun-gae-mc-td`。

## 想保持无偏，价值评估模型（critic）还能干什么

最直接的是只当 baseline：拟合 $V^\pi$，用 $G_t-\hat V$，或者取 $\lambda=1$。样本仍然要跑完整回合，截断算另一层偏差，见 `fund-term-vs-trunc`。

Q-Prop 一类方法把 critic 当控制变量，再补一项对 critic 可微的修正，让总期望仍然是 $\nabla J$。这是加分项，不必当默认实现。

也别指望「先把 $V$ 训准，小 $\lambda$ 就近似无偏」。$V$ 准，偏差确实小，但近似无偏仍然是有偏；$V$ 一滞后（策略已经往前走了），偏差马上回来。

LLM 的长 chain of thought（CoT，即分步推理过程）很难拿到准的 $V$，所以很多人宁可用组均值这种粗 baseline，也不用小 $\lambda$ 的 GAE。组均值是 $b(s)$ 的经验版，属于「减」，不属于「替未来」；它的有限样本偏差是另一层问题，见 `fund-finite-sample-baseline`。

## 追问

**PPO 的 value 损失（loss）训歪了，policy 梯度还能无偏吗？**
如果优势是 $G-V$，可以；如果优势是 GAE，不能。先问实现里用的是哪种 $\hat A$。

**$\lambda=1$ 还要 critic 吗？**
要，用来减方差。没有 $V$ 就是纯 MC，$\lambda=1$ 不等于没有 critic。

**returns = adv + V 是无偏的回报吗？**
那是把 $\hat A$ 加回 baseline 当 value target。$\hat A$ 如果来自 GAE，这个 return 同样有偏，见 `code-gae`。

**有过程奖励时还要不要 GAE？**
$r_t$ 已经很密，可以用更小的 $\lambda$。那是在做 credit assignment，并不能因此说它无偏。

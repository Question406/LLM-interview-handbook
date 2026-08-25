---
id: pt-pg-to-ppo-to-grpo
section: posttrain
order: 4
level: S
title: 从 Policy Gradient 怎么一步步推到 PPO，再推到 GRPO？
quick: >-
  REINFORCE 给出 $\nabla J=\mathbb{E}[\nabla\log\pi\cdot G]$，无偏但方差大。减与动作无关的 baseline 得到
  advantage；复用旧轨迹要乘 $\rho=\pi_\theta/\pi_{\mathrm{old}}$，偏离太远则方差爆，于是 TRPO 用 KL
  约束、PPO 用 clip 做一阶近似。LLM 上同 prompt 多采样、奖励在序列末才出现时，组均值可以代替
  $V_\psi$，PPO 的 clip 目标就变成 GRPO。
tags:
  - Policy Gradient
  - PPO
  - GRPO
  - GAE
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Policy Gradient Methods for Reinforcement Learning with Function Approximation
    url: https://proceedings.neurips.cc/paper/1999/hash/464d828b85b0bed98e80ade0a5c43b0f-Abstract.html
    type: primary
  - title: Trust Region Policy Optimization
    url: https://arxiv.org/abs/1502.05477
    type: primary
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: primary
  - title: High-Dimensional Continuous Control Using Generalized Advantage Estimation
    url: https://arxiv.org/abs/1506.02438
    type: primary
  - title: DeepSeekMath / GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

把这条链当成白板推导，不要背三份互不相关的公式。每一步都只修上一步的一个缺陷。

## 1. REINFORCE：能对不可微环境求导

目标 $J(\theta)=\mathbb{E}_{\tau\sim\pi_\theta}[R(\tau)]$。对数导数 $\nabla\pi=\pi\nabla\log\pi$ 把「对分布求导」变成「对 $\log\pi$ 取期望」：

$$
\nabla_\theta J=\mathbb{E}_{\tau\sim\pi_\theta}\Big[R(\tau)\sum_t\nabla_\theta\log\pi_\theta(a_t\mid s_t)\Big].
$$

因果性允许把整段 $R$ 换成从 $t$ 起的回报 $G_t$，仍无偏。这就是 REINFORCE。完整板书见「Policy Gradient Theorem / REINFORCE 怎么从目标函数推出来？」。

缺陷：一条轨迹的 $G_t$ 噪声极大。好状态里的普通动作、坏状态里的好动作会被同一把标尺衡量。

## 2. Baseline / Advantage：不改期望，只降方差

只依赖 state 的 $b(s)$ 满足 $\mathbb{E}_{a\sim\pi}[\nabla\log\pi(a\mid s)b(s)]=0$，所以

$$
\nabla_\theta J=\mathbb{E}\big[\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,(G_t-b(s_t))\big]
$$

与原来同一期望。自然选择是 $b(s)=V^\pi(s)$，于是系数变成 advantage $A^\pi=Q^\pi-V^\pi$：「这个动作比该状态下的平均行为好多少」。细节见「Policy Gradient 为什么可以减 Baseline？」和「Bellman Equation、V、Q、Advantage 的关系？」。

缺陷：真实 $V^\pi$ 没有闭式。用 Monte Carlo 估 $G_t$ 仍很吵；用一步 TD 又偏。

## 3. Actor-Critic + GAE：用 $V_\psi$ 在 bias-variance 之间插值

再训一个 Critic $V_\psi(s)$。TD residual $\delta_t=r_t+\gamma V(s_{t+1})-V(s_t)$ 是一步 advantage；GAE 把不同 horizon 的 $\delta$ 做指数混合，用 $\lambda$ 在「信 bootstrap」和「信整条回报」之间滑动。推导见「从 TD residual 推导 GAE，并解释 $\gamma$、$\lambda$」。

此时算法已经是 on-policy actor-critic：Actor 用 $\hat{A}$ 做策略梯度，Critic 拟合 $V^\pi$。LLM RLHF 里的 PPO 就是这个骨架，再加 clip 和 KL。

缺陷：每更新几步就要重新采样。样本太贵，想对同一批 rollout 做多个 epoch。

## 4. Importance Sampling：旧轨迹上估新策略

数据来自 $\pi_{\mathrm{old}}$，目标却是 $\pi_\theta$。重要性权重

$$
\rho_t(\theta)=\frac{\pi_\theta(a_t\mid s_t)}{\pi_{\mathrm{old}}(a_t\mid s_t)}
$$

给出一阶 surrogate

$$
L(\theta)=\mathbb{E}_{t\sim\pi_{\mathrm{old}}}\big[\rho_t(\theta)\,\hat{A}_t\big].
$$

在 $\theta=\theta_{\mathrm{old}}$ 处 $\rho=1$，一阶导数与真实 on-policy 梯度相同，所以可以小步复用这批数据。一旦 $\rho$ 远离 1，少数样本支配估计，方差爆炸。这是「Importance Sampling 为什么成立？为什么 variance 会爆？」和「On-policy vs Off-policy；PPO/GRPO 为什么强调 Fresh Rollout？」在这条链上的位置。

缺陷：需要一种不让 $\theta$ 跑太远的机制，否则 surrogate 不再可信。

## 5. TRPO：硬信任域，PPO 的理论动机

TRPO 直接写约束：最大化 $L(\theta)$，同时 $D_{\mathrm{KL}}(\pi_{\mathrm{old}}\|\pi_\theta)\le\delta$。这是相对上一轮行为策略的正向 KL，保证新策略不能把旧策略认为好的动作概率压没。实现要共轭梯度、线搜索，工程重。

PPO 的贡献是：不要真的解带约束的二次规划，用 clip 把 surrogate 在「有利方向更新过头」时削平。

## 6. PPO：clip 近似信任域，RLHF 再加 drift KL

Clipped objective：

$$
L^{\mathrm{CLIP}}(\theta)=\mathbb{E}_t\left[\min\big(\rho_t\hat{A}_t,\ \mathrm{clip}(\rho_t,1-\varepsilon,1+\varepsilon)\hat{A}_t\big)\right].
$$

$\hat{A}_t>0$ 时限制 $\rho$ 不要过大；$\hat{A}_t\lt 0$ 时限制 $\rho$ 不要过小。Clip 的是目标函数，不是把真实概率比强制截进区间。符号效应见「PPO clipped objective 为什么长这样？」和百度真题卡。

接到 LLM 对齐时，还要第二套 KL。Clip / TRPO 管的是相对 $\pi_{\mathrm{old}}$ 的 Trust-Region；InstructGPT 式 PPO 还在奖励里减

$$
r_t\leftarrow r_\phi(x,y)-\beta\log\frac{\pi_\theta(y_t\mid x,y_{1:t-1})}{\pi_{\mathrm{ref}}(y_t\mid x,y_{1:t-1})},
$$

这是相对冻结 SFT 的 Drift，反向 $D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})$。两套 KL 不是同一个东西，见「PPO 里的 Trust-Region KL 和 Drift KL 是同一个东西吗？」。

四件套：Actor 被优化，Reference 冻结当锚，Reward Model 打分，Critic 出 $V$ 给 GAE。见「Actor、Reference、Reward Model、Critic 分别做什么？」。

缺陷：Critic 几乎和 Actor 一样大，要同步、会过拟合、长 CoT 上 $V(s)$ 难估。数学 / 代码这类同题可对比、奖励在序列末才出现的任务，逐步 bootstrap 用不上。

## 7. GRPO：组均值代替 $V_\psi$，clip 目标留下

同一 prompt $x$ 采 $G$ 条回复 $o_1,\ldots,o_G$，得到标量奖励 $r_1,\ldots,r_G$。组归一化

$$
\hat{A}_i=\frac{r_i-\mu}{\sigma+\epsilon},\qquad \mu=\frac1G\sum_j r_j
$$

当作这条回复里每个 token 共享的 advantage。PPO 的 clip 原样留下，$\rho$ 仍是 $\pi_\theta/\pi_{\mathrm{old}}$。DeepSeekMath 把相对 $\pi_{\mathrm{ref}}$ 的 KL 写成 $k_3$ 加进 loss，而不是扣进 reward。

这一步在改什么：不是发明新的策略梯度，而是换 baseline 的构造方式。PPO 用 learned $V^\pi(s)$ 减「这个前缀往后的期望回报」；GRPO 用「同一道题、这一组样本的经验均值」减「这条回复相对同题其它回复好多少」。组均值不是 Value Function，也没有逐步 future return。见「GRPO 是什么？为什么能去掉 Critic？」。

为什么在 reasoning RL 里合理：outcome reward 在 EOS 才出现，一条回复内部的 token 本来就共享同一个 $G$；同 prompt 的多条 rollout 天然构成对照。GAE 的逐步信用分配没有信息可挖，Critic 的成本就显得亏。

## 这条链上还没消失的约束

- **Fresh rollout 还在。** GRPO 仍然是（近似）on-policy，epoch 过多、ratio 偏离，$\rho$ 一样会炸。
- **Clip 还在。** 美团会问「GRPO 为什么还要 clip」：组 baseline 只换了 $A$，没有换信任域。
- **组全对 / 全错时 $\hat{A}=0$。** 没有相对信号，这一批是空梯度。PPO 的 Critic 在这种情况下仍可能给出非零 $A$，只是不一定对。
- **$\sigma$ 归一化不是免费的。** 它会改变不同题目的权重；Dr.GRPO 指出长度和 std 带来的偏置。RLOO 则用「不含自己的组均值」，更接近教科书 baseline。

我会把链收成：REINFORCE 给无偏梯度，baseline / $A$ 降方差，$V$+GAE 估 $A$，IS 复用旧轨迹，clip 限制 $\rho$ 得到 PPO，同题组统计换掉 $V$ 得到 GRPO。

面试若只问「PPO 和 GRPO 的公式差在哪」，先答：同一套 clipped IS 策略梯度；差在 advantage 从哪来，以及还要不要训 Critic。

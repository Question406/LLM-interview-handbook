---
id: fund-rl-bias-var-index
section: fundamentals
order: 145
level: A
title: RL 方差、无偏 / biased estimate 面试要准备哪些题？
quick: >-
  先说清「无偏」针对哪个目标：policy gradient、回报，还是 KL 标量。再按操作分类，减 state baseline、reward-to-go
  仍无偏；bootstrap、clip、除组标准差、self-normalized IS 是用偏差换方差。下面按这条链排。
tags:
  - RL
  - Bias-Variance
  - Policy Gradient
  - 真题导航
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: >-
      Simple Statistical Gradient-Following Algorithms for Connectionist
      Reinforcement Learning
    url: 'https://link.springer.com/article/10.1007/BF00992696'
    type: primary
  - title: High-Dimensional Continuous Control Using Generalized Advantage Estimation
    url: 'https://arxiv.org/abs/1506.02438'
    type: primary
  - title: IMPALA / V-trace
    url: 'https://arxiv.org/abs/1802.01561'
    type: primary
---

准备这块题，关键是每说一个估计「无偏」，都先讲清是相对哪个目标，policy gradient、回报，还是 KL 标量；然后按操作分两类，一类只改方差，一类拿偏差换方差。网上能对上的高频问法已经拆成了独立卡，总览在「Bias–Variance Tradeoff 在 RL 中有哪些具体例子？」，这一页只排「无偏还是有偏」这条链，点下面每一条就能跳到对应的题。

## 先分清无偏的对象

- Policy Gradient Theorem / REINFORCE 怎么从目标函数推出来？
- policy gradient 里哪些操作仍无偏？哪些会引入偏差？
- Policy Gradient 为什么可以减 Baseline？
- 为什么 $V^\pi(s)$ 是最优 baseline？$V$ 估错了梯度还无偏吗？
- Schulman 的 $k_1/k_2/k_3$ 各估什么？数值无偏和梯度正确是一回事吗？

这几张的共同点是先说清相对哪条期望。减只依赖 state 的 baseline，梯度期望不变；$V$ 估错了，只要不拿它当 bootstrap 去替换未来回报，MC 优势仍然无偏。KL 那边也一样，$k_3$ 作为标量无偏，不等于对 $\theta$ backpropagation 出来的就是 KL 梯度，见 `fund-kl-k1-k2-k3`。

## Return / Advantage：MC 无偏，TD 有偏

- Reward-to-go 为什么仍无偏？为什么比整段回报方差更小？
- 即使 on-policy，REINFORCE 的方差为什么仍随长度和稀疏奖励涨？
- $G_t-V(s_t)$ 和 GAE 差在哪？怎样用 Critic 降方差却保持无偏？
- $\gamma$ 和 $\lambda$ 为什么不能合成一个乘积？谁改目标、谁改估计器？
- 轨迹自然结束和 max-length 截断，bootstrap 各该怎么做、偏在哪？
- 阶跃星辰：GAE 是什么？Monte Carlo 和 TD 有何差别？
- 从 TD residual 推导 GAE，并解释 $\gamma$、$\lambda$
- 百度文心后训练：GAE 中 $\lambda$ 的作用，与偏差/方差如何权衡？
- Bias–Variance Tradeoff 在 RL 中有哪些具体例子？

这一组讲回报和优势。MC，也就是 $\lambda=1$，信的是轨迹，无偏，方差随长度涨；TD 或小 $\lambda$ 信的是 $V$，方差小，有 bootstrap 偏差。$\gamma$ 改的是任务的时间尺度，$\lambda$ 只改估计器。减 $V$ 仍无偏，用 $V$ 替未来才偏。

## 有限样本 baseline 与 normalization

- 组均值含当前样本、Leave-one-out、batch standardization，有限样本下谁还无偏？
- RLOO 和 GRPO 都不用 Critic，它们的 baseline 有什么关键区别？
- Advantage 减均值、除标准差、按长度 normalization，分别改了什么目标？
- Dr.GRPO 认为 vanilla GRPO 有哪些 bias？
- REINFORCE++ 怎么降方差？和 GRPO / PPO 的无偏性差在哪？
- 0-1 奖励的方差何时最大？这对 GRPO 有效组意味着什么？

减均值，不管是常数还是 state baseline，通常还在无偏族里；除 $\sigma$、按长度平均是在改目标里的权重。组太小、均值含自身、再除组标准差，偏差最明显。$p(1-p)$ 在两端为 0，组相对优势靠的是组内有方差，这里的方差并不是越小越好。

## sampling 图与三种 clip

- Score-function 和 reparameterization 差在哪？LLM 的 token 为什么只能走高方差那条？
- Gradient clip、Advantage clip、Ratio clip 分别偏了什么？

Token sampling 没法走低方差的 reparam。三种 clip 截的也是三个不同的量，分别是步长、$A$ 和 $\rho$。

## 复用旧数据：IS 无偏，截断 / self-normalization 有偏

- Importance Sampling 为什么成立？为什么 variance 会爆？
- Self-normalized IS 为什么有偏？ESS 怎么读？
- Per-decision IS 和整段轨迹 IS 哪个无偏？方差差在哪？
- Token 级 importance ratio 连乘为什么方差会指数爆？
- V-trace / 截断重要性权重为什么有偏？异步 LLM RL 为什么还用？
- CISPO 为什么 clip 的是 IS 权重，而不是 PPO 那样 clip surrogate？
- On-policy vs Off-policy；PPO/GRPO 为什么强调 Fresh Rollout？

普通 IS 无偏，但尾部会爆；PD-IS 同样无偏，少乘了未来的 $\rho$；WIS、clip、V-trace 拿偏差换能训的梯度。PPO 的逐步 $\rho_t A_t$ 是局部 surrogate，和 PD-IS 定理是两回事。

准备顺序是先会无偏梯度，再谈降方差，再谈复用旧数据。每用一个 trick，都要能说出牺牲了哪一块无偏性。

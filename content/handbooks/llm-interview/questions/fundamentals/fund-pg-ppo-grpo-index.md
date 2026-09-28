---
id: fund-pg-ppo-grpo-index
section: fundamentals
order: 3
level: A
title: Policy Gradient → PPO → GRPO 该按什么顺序学？
quick: >-
  先会 REINFORCE 的 $\nabla\log\pi\cdot G$，再减 baseline 得到 $A$，然后 GAE / Critic、importance
  sampling、TRPO 约束，最后才是 PPO clip 和 GRPO 的组相对优势。下面按这条链排，点击标题即可跳转。
tags:
  - Policy Gradient
  - PPO
  - GRPO
  - 真题导航
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-24
sources:
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: primary
  - title: DeepSeekMath / GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

网上对得上的高频问法已经拆成独立卡。主推导在「从 Policy Gradient 怎么一步步推到 PPO，再推到 GRPO？」，本页只给顺序。点下面每条就能跳到对应题。

## 梯度从哪来

- Policy Gradient Theorem / REINFORCE 怎么从目标函数推出来？
- Policy Gradient 为什么可以减 Baseline？
- 为什么 LLM 用 Actor-Critic，而不是纯 Critic / DQN？
- Bellman Equation、V、Q、Advantage 的关系？
- Entropy Regularization 和 Sampling Temperature 有什么区别？

## 无偏还是有偏、方差从哪来

导航总表见「RL 方差、无偏 / 有偏估计面试要准备哪些题？」。先会下面几张再谈 PPO clip。

- 策略梯度里哪些操作仍无偏？哪些会引入偏差？
- Reward-to-go 为什么仍无偏？为什么比整段回报方差更小？
- 即使 on-policy，REINFORCE 的方差为什么仍随长度和稀疏奖励涨？
- 为什么 $V^\pi(s)$ 是最优 baseline？$V$ 估错了梯度还无偏吗？
- $G_t-V(s_t)$ 和 GAE 差在哪？怎样用 Critic 降方差却保持无偏？
- $\gamma$ 和 $\lambda$ 为什么不能合成一个乘积？谁改目标、谁改估计器？
- 轨迹自然结束和 max-length 截断，bootstrap 各该怎么做、偏在哪？
- 组均值含当前样本、Leave-one-out、batch 标准化，有限样本下谁还无偏？
- Advantage 减均值、除标准差、按长度归一化，分别改了什么目标？
- Gradient clip、Advantage clip、Ratio clip 分别偏了什么？
- 0-1 奖励的方差何时最大？这对 GRPO 有效组意味着什么？
- Score-function 和 reparameterization 差在哪？LLM 的 token 为什么只能走高方差那条？
- Self-normalized IS 为什么有偏？ESS 怎么读？
- Per-decision IS 和整段轨迹 IS 哪个无偏？方差差在哪？
- Token 级 importance ratio 连乘为什么方差会指数爆？
- V-trace / 截断重要性权重为什么有偏？异步 LLM RL 为什么还用？
- REINFORCE++ 怎么降方差？和 GRPO / PPO 的无偏性差在哪？
- Bias–Variance Tradeoff 在 RL 中有哪些具体例子？

## 为什么不能直接对旧轨迹做多轮 SGD

- Importance Sampling 为什么成立？为什么 variance 会爆？
- On-policy vs Off-policy；PPO/GRPO 为什么强调 Fresh Rollout？
- 从 TD residual 推导 GAE，并解释 $\gamma$、$\lambda$
- Actor、Reference、Reward Model、Critic 分别做什么？

## PPO 本身

- 从 Policy Gradient 怎么一步步推到 PPO，再推到 GRPO？
- PPO clipped objective 为什么长这样？
- 百度文心 RL 后训练：PPO clip 在优势为正/负时分别限制哪一侧？
- PPO 里的 Trust-Region KL 和 Drift KL 是同一个东西吗？
- 蚂蚁一面：PPO 的 KL 能改成交叉熵吗？

## 换成组 baseline 之后

- GRPO 是什么？为什么能去掉 Critic？
- 美团北斗：项目里为什么选 GRPO 而不是 PPO 或 DPO？
- 美团秋招二面：GRPO 为什么还要 clip？SFT 后直接上会不会仍不稳定？
- 字节大模型算法：GRPO 一组全对或全错时为什么这一步不起作用？
- RLOO 和 GRPO 都不用 Critic，它们的 baseline 有什么关键区别？
- Dr.GRPO 认为 vanilla GRPO 有哪些 bias？
- 蚂蚁：GRPO 的 KL 和 PPO 有何不同？K1/K2/K3 是什么？
- Schulman 的 $k_1/k_2/k_3$ 各估什么？数值无偏和梯度正确是一回事吗？
- 相对 GRPO，SAPO / MaxRL / SimKO 各改哪一层？
- GFPO 怎么用组内过滤压长度膨胀？和 DAPO overlong 差在哪？
- 熵塌了先动哪几个旋钮？温度为什么排最后？
- 异步 / partial rollout 里的 TIS，和 CISPO 截断 IS 是一回事吗？
- MoE RL 的 Routing Replay（R2 / R3）和 Keep Routing、GSPO 各修哪一层？
- TRPO、DPPO、AReaL 各自怎么给 RL 目标加 trust region？
- 2026 RL 算法 / Infra 面试 35 题该按什么顺序准备？

准备顺序：先会无偏梯度，再谈降方差，再谈复用旧数据，最后才是「要不要 Critic」。方差 / 无偏专项见「RL 方差、无偏 / 有偏估计面试要准备哪些题？」。2026 社区 35 题对照见「2026 RL 算法 / Infra 面试 35 题该按什么顺序准备？」。

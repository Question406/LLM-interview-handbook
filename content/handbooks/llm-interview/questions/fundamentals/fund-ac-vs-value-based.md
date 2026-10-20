---
id: fund-ac-vs-value-based
section: fundamentals
order: 191
level: S
title: 为什么 LLM 用 Actor-Critic，而不是纯 Critic / DQN？
quick: "纯 Critic 要对 $10^5$ 级词表估 $Q(s,a)$ 再 argmax，还丢掉了可采样的策略。Actor 直接输出 $\\pi_\\theta$，Critic 只估 $V(s)$ 当 baseline 来降方差。"
tags:
  - Actor-Critic
  - Policy Gradient
  - LLM RL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Policy Gradient Methods for Reinforcement Learning with Function Approximation
    url: https://proceedings.neurips.cc/paper/1999/hash/464d828b85b0bed98e80ade0a5c43b0f-Abstract.html
    type: primary
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: primary
  - title: DeepSeekMath / GRPO
    url: https://arxiv.org/abs/2402.03300
    type: primary
---

常见误区是：把「为什么要 Critic」答成「因为 PPO 论文里有」。面试官问的是另一面：为什么不用纯 value-based。LLM 的动作是词表中的 token，状态是长上下文。直接使用 DQN 的方式既要处理很大的动作空间，也需要额外解决如何得到可采样的策略分布。

## 纯 Actor 方差太大

目标 $J(\theta)=\mathbb{E}_{\tau\sim\pi_\theta}[\sum_t\gamma^t r_t]$。Policy gradient 给出

$$
\nabla_\theta J=\mathbb{E}\big[\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,Q^\pi(s_t,a_t)\big].
$$

用整段 Monte Carlo 回报 $\hat Q_t=G_t$ 无偏，但一条长 思维链（CoT，即分步推理过程） 的噪声极大。同一状态下的普通动作和关键动作会被同一把标尺衡量。推导链见 `pt-pg-to-ppo-to-grpo`。

## Critic 只做 baseline，不当贪心策略

引入 $V^\pi(s)$ 后写 $A^\pi=Q^\pi-V^\pi$，梯度变成 $\mathbb{E}[\nabla\log\pi\cdot A]$。只依赖 state 的 $b(s)$ 满足

$$
\mathbb{E}_{a\sim\pi}\big[\nabla_\theta\log\pi_\theta(a\mid s)\,b(s)\big]=0,
$$

所以减 $V(s)$ 不改期望，只降方差。这就是 Actor-Critic：Actor 出分布，Critic 估价值。细节见 `fund-pg-baseline`。PPO 再在这套骨架上加 clip 和 GAE。

## 纯 Critic 在 LLM 上过不去

Value-based 方法学 $Q(s,a)$，执行时 $\arg\max_a Q$。三个硬伤：1. 每个前缀都要对 $|\mathcal{V}|$ 个 token 估 $Q$，词表 $10^5$ 量级。
2. 生成仍要一个随机策略。$\arg\max$ 丢掉多样性和可采样性，后面的 强化学习（RL） 探索、group sampling 都没了。
3. 语言是多峰的：同一题有多条正确链。贪心 $Q$ 会把概率质量压到一条表面上高分的路径。

所以 LLM post-training 几乎全是 policy-based。需要降方差时加 Critic（PPO）；同题可对比、奖励在序列末才出现时，组均值就能顶 baseline，于是 GRPO 去掉 learned $V$，见 `pt-grpo`。奖励模型（RM） 打分和 Critic 估未来回报不是同一个头，见 `ant-rm-vs-critic`。

Actor 直接建模 $\pi$，避免每步都依赖对所有动作的价值估计来生成；Critic 或组均值则作为 baseline，降低 Monte Carlo 回报带来的方差。

## 追问

- **GRPO 还算 Actor-Critic 吗？** 骨架仍是带 baseline 的策略梯度，只是 baseline 从 $V_\psi$ 换成同一输入提示 组统计。没有逐步 bootstrap，也没有逐步 $Q(s,a)$。
- **能不能对每个 token 训一个 $Q$ 头？** 工程上能共享 backbone，但目标仍是回归未来回报，不是拿 $\arg\max$ 当解码器。解码永远走 $\pi_\theta$。
- **baseline 依赖当前动作会怎样？** 期望会偏。组均值含自己有 $O(1/G)$ 收缩，见 `fund-finite-sample-baseline`。RLOO 用不含自己的均值，更接近教科书。

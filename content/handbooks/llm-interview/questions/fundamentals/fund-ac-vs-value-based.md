---
id: fund-ac-vs-value-based
section: fundamentals
order: 191
level: S
title: 为什么 LLM 用 Actor-Critic，而不是纯 Critic / DQN？
quick: "LLM 的动作是 $10^5$ 级词表里的 token，纯 Critic 要对每个前缀估所有 token 的 $Q(s,a)$ 再 argmax，还丢掉了可采样的随机策略。所以让 Actor 直接输出 $\\pi_\\theta$ 负责生成，Critic 只估 $V(s)$ 当 baseline 来降方差。"
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

因为 LLM 生成本来就需要一个能采样的策略分布，纯 value-based 给不了，还得对十万级的词表逐个估价值。所以让 Actor 直接输出 $\pi_\theta$ 负责生成，Critic 只估 $V(s)$ 当 baseline 来降方差。这题容易答成「因为 PPO 论文里有 Critic」，面试官问的是另一面：为什么不用纯 value-based、纯 DQN。LLM 的动作是词表里的 token，状态是长上下文，照搬 DQN 既要处理很大的动作空间，还得另外解决怎么得到可采样的策略分布。

先看纯 Actor 的问题。目标是 $J(\theta)=\mathbb{E}_{\tau\sim\pi_\theta}[\sum_t\gamma^t r_t]$，policy gradient 给出

$$
\nabla_\theta J=\mathbb{E}\big[\nabla_\theta\log\pi_\theta(a_t\mid s_t)\,Q^\pi(s_t,a_t)\big].
$$

用整段 Monte Carlo 回报 $\hat Q_t=G_t$ 是无偏的，但一条长思维链（CoT，即分步推理过程）的噪声极大。比如一道数学题推了很长一段，最后答对，每个 token 拿到的都是同一个回报，普通的过渡词和关键的那一步被同一把标尺衡量。推导链见 `pt-pg-to-ppo-to-grpo`。

解决办法是引入 $V^\pi(s)$，写成 $A^\pi=Q^\pi-V^\pi$，梯度变成 $\mathbb{E}[\nabla\log\pi\cdot A]$。只依赖 state 的 $b(s)$ 满足

$$
\mathbb{E}_{a\sim\pi}\big[\nabla_\theta\log\pi_\theta(a\mid s)\,b(s)\big]=0,
$$

所以减掉 $V(s)$ 不改变期望，只降方差。这就是 Actor-Critic：Actor 出分布，Critic 估价值，Critic 只做 baseline，不拿来当贪心策略。细节见 `fund-pg-baseline`，PPO 再在这套骨架上加 clip 和 GAE。

那为什么不干脆只用 Critic？Value-based 方法学 $Q(s,a)$，执行时取 $\arg\max_a Q$，放到 LLM 上有三个硬伤。一是每个前缀都要对 $|\mathcal{V}|$ 个 token 估 $Q$，词表是 $10^5$ 量级。二是生成仍然需要一个随机策略，$\arg\max$ 丢掉了多样性和可采样性，后面强化学习（RL）的探索、group sampling 都没了。三是语言是多峰的，同一道题有多条正确的推理链，贪心的 $Q$ 会把概率质量压到一条表面上高分的路径上。

所以 LLM post-training 几乎全是 policy-based：Actor 直接建模 $\pi$，生成时不用每一步都依赖对所有动作的价值估计；需要降方差时加 Critic（PPO）。同一题的多个回答可以互相比较、奖励又只在序列末尾才出现时，组均值就能顶替 baseline，于是 GRPO 去掉了 learned $V$，见 `pt-grpo`。另外，奖励模型（RM）打分和 Critic 估未来回报是两个不同的头，见 `ant-rm-vs-critic`。

## 追问

**GRPO 还算 Actor-Critic 吗？**
骨架仍是带 baseline 的策略梯度，只是 baseline 从 $V_\psi$ 换成了同一输入提示下的组统计。它没有逐步 bootstrap，也没有逐步的 $Q(s,a)$。

**能不能给每个 token 训一个 $Q$ 头？**
工程上可以共享 backbone，但这个头的目标是回归未来回报，不拿 $\arg\max$ 当解码器，解码永远走 $\pi_\theta$。

**baseline 依赖当前动作会怎样？**
期望会有偏。组均值里含了自己，会有 $O(1/G)$ 的收缩，见 `fund-finite-sample-baseline`；RLOO 用不含自己的均值，更接近教科书的做法。

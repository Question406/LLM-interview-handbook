---
id: fund-optimal-baseline
section: fundamentals
order: 147
level: S
title: 为什么 $V^\pi(s)$ 是最优 baseline？$V$ 估错了梯度还无偏吗？
quick: >-
  任意只依赖 $s$ 的 $b(s)$ 都不改策略梯度期望。在这类函数里，$b(s)=V^\pi(s)$ 使
  $A=G-V$ 尽量 centered，方差近似最小。$V$ 估错了，MC 的 $G_t-\hat V(s_t)$ 仍无偏，只是降方差变差；用错的
  $\hat V$ 去 bootstrap 才引入偏差。
tags:
  - RL
  - Policy Gradient
  - Baseline
  - Bias-Variance
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-20
sources:
  - title: Simple Statistical Gradient-Following Algorithms for Connectionist Reinforcement Learning (REINFORCE)
    url: https://link.springer.com/article/10.1007/BF00992696
    type: primary
  - title: Policy Gradient Methods for Reinforcement Learning with Function Approximation
    url: https://proceedings.neurips.cc/paper/1999/hash/464d828b85b0bed98e80ade0a5c43b0f-Abstract.html
    type: primary
---

陷阱是把「$V$ 不准所以梯度有偏」一句话讲完。要拆成两件事：**当 baseline 减**，和 **当 bootstrap 替换未来回报**。前者不要求 $V$ 正确；后者才把 critic 的误差写进期望。Baseline 恒等式见 `fund-pg-baseline`：

$$
\mathbb{E}_{a\sim\pi(\cdot\mid s)}\big[\nabla_\theta\log\pi_\theta(a\mid s)\,b(s)\big]=b(s)\,\nabla_\theta\sum_a\pi_\theta(a\mid s)=0.
$$

所以估计器 $\nabla\log\pi\cdot(G_t-b(s_t))$ 对任意函数 $b(s)$ 都无偏，包括常数、$V$、甚至一个乱写的 MLP——只要它不看当前 sampled $a_t$。

## 为什么「最优」是 $V^\pi$

无偏只保证期望对，不保证方差小。$G_t$ 把「这个 state 本来就好」和「这个 action 相对更好」混在一起。减去该 state 下回报的条件期望

$$
b^\star(s)=\mathbb{E}[G_t\mid s_t=s]=V^\pi(s)
$$

得到 advantage $A^\pi=Q^\pi-V^\pi$，在 $s$ 上均值为 0，去掉公共噪声。严格讲，最小化 $\mathrm{Var}(\nabla\log\pi\cdot(G-b(s)))$ 的 $b$ 是按 $\|\nabla\log\pi\|^2$ 加权的条件期望，不一定恰好等于 $V$；面试说 **$V$ 是自然 / 近优的 control variate** 即可，不必推加权式。实践上训一个 critic 去拟合 $V^\pi$，就是在估这条 baseline。

$b$ 一旦依赖当前动作，恒等式不再成立，除非再做 importance 或 leave-one-out 修正。这就是为什么不能把「这条回复自己的 reward」未经处理地当自己的 baseline，也是 RLOO 要留一只样本在组外的原因，见 `fund-finite-sample-baseline`。

## $V$ 估错了：减它仍无偏，用它截断才偏

记 $\hat V$ 是任意函数（欠拟合、滞后、甚至常数 0）。

- **MC advantage** $\hat A_t=G_t-\hat V(s_t)$。$\hat V(s_t)$ 仍只依赖 state，期望梯度不变。估错的代价是 **方差减得少**，甚至比不减更吵——不是偏差。
- **$n$-step / GAE** 把 $G_t$ 里尚未发生的回报换成 $\gamma^n\hat V(s_{t+n})$。$\hat V\neq V^\pi$ 时，这段替换的期望不是真优势，这才是偏差。$\lambda\to 0$ 越信 $\hat V$，$\lambda\to 1$ 越退回 MC。见 `pt-gae`、`stepfun-gae-mc-td`。

Actor-critic 面试常被追「那 critic 不准还能训吗」。答：能，PPO 天天这么干；你接受的是 GAE 的 bootstrap 偏差，换方差。$\hat V$ 系统性低估长思维链时，小 $\lambda$ 会把长思考的优势压掉——这是偏差已经主导，该加大 $\lambda$、换组相对、或先把 value 拟合终局，而不是加学习率。

兼容函数近似（critic 线性于 $\nabla\log\pi$ 特征）是另一句加分：此时即使 $Q$ 有近似误差，策略梯度在投影意义下仍对。LLM 里几乎没人真去构造兼容特征，不要把它说成 PPO 的实现细节。

## 追问

- **常数 baseline 合法吗？** 合法，全局减均值就是常数 $b$。降方差弱于 $V(s)$，因为没条件在 state 上。
- **RM 分数能当 $V$ 吗？** 不能直接代。RM 是标量奖励模型，critic 估的是从该 token 起的期望回报。见 `baidu-gae-lambda`。
- **GRPO 没有 $V$ 为什么还能降方差？** 同 prompt 多条 rollout 的均值是另一条 $b(s)$，state 粗粒度成了「这道题」。见 `pt-rloo-vs-grpo`。
- **$\hat V$ 过拟合当前 batch？** 若 $\hat V$ 偷看了 $a_t$ 或当前 $G_t$，baseline 条件被破坏，有限样本会偏。这是为什么 value 要 stop-gradient，且不要用同一条轨迹的 $G_t$ 既当目标又当减数而不做 LOO。

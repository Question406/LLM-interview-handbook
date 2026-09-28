---
id: fund-per-decision-is
section: fundamentals
order: 162
level: A
title: Per-decision IS 和整段轨迹 IS 哪个无偏？方差差在哪？
quick: >-
  两者在 support 覆盖时都无偏。整段 IS 用同一个 $w_{0:T}=\prod_{k=0}^T\rho_k$ 乘整条回报，后面的 $\rho$
  会污染早就该入账的 $r_t$。Per-decision 对第 $t$ 步奖励只乘 $w_{0:t}$，少乘未来的比，方差通常小得多。PPO 的逐步
  $\rho_t A_t$ 连这个也不是，只是 $\theta\approx\theta_{\mathrm{old}}$ 处的一阶 surrogate。
tags:
  - Importance Sampling
  - Off-policy
  - Bias-Variance
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Eligibility Traces for Off-Policy Policy Evaluation (Precup, Sutton, Singh, ICML 2000)
    url: https://mlanthology.org/icml/2000/precup2000icml-eligibility/
    type: primary
  - title: Safe and Efficient Off-Policy Reinforcement Learning (Retrace)
    url: https://arxiv.org/abs/1606.02647
    type: secondary
  - title: Proximal Policy Optimization Algorithms
    url: https://arxiv.org/abs/1707.06347
    type: secondary
---

错法：把 PPO 里每个 token 乘 $\rho_t$ 叫做「无偏 per-decision IS」。无偏 off-policy 评估要的是：行为策略 $\mu$ 上的样本，乘上从开头到该奖励为止的似然比，把测度改回 $\pi$。PPO 既不是整段 $w_{0:T}$，也不是严格的 per-decision，见 `fund-is`、`fund-token-is-var`。

## 整段：一个乘积管所有奖励

$$
\hat J_{\mathrm{traj}}=w_{0:T}\sum_{t=0}^T\gamma^t r_t,\qquad
w_{0:T}=\prod_{k=0}^T\rho_k,\quad
\rho_k=\frac{\pi(a_k\mid s_k)}{\mu(a_k\mid s_k)}.
$$

$\mathbb{E}_\mu[\hat J_{\mathrm{traj}}]=J(\pi)$（覆盖成立时），无偏。第 0 步的 $r_0$ 也被 $w_{0:T}$ 乘了，后面 token 漂了，早先已经到手的奖励跟着炸。$T$ 一大，$(1+\varepsilon)^T$ 的二阶矩见 `fund-token-is-var`。

## Per-decision：每笔奖励只乘到自己为止

$$
\hat J_{\mathrm{PD}}=\sum_{t=0}^T\gamma^t r_t\,w_{0:t},\qquad
w_{0:t}=\prod_{k=0}^t\rho_k.
$$

$r_t$ 在 $t$ 时刻已实现，之后的动作不再改变这笔奖励，后面的 $\rho_{t+1:T}$ 对它是噪声。可以证明 $\mathbb{E}_\mu[\hat J_{\mathrm{PD}}]$ 仍是 $J(\pi)$，故同样无偏，方差通常严格更小（少乘了独立于 $r_t$ 的未来比）。这是 off-policy 评估里该默认的那一档，不是「有偏的逐步近似」。

加权 / 自归一化、截断 $c_t=\min(1,\rho_t)$（Retrace / V-trace）在 per-decision 之上再动手，才开始偏，见 `fund-wis-ess`、`fund-vtrace`。

## PPO 的 $\rho_t A_t$ 是第三种东西

Surrogate $\mathbb{E}_\mu[\rho_t\hat A_t]$ 在 $\theta=\theta_{\mathrm{old}}$ 处对 $\theta$ 的导数等于 on-policy 梯度，离开这一点既偏也高方差。它没有把 $w_{0:t}$ 乘到早期奖励上：优势 $\hat A_t$ 已经是从 $t$ 起的量，再乘的是单步 $\rho_t$，不是前缀乘积。这是工程局部近似，不是 Precup 的 PD-IS 定理。GSPO 把单步 $\rho_t$ 收成序列几何平均，改粒度；CISPO 截断单步 $\rho$，改尾部。都不要说成「所以我们在做无偏 per-decision IS」。

异步 LLM 若真要无偏复用旧轨迹，应对每笔 token 奖励乘前缀 $w_{0:t}$ 再考虑截断；实践上几乎没人在长 CoT 上做完整 PD-IS，因为 $w_{0:t}$ 照样随 $t$ 爆。于是退回 fresh + 单步 $\rho$ + clip。三层要说清：整段无偏最高方；PD-IS 无偏较低方；PPO 局部有偏。

## 追问

- **Advantage 已经是 to-go，还要 PD-IS 吗？** 评估 $J$ 时，每笔 $r_t$ 用 $w_{0:t}$。优化时用 $\rho_t A_t$ 是另一套。不要把 $A_t$ 再乘一遍 $w_{0:t}$ 却声称那是 PPO。
- **WIS 能套在 PD-IS 上吗？** 能，逐步自归一化会再偏。OPE 里常见；在线 PPO 很少用。
- **和逐步 TD target 的 IS 呢？** V-trace 的 $\rho_t$ 截的是残差系数，$c_t$ 截的是回传，是 PD-IS 的截断版，有偏。
- **为什么不在 GRPO 上做整段 $w_{0:T}$？** $T$ 上千时 ESS 会掉到个位数。组相对已经在同 prompt 上对照，再乘爆掉的 $w$ 会让组内排序被一条极端比主导。

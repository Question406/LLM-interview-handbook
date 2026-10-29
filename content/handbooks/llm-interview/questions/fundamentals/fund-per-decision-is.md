---
id: fund-per-decision-is
section: fundamentals
order: 162
level: A
title: Per-decision IS 和整段轨迹 IS 哪个无偏？方差差在哪？
quick: "support 覆盖时两者都无偏，per-decision 的方差通常小得多。整段 IS 用同一个 $w_{0:T}=\\prod_{k=0}^T\\rho_k$ 乘整条回报，后面的 $\\rho$ 会污染早就该入账的 $r_t$；per-decision 对第 $t$ 步奖励只乘 $w_{0:t}$。PPO 的逐步 $\\rho_t A_t$ 两种都不是，只是 $\\theta\\approx\\theta_{\\mathrm{old}}$ 处的一阶 surrogate。"
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

两个都无偏，前提是 support 覆盖；per-decision IS 的方差通常小得多，因为每笔奖励只乘到它自己那一步为止的 likelihood ratio。容易说错的是 PPO：它给每个 token 乘一个 $\rho_t$，看着像「无偏 per-decision IS」，其实整段 $w_{0:T}$ 和严格的 per-decision 它都不是，见 `fund-is`、`fund-token-is-var`。

无偏的 off-policy 评估要做的事是：样本来自行为策略 $\mu$，给每笔奖励乘上从开头到这笔奖励为止的 likelihood ratio，把测度改回 $\pi$。两种做法的差别就在「乘到哪里为止」。

## 整段 IS：一个乘积管所有奖励

$$
\hat J_{\mathrm{traj}}=w_{0:T}\sum_{t=0}^T\gamma^t r_t,\qquad
w_{0:T}=\prod_{k=0}^T\rho_k,\quad
\rho_k=\frac{\pi(a_k\mid s_k)}{\mu(a_k\mid s_k)}.
$$

覆盖成立时 $\mathbb{E}_\mu[\hat J_{\mathrm{traj}}]=J(\pi)$，无偏。可第 0 步的 $r_0$ 也被 $w_{0:T}$ 乘了。比如一条回复开头已经拿到了一笔奖励，后面某个 token 在新旧策略下概率差很多，这个 $\rho$ 一乘，早就到手的那笔奖励也跟着炸。$T$ 一大，$(1+\varepsilon)^T$ 的二阶矩见 `fund-token-is-var`。

## Per-decision：每笔奖励只乘到自己为止

$$
\hat J_{\mathrm{PD}}=\sum_{t=0}^T\gamma^t r_t\,w_{0:t},\qquad
w_{0:t}=\prod_{k=0}^t\rho_k.
$$

$r_t$ 在 $t$ 时刻已经实现，之后的动作改变不了它，后面的 $\rho_{t+1:T}$ 对它只是噪声。可以证明 $\mathbb{E}_\mu[\hat J_{\mathrm{PD}}]$ 仍是 $J(\pi)$，所以同样无偏，方差通常严格更小，因为少乘了独立于 $r_t$ 的未来比率。它是 off-policy 评估里该默认用的那一档，本身没有做「有偏的逐步近似」。

在 per-decision 之上再做加权 / self-normalization，或者截断 $c_t=\min(1,\rho_t)$（Retrace / V-trace），才开始有偏，见 `fund-wis-ess`、`fund-vtrace`。

## PPO 的 $\rho_t A_t$ 是第三种东西

Surrogate $\mathbb{E}_\mu[\rho_t\hat A_t]$ 在 $\theta=\theta_{\mathrm{old}}$ 处对 $\theta$ 的导数等于 on-policy 梯度，离开这一点就既有偏又高方差。它没有把 $w_{0:t}$ 乘到早期奖励上：优势 $\hat A_t$ 已经是从 $t$ 起的量，再乘的是单步 $\rho_t$，用不到前缀乘积。这是工程上的局部近似，和 Precup 的 PD-IS 定理是两回事。GSPO 把单步 $\rho_t$ 收成序列几何平均，改的是粒度；CISPO 截断单步 $\rho$，改的是尾部。这两个也都别说成「所以我们在做无偏 per-decision IS」。

异步 LLM 训练如果真想无偏地复用旧轨迹，应该给每笔 token 奖励乘前缀 $w_{0:t}$，再考虑截断。实践中几乎没人在长 chain of thought（CoT）上做完整的 PD-IS，因为 $w_{0:t}$ 照样随 $t$ 爆炸，于是退回 fresh + 单步 $\rho$ + clip。面试时把三层说清楚：整段 IS 无偏但方差较高；PD-IS 仍无偏，方差通常较低；PPO 用局部近似，会引入偏差。

## 追问

**Advantage 已经是 to-go 了，还要 PD-IS 吗？**
看你在做什么。评估 $J$ 时，每笔 $r_t$ 乘 $w_{0:t}$；优化时用 $\rho_t A_t$，是另一套。别把 $A_t$ 再乘一遍 $w_{0:t}$，还说那是 PPO。

**WIS 能套在 PD-IS 上吗？**
能，逐步 self-normalization 之后会再引入偏差。这在 OPE 里常见，在线 PPO 很少用。

**逐步 TD target 的 IS 呢？**
V-trace 就是这类：$\rho_t$ 截的是残差系数，$c_t$ 截的是回传，相当于 PD-IS 的截断版，有偏。

**为什么不在 GRPO 上做整段 $w_{0:T}$？**
$T$ 上千时 ESS 会掉到个位数。组相对已经在同一 prompt 上做了对照，再乘一个爆掉的 $w$，组内排序会被一条极端比率主导。

---
id: fund-vtrace
section: fundamentals
order: 150
level: A
title: V-trace / 截断重要性权重为什么有偏？异步 LLM RL 为什么还用？
quick: >-
  V-trace 把逐步 IS 比截成 $\rho_t=\min(\bar\rho,\pi/\mu)$、$c_t=\min(\bar c,\pi/\mu)$ 再累进 TD
  残差。截断后期望不再等于 on-policy $V^\pi$，所以有偏；换来的是 $\rho$ 连乘不爆炸，actor 可以比
  learner 落后若干步。LLM 异步 / partial / 量化采样里的 TIS、CISPO 是同一思想，不是另一套魔法。
tags:
  - V-trace
  - Importance Sampling
  - Off-policy
  - Bias-Variance
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: IMPALA — Scalable Distributed Deep-RL with Importance Weighted Actor-Learner Architectures
    url: https://arxiv.org/abs/1802.01561
    type: primary
  - title: MiniMax-M1 (CISPO)
    url: https://arxiv.org/abs/2506.13585
    type: secondary
---

错法：把 V-trace 背成「IMPALA 的 value 公式」，说不出截断哪两个比、偏了什么、LLM 异步为什么要同一招。普通逐步 IS 无偏但

$$
\prod_{t=1}^T\frac{\pi(a_t\mid s_t)}{\mu(a_t\mid s_t)}
$$

随 $T$ 指数高方差，见 `fund-token-is-var`、`fund-is`。异步 actor-learner 里 $\mu$ 是几分钟前的 $\pi$，不截断则少数轨迹主宰梯度。V-trace 的回答是：接受偏差，换有界权重。

## 截断两个系数：$\rho$ 管残差，$c$ 管传多远

IMPALA 对 behavior $\mu$ 上的轨迹写

$$
\delta_t V=\rho_t\big(r_t+\gamma V(s_{t+1})-V(s_t)\big),\qquad
\rho_t=\min\big(\bar\rho,\,\pi(a_t\mid s_t)/\mu(a_t\mid s_t)\big),
$$

$$
v_s=V(s_s)+\sum_{t=s}^{s+n-1}\gamma^{t-s}\Big(\prod_{i=s}^{t-1}c_i\Big)\delta_t V,\qquad
c_t=\min\big(\bar c,\,\pi/\mu\big).
$$

$\rho_t$ 截的是这一跳 TD 残差该信多少：动作在 $\pi$ 下更可能，才让残差进 value。$c_t$ 截的是残差还能往回传几步，挡住连乘。通常 $\bar\rho\ge\bar c$（常见都取 1）。$\pi=\mu$ 且截断从不触发时，退回普通 $n$-step / GAE 目标；一旦 $\min$ 生效，$\mathbb{E}[v_s]\neq V^\pi(s)$，这就是偏差。$\bar\rho,\bar c$ 越小越稳、越偏；开到无穷回到无偏高方差 IS。

策略梯度一侧同样：用截断后的 $\rho$ 乘 advantage，而不是完整轨迹乘积。这和 PPO clip surrogate 不同，PPO 在有利方向上可以把梯度直接打成 0；V-trace / 截断 IS 是把系数封顶后仍然更新。CISPO 把 $\rho$ clip 再 `detach`，梯度走 $\log\pi$，是 LLM 版同一思想，见 `pt-cispo`。

## 为什么异步 LLM RL 还要用

Rollout 引擎（vLLM / SGLang）和训练图不是同一步 $\theta$：量化、partial 续写、fully-async 队列都会让轨迹生于旧权。完全重采最干净，但墙钟被 generate 绑死。工程上三条路并列：

- 丢掉过期轨迹（freshness / staleness 阈值）：偏成「只训够新的样本」，方差来自有效样本变少。
- Mask 旧 prefix：半截不进 loss，付了 decode 却不训。
- 截断 IS / TIS / V-trace：旧 token 留在 loss 里但权重封顶，有偏、可训。

slime 的 `--use-tis` 修的是采样策略与训练策略的分布隙，和 `algorithm.adv_estimator` 正交，见 `slime-advantage-estimator`。它代替不了 训练图重算 logp：TIS 管分布，recompute 管数值图。异步不是「可以 off-policy 所以更先进」，是用有偏估计买重叠；holdout 掉了先查 trajectory age 和 ESS，而不是加学习率。

Retrace（$c_t=\lambda\min(1,\pi/\mu)$）是同一族：把截断写进 eligibility trace。不必背名字，要能说「截断 IS 有偏、为了方差」。

## 追问

- **$\bar\rho=1$ 是什么意思？** 只让「当前策略更可能的动作」的残差完整进入；$\mu$ 爱走、$\pi$ 不爱走的动作，贡献被压到至多 1。偏的是低估某些 off-policy 动作的价值。
- **和 PPO clip 能叠吗？** 能，但两层都在改目标。先盯 $\rho$ 分位数：已经几乎全被 V-trace 截断，再叠紧 PPO clip，有效更新接近 0。
- **GSPO 还要 V-trace 吗？** GSPO 改 ratio **粒度**（序列几何平均），V-trace 改 **尾部截断**。长 CoT 上两者都在打连乘方差，正交，不必说成互替。
- **不截断、改用 WIS？** WIS 有限样本有偏且对覆盖差不敏感，见 `fund-wis-ess`。异步 stale 是系统性漂移，截断或丢弃更对症。
- **LLM 里的 TIS 就是 CISPO 吗？** 不是。TIS 的分母是行为策略 $\mu$；CISPO 的分母通常是 $\pi_{\mathrm{old}}$，截断后还 detach。见 `pt-tis-async`。

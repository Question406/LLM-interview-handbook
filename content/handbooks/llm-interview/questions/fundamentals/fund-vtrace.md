---
id: fund-vtrace
section: fundamentals
order: 150
level: A
title: V-trace / 截断重要性权重为什么有偏？异步 LLM RL 为什么还用？
quick: >-
  V-trace 把逐步 IS 比截成 $\rho_t=\min(\bar\rho,\pi/\mu)$、$c_t=\min(\bar c,\pi/\mu)$
  再累进 TD 残差，截断后期望不再等于 on-policy 的 $V^\pi$，所以有偏。换来的是 $\rho$ 连乘不爆炸，actor 可以比
  learner 落后若干步。LLM 异步 / partial / 量化 sampling 里的 TIS、CISPO 是同一思想，都在用偏差换取更稳定的估计。
tags:
  - V-trace
  - Importance Sampling
  - Off-policy
  - Bias-Variance
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: >-
      IMPALA — Scalable Distributed Deep-RL with Importance Weighted
      Actor-Learner Architectures
    url: 'https://arxiv.org/abs/1802.01561'
    type: primary
  - title: MiniMax-M1 (CISPO)
    url: 'https://arxiv.org/abs/2506.13585'
    type: secondary
---

V-trace 有偏，是因为它把重要性比截断了：$\rho_t$ 和 $c_t$ 都封了顶，截断一旦生效，估出来的值就不再等于 $V^\pi$。异步 LLM RL 还用它，是因为不截断的方差更要命。异步 actor-learner 里，$\mu$ 是几分钟前的 $\pi$，普通逐步 IS 虽然无偏，但

$$
\prod_{t=1}^T\frac{\pi(a_t\mid s_t)}{\mu(a_t\mid s_t)}
$$

随 $T$ 指数高方差（`fund-token-is-var`、`fund-is`），不截断的话，少数轨迹会主宰梯度。V-trace 的选择是接受偏差，换有界的权重。面试里光把它背成「IMPALA 的 value 公式」不够，要说得出截了哪两个比、偏了什么、LLM 异步训练为什么用的是同一招。

## 截断两个系数：$\rho$ 管残差，$c$ 管传多远

IMPALA 对 behavior 策略 $\mu$ 采到的轨迹写

$$
\delta_t V=\rho_t\big(r_t+\gamma V(s_{t+1})-V(s_t)\big),\qquad
\rho_t=\min\big(\bar\rho,\,\pi(a_t\mid s_t)/\mu(a_t\mid s_t)\big),
$$

$$
v_s=V(s_s)+\sum_{t=s}^{s+n-1}\gamma^{t-s}\Big(\prod_{i=s}^{t-1}c_i\Big)\delta_t V,\qquad
c_t=\min\big(\bar c,\,\pi/\mu\big).
$$

$\rho_t$ 截的是这一跳 TD 残差该信多少：动作在 $\pi$ 下更可能，才让残差进入 value。$c_t$ 截的是残差还能往回传几步，用来挡住连乘。通常 $\bar\rho\ge\bar c$，常见都取 1。$\pi=\mu$ 且截断从不触发时，它退回普通的 $n$-step / GAE 目标；一旦 $\min$ 生效，$\mathbb{E}[v_s]\neq V^\pi(s)$，这就是偏差。$\bar\rho,\bar c$ 越小越稳、也越偏，开到无穷就回到无偏但高方差的 IS。

policy gradient 那一侧也一样，用截断后的 $\rho$ 乘 advantage，不用完整轨迹的乘积。这和 PPO 的 clip surrogate 不同：PPO 在有利方向上越界时可以把梯度直接打成 0，V-trace 和截断 IS 是把系数封顶后照样更新。CISPO 把 $\rho$ clip 之后再 `detach`，梯度走 $\log\pi$，是 LLM 版的同一思想，见 `pt-cispo`。

## 为什么异步 LLM RL 还要用

Rollout 引擎（vLLM / SGLang）和训练图用的不是同一步的 $\theta$：量化、partial 续写、fully-async 队列，都会让轨迹出自旧权重。全部重采最干净，可实际耗时主要卡在生成上。比如一条长推理生成到一半，权重已经更新过了，这半条轨迹是扔掉、mask 掉，还是降权用，就对应工程上并列的三条路。

第一种是丢掉过期轨迹，按 freshness / staleness 设阈值，偏差变成「只训够新的样本」，方差来自有效样本变少。第二种是 mask 掉旧 prefix，半截不进损失（loss），等于付了逐 token 生成（decode）的成本却不训。第三种是截断 IS、TIS、V-trace，旧 token 仍参与 loss 计算但权重封顶，有偏，但能训。

slime 的 `--use-tis` 修的是 sampling 策略和训练策略之间的分布差距，和 `algorithm.adv_estimator` 正交，见 `slime-advantage-estimator`。它也代替不了在训练图里重算 logp：TIS 管分布，recompute 管数值图。异步也谈不上「能 off-policy 所以更先进」，它是接受估计偏差，好让 sampling 和训练重叠起来；holdout 掉了，先查 trajectory age 和 ESS，加学习率没用。

Retrace（$c_t=\lambda\min(1,\pi/\mu)$）是同一族，把截断写进了 eligibility trace。名字不用背，能说出「截断 IS 有偏，是为了方差」就行。

## 追问

**$\bar\rho=1$ 是什么意思？**
只让当前策略更可能选的动作的残差完整进入；$\mu$ 爱走、$\pi$ 不爱走的动作，贡献被压到至多 1。偏差体现在低估某些 off-policy 动作的价值。

**能和 PPO clip 叠着用吗？**
能，但两层都在改目标。先盯 $\rho$ 分位数：如果几乎全被 V-trace 截断了，再叠一个很紧的 PPO clip，有效更新就接近 0 了。

**用了 GSPO 还要 V-trace 吗？**
可以都用。GSPO 改的是 ratio 的**粒度**（序列几何平均），V-trace 改的是**尾部截断**。在长 chain of thought（CoT，即分步推理过程）上两者都在压连乘方差，彼此正交，谈不上谁替代谁。

**不截断，改用 WIS 行不行？**
不太对症。WIS 在有限样本下有偏，对覆盖差也不敏感，见 `fund-wis-ess`。异步 stale 是系统性漂移，截断或丢弃更对症。

**LLM 里的 TIS 就是 CISPO 吗？**
不是。TIS 的分母是行为策略 $\mu$；CISPO 的分母通常是 $\pi_{\mathrm{old}}$，截断后还要 detach，见 `pt-tis-async`。

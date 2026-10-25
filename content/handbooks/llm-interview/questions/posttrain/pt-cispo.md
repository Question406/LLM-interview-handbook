---
id: pt-cispo
section: posttrain
order: 21
level: S
title: CISPO 为什么 clip 的是 IS 权重，而不是 PPO 那样 clip surrogate？
quick: "PPO 的 clipped surrogate 会让越界 token 的梯度直接变 0。CISPO 只把 IS 权重截断并 detach，损失是 $\\mathrm{sg}(\\hat r_t)\\hat A_t\\log\\pi_\\theta$，每个 token 都还有梯度，过大的比率只是被封顶了系数。"
tags:
  - CISPO
  - GRPO
  - MiniMax
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: MiniMax-M1 (CISPO)
    url: https://arxiv.org/abs/2506.13585
    type: primary
---

因为 PPO 那样 clip surrogate，越界 token 的梯度会直接变成 0，CISPO 想把这些 token 留住。它只把 importance sampling（IS）权重截断并 detach，梯度始终走 $\log\pi$，过大的比率只是系数被封了顶。它仍然是 REINFORCE / GRPO 组优势那一套，改的只是 off-policy 权重怎么截断，别把它背成一个毫不相干的第四种算法。

## PPO clip 丢掉了哪些 token

PPO / GRPO 的 clipped surrogate 是

$$
\min\big(\rho_t A_t,\;\mathrm{clip}(\rho_t,1-\varepsilon,1+\varepsilon)A_t\big).
$$

$\rho_t$ 一旦越出区间、而且处在「有利方向」，这一项对 $\theta$ 的梯度就是 0，这个 token 本轮不贡献梯度。比如一条长推理里有个低概率的关键转折词，策略刚开始学会它，$\rho$ 很快冲过 $1+\varepsilon$，它就被 clip 掉，不再被强化。长 思维链（CoT，即分步推理过程）、多轮 off-policy reuse 时，这类 token 更容易被丢掉，熵和探索会跟着塌。

## CISPO 怎么改

CISPO 回到带 IS 校正的 REINFORCE，只截断权重：

$$
\hat r_t=\mathrm{clip}\big(\rho_t,\;1-\varepsilon_{\mathrm{low}}^{\mathrm{IS}},\;1+\varepsilon_{\mathrm{high}}^{\mathrm{IS}}\big),
$$

$$
\mathcal{J}_{\mathrm{CISPO}}=\mathbb{E}\Big[\frac{1}{\sum_i|o_i|}\sum_{i,t}\mathrm{sg}(\hat r_{i,t})\,\hat A_{i,t}\log\pi_\theta(o_{i,t}\mid q,o_{i,1:t-1})\Big].
$$

$\mathrm{sg}(\cdot)$ 让 $\hat r$ 当常数处理，所以所有 token 都有梯度，过大的 $\rho$ 只是被封了顶，方差不会爆。没有 clip 时，上式就是 token-level 的 IS-REINFORCE。advantage 仍用 GRPO 的组相对优势，损失（loss） 按 token 平均，和 DAPO / Dr.GRPO 的 token-level 聚合一致；论文默认不加 KL。MiniMax-M1 的实验里常把 $\varepsilon_{\mathrm{low}}^{\mathrm{IS}}$ 放得很宽，主要调上界。

和 GSPO 放在一起对照：

| | clip 对象 | 粒度 | 被 clip 掉的是 |
| --- | --- | --- | --- |
| PPO / GRPO | surrogate $\rho A$ | token | 越界 token 的整段梯度 |
| GSPO | sequence likelihood ratio | 序列 | 局部 token 噪声被几何平均压掉 |
| CISPO | IS 权重 $\rho$，且 detach | token | 只封顶系数，梯度仍在 |

GSPO 改的是 ratio 的计算粒度，CISPO 改的是 clip 的对象。slime 里 `--advantage-estimator cispo` 只是同一套 采样轨迹（rollout） 换了 loss，采样方式没变。

## 追问

**CISPO 有偏吗？**
有。权重被截断以后，期望就不再严格等于 on-policy 梯度，换来的是稳定性和「不丢 token」。

**$\varepsilon_{\mathrm{high}}$ 为什么比 PPO 的 $0.2$ 大？**
这里它只决定系数封顶在哪，可以放松一些；PPO 的 $\varepsilon$ 直接决定这个 token 还有没有梯度。实现里常见的写法是把 ratio clamp 到 $[0, 1+\varepsilon_{\mathrm{high}}]$。

**手写怎么写？**
`w = (pi_logp - old_logp).exp().clamp(max=1+eps).detach()`，再算 `-w * A * pi_logp`，乘上 response mask 后按 token 平均。

**和异步里的 TIS 是一回事吗？**
两回事。CISPO 修的是 clip 的形状，分母是 $\pi_{\mathrm{old}}$；TIS 修的是行为策略 $\mu$，见 `pt-tis-async`。别答成同一个开关。

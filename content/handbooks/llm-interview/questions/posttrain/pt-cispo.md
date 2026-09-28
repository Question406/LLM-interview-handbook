---
id: pt-cispo
section: posttrain
order: 21
level: S
title: CISPO 为什么 clip 的是 IS 权重，而不是 PPO 那样 clip surrogate？
quick: >-
  CISPO 把 $r_t=\pi_\theta/\pi_{\mathrm{old}}$ 截断后 detach 成常数系数，损失仍是
  $\mathrm{sg}(\hat r_t)\hat A_t\log\pi_\theta$。每个 token 都有 $\nabla\log\pi$ 梯度；PPO/GRPO
  的 $\min(\rho A,\mathrm{clip}(\rho)A)$ 会让越出 clip 区间的 token 梯度变 0。
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

错法：背成第四种完全无关的算法。CISPO 仍是 REINFORCE / GRPO 组优势，只是 off-policy 权重的截断方式换了。

## 它在修 PPO clip 的哪个缺陷

PPO / GRPO 的 clipped surrogate 是

$$
\min\big(\rho_t A_t,\;\mathrm{clip}(\rho_t,1-\varepsilon,1+\varepsilon)A_t\big).
$$

$\rho_t$ 一旦越出区间且处在「有利方向」，该项对 $\theta$ 的梯度为 0：这个 token 本轮被扔掉。长 CoT、多轮 off-policy reuse 时，低概率但关键的推理 token 更容易被 clip 掉，熵和探索会塌。

CISPO 回到带 IS 校正的 REINFORCE，只截断权重：

$$
\hat r_t=\mathrm{clip}\big(\rho_t,\;1-\varepsilon_{\mathrm{low}}^{\mathrm{IS}},\;1+\varepsilon_{\mathrm{high}}^{\mathrm{IS}}\big),
$$

$$
\mathcal{J}_{\mathrm{CISPO}}=\mathbb{E}\Big[\frac{1}{\sum_i|o_i|}\sum_{i,t}\mathrm{sg}(\hat r_{i,t})\,\hat A_{i,t}\log\pi_\theta(o_{i,t}\mid q,o_{i,1:t-1})\Big].
$$

$\mathrm{sg}(\cdot)$ 让 $\hat r$ 当常数。梯度始终走 $\log\pi$，所有 token 都贡献；过大的 $\rho$ 只是把系数封顶，避免方差爆炸。MiniMax-M1 实验里常把 $\varepsilon_{\mathrm{low}}^{\mathrm{IS}}$ 放得很宽，主要调上界。

没有 clip 时，上式就是 token-level 的 IS-REINFORCE。Advantage 仍用 GRPO 组相对；loss 按 token 平均（和 DAPO / Dr.GRPO 的 token-level 聚合一致）。论文里默认不加 KL。

## 和 GSPO 怎么分

| | clip 对象 | 粒度 | 被 clip 掉的是 |
| --- | --- | --- | --- |
| PPO / GRPO | surrogate $\rho A$ | token | 越界 token 的整段梯度 |
| GSPO | sequence likelihood ratio | 序列 | 局部 token 噪声被几何平均压掉 |
| CISPO | IS 权重 $\rho$，且 detach | token | 只封顶系数，梯度仍在 |

现场口诀：GSPO 换 ratio 的粒度；CISPO 换 clip 的对象。slime 里 `--advantage-estimator cispo` 只是同一套 rollout 换 loss，不是另一套采样。

## 追问

- **有偏吗？** 有。权重被截断后期望不再严格等于 on-policy 梯度，换稳定性和「不丢 token」。
- **$\varepsilon_{\mathrm{high}}$ 为什么比 PPO 的 $0.2$ 大？** 系数封顶可以更松；PPO 的 $\varepsilon$ 直接决定要不要梯度。实现里常见把 ratio clamp 到 $[0, 1+\varepsilon_{\mathrm{high}}]$。
- **手写？** `w = (pi_logp - old_logp).exp().clamp(max=1+eps).detach()`，再 `-w * A * pi_logp`，乘 response mask 后按 token 平均。
- **和异步 TIS？** CISPO 修 clip 形状，分母是 $\pi_{\mathrm{old}}$。TIS 修行为策略 $\mu$，见 `pt-tis-async`。不要答成同一个开关。

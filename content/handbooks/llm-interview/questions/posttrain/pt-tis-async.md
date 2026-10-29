---
id: pt-tis-async
section: posttrain
order: 255
level: S
title: 异步 / partial rollout 里的 TIS，和 CISPO 截断 IS 是一回事吗？
quick: >-
  是两回事。TIS 的分母是引擎 sampling 时的行为策略 $\mu$，截断后当权重，修正异步 / partial 带来的 off-policy
  数据；CISPO 的分母是 $\pi_{\mathrm{old}}$，修的是 PPO clip 把越界 token 的梯度打成 0。两者可以同时开。
tags:
  - TIS
  - CISPO
  - Off-policy
  - slime
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-24T00:00:00.000Z
sources:
  - title: IMPALA / V-trace
    url: 'https://arxiv.org/abs/1802.01561'
    type: primary
  - title: MiniMax-M1 (CISPO)
    url: 'https://arxiv.org/abs/2506.13585'
    type: primary
  - title: slime 使用文档
    url: 'https://thudm.github.io/slime/zh/get_started/usage.html'
    type: primary
---

两者是两回事，区别在 $\rho$ 的分母。TIS 的分母是引擎 sampling 时的行为策略 $\mu$，管的是「这批数据从哪来」；CISPO 的分母是训练图上的 $\pi_{\mathrm{old}}$，管的是「PPO clip 把越界 token 的梯度掐死了」。所以别把 `--use-tis` 说成「就是 CISPO」，面试时先问清 $\rho$ 的分母是引擎的行为策略，还是 trainer 重算的旧策略。

为什么会有 $\mu$ 和 $\pi_{\mathrm{old}}$ 两个分布？异步、partial、量化的 sampling 轨迹（rollout）都会让 sampling 分布 $\mu$ 和训练图上的 $\pi_{\mathrm{old}}$ 对不上，见 `sys-partial-kv-policy`、`slime-dynamic-partial`。比如一条 partial rollout 前半段是旧权重采的、后半段是新权重采的，trainer 重算出的 $\pi_{\mathrm{old}}$ 就不是当初真正产生这些 token 的分布。

## TIS 校正行为策略

Truncated importance sampling 来自 off-policy actor-critic，V-trace 就是把 IS 截断再 bootstrap，见 `fund-vtrace`。在 LLM RL 里常简化成对每个 token 算

$$
\rho_t=\mathrm{clip}\Big(\frac{\pi_\theta(a_t\mid s_t)}{\mu(a_t\mid s_t)},\,0,\,\bar\rho\Big),
$$

这里的 $\mu$ 是 generate 时引擎记下的概率（或旧 checkpoint）。clip 是为了防止个别 token 把整段梯度炸掉。slime 里 `--use-tis` 和 `--mask-offpolicy-in-partial-rollout` 是两条腿，一个给旧段降权，一个直接不训旧段。没有 TIS 又把 $\rho$ 写成 1，等于拿错误条件分布的样本当 on-policy 用。ESS 掉、clip fraction 乱跳的时候，先画 version 和引擎-训练之间的 KL，见 `fund-wis-ess`、`sys-staleness`。

## CISPO 校正 clip 的形状

CISPO 把 $r_t=\pi_\theta/\pi_{\mathrm{old}}$ 截断后 detach，损失仍然乘 $\log\pi_\theta$，这样越界的 token 也还有梯度，见 `pt-cispo`。它的分母通常是训练图上的 $\pi_{\mathrm{old}}$，要解决的是 PPO 的 min 会把探索 token 的梯度掐死，跟引擎和 trainer 一致不一致没关系。放在一起看：

| | 分母 | 截断之后 |
| --- | --- | --- |
| TIS | 行为策略 $\mu$（引擎 / 旧权） | 权重，防 off-policy 爆炸 |
| CISPO | $\pi_{\mathrm{old}}$（常为重算） | detach 系数，梯度仍走 $\log\pi$ |
| PPO clip | $\pi_{\mathrm{old}}$ | 越界则该项梯度 0 |

两者可以同时开，TIS 管数据来源，CISPO 管更新步允许多猛。也有不同意见，DPPO 认为 CISPO 等于放弃了信任域，见 `pt-dppo-areal-trust-region`。面试时先承认有两套 $\rho$，再谈叠不叠。

## 追问

**已经重算了 logp，还需要 TIS 吗？**
需要。重算让分子分母走同一个 kernel，修的是数值上的差距。partial / 异步留下的仍然是旧 $\theta$ 采出来的 token，TIS 或 mask 还得有。

**截断是有偏的吗？**
是，用偏差换方差。$\bar\rho$ 太小，等于几乎只在 on-policy 时才更新；太大，等于没截。

**和 AReaL 按版本过滤有什么区别？**
过滤是 mandatory checks 槛，TIS 是软权重。队列太长时先丢最旧的，剩下的再做 TIS，见 `sys-areal-vs-slime`。

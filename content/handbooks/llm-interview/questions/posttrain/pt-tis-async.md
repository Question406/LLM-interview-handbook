---
id: pt-tis-async
section: posttrain
order: 255
level: S
title: 异步 / partial rollout 里的 TIS，和 CISPO 截断 IS 是一回事吗？
quick: >-
  不是。TIS 修的是「这条轨迹是谁采的」：引擎 logp、旧权、半截 token 相对当前 $\pi_\theta$ 的
  $\rho$，截断后当权重，避免假装 on-policy。CISPO 修的是 PPO clip 把越界 token 梯度打成
  0，对象仍是 $\pi_\theta/\pi_{\mathrm{old}}$ 的 surrogate。一个管行为策略，一个管 clip 形状。
tags:
  - TIS
  - CISPO
  - Off-policy
  - slime
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-24
sources:
  - title: IMPALA / V-trace
    url: https://arxiv.org/abs/1802.01561
    type: primary
  - title: MiniMax-M1 (CISPO)
    url: https://arxiv.org/abs/2506.13585
    type: primary
  - title: slime 使用文档
    url: https://thudm.github.io/slime/zh/get_started/usage.html
    type: primary
---

异步、partial、量化 rollout 都会让采样分布 $\mu$ 不等于训练图上的 $\pi_{\mathrm{old}}$，见 `sys-partial-kv-policy`、`slime-dynamic-partial`。别把 `--use-tis` 说成「就是 CISPO」。先问 $\rho$ 的分母是引擎行为策略，还是 trainer 重算的旧策略。

## TIS：校正行为策略

Truncated importance sampling 来自 off-policy actor-critic（V-trace 把 IS 截断再 bootstrap，见 `fund-vtrace`）。LLM RL 里常简化成：对每个 token

$$
\rho_t=\mathrm{clip}\Big(\frac{\pi_\theta(a_t\mid s_t)}{\mu(a_t\mid s_t)},\,0,\,\bar\rho\Big),
$$

$\mu$ 是 **generate 时引擎记下的概率**（或旧 checkpoint）。clip 防止个别 token 把整段梯度炸掉。slime 的 `--use-tis` 和 `--mask-offpolicy-in-partial-rollout` 是两条腿：一个降权，一个直接不训旧段。

没有 TIS 又把 $\rho$ 写成 1，等于用错误条件分布的样本当 on-policy。ESS 掉、clip fraction 乱跳时，先画 version / 引擎-训练 KL，见 `fund-wis-ess`、`sys-staleness`。

## CISPO：校正 clip 形状

CISPO 的 $r_t=\pi_\theta/\pi_{\mathrm{old}}$ 截断后 **detach**，损失仍乘 $\log\pi_\theta$，越界 token 还有梯度，见 `pt-cispo`。分母通常是训练图上的 $\pi_{\mathrm{old}}$，目的不是「引擎和 trainer 不一致」，而是「PPO min 会把探索 token 梯度掐死」。

| | 分母 | 截断之后 |
| --- | --- | --- |
| TIS | 行为策略 $\mu$（引擎 / 旧权） | 权重，防 off-policy 爆炸 |
| CISPO | $\pi_{\mathrm{old}}$（常为重算） | detach 系数，梯度仍走 $\log\pi$ |
| PPO clip | $\pi_{\mathrm{old}}$ | 越界则该项梯度 0 |

可以同时开：TIS 管「这批数据从哪来」，CISPO 管「更新步允许多猛」。DPPO 认为 CISPO 等于放弃信任域，见 `pt-dppo-areal-trust-region`。面试先承认两套 $\rho$，再谈叠不叠。

## 追问

- **重算 logp 了还要 TIS 吗？** 重算让分子分母进同一 kernel，修的是数值隙。partial / 异步留下的仍是 **旧 $\theta$ 采的 token**，TIS 或 mask 还要。
- **截断是有偏的吗？** 是。换方差。$\bar\rho$ 太小等于几乎 on-policy 才更新；太大等于没截。
- **和 AReaL 按版本过滤？** 过滤是硬门槛；TIS 是软权重。队列太长先丢最旧的，剩下的再 TIS，见 `sys-areal-vs-slime`。

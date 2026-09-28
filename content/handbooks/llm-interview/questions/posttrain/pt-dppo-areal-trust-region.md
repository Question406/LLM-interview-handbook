---
id: pt-dppo-areal-trust-region
section: posttrain
order: 251
level: S
title: TRPO、DPPO、AReaL 各自怎么给 RL 目标加 trust region？
quick: >-
  TRPO 对 $D_{\mathrm{KL}}(\pi_{\mathrm{old}}\|\pi_\theta)$ 硬约束，二阶、难 scale。PPO clip 用单点
  $\rho$ 冒充总变差，词表长尾上会过罚低频 token、欠约束高频 token。2026 的 DPPO（Divergence PPO）改成估 TV / KL
  再 mask。AReaL 的约束在样本年龄：过旧轨迹过滤或降权，不是改 clip 公式。
tags:
  - TRPO
  - DPPO
  - AReaL
  - Trust Region
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Trust Region Policy Optimization
    url: https://arxiv.org/abs/1502.05477
    type: primary
  - title: Rethinking the Trust Region in LLM Reinforcement Learning
    url: https://arxiv.org/abs/2602.04879
    type: primary
  - title: AReaL
    url: https://arxiv.org/abs/2505.24298
    type: primary
---

两套 KL 的锚点见 `pt-trust-region-vs-drift-kl`。本题问的是**近端约束怎么落地**：硬 KL、ratio clip、散度 mask、还是异步样本的年龄。2026 社区 35 题里的 DPPO，默认是 Divergence Proximal Policy Optimization（`2602.04879`），不是 Distributed PPO，也不是把 IS 和 clip 拆开的 Decoupled PPO。名字撞了先问对方。

## TRPO：约束写在分布上

$$
\max_\theta\ L_{\pi_{\mathrm{old}}}(\pi_\theta)\quad\text{s.t.}\quad
\mathbb{E}_s\big[D_{\mathrm{KL}}(\pi_{\mathrm{old}}(\cdot\mid s)\,\|\,\pi_\theta(\cdot\mid s))\big]\le\delta.
$$

约束的是**整份条件分布**的 KL，不是某一个被采样 token 的 $\rho$。实现走 Fisher / 共轭梯度，大词表 LLM 基本不用。PPO 用 $\mathrm{clip}(\rho,1-\varepsilon,1+\varepsilon)$ 做一阶工程近似，见 `pt-ppo-clip`。

## PPO clip 为什么在 LLM 上歪

$|\rho-1|\le\varepsilon$ 相当于用一个被采样 token 的比去估总变差。低频探索 token 的 $\rho$ 噪声大，容易被 clip 掉，正是 CISPO / clip-higher 想救的那类 token，见 `pt-cispo`、`pt-dapo`。高频 token 的 $\rho$ 靠近 1，分布漂移可能已经很大，clip 却放行。所以 clip 不是「算过 KL」，只是 noisy Monte Carlo。

## DPPO：直接估散度再 mask

Divergence PPO 仍用策略梯度 surrogate，但进出信任域的判据换成 TV 或 KL 的估计，而不是 $|\rho-1|$。词表太大，精确散度吃显存，论文用 **Binary**（把质量拆成「被采样 token vs 其余」）和 **Top-$K$** 近似。mask 是非对称的：只挡「已经在往域外走」的更新，不挡把 $\rho$ 往 1 拉回来的步。VeRL 文档里有 Binary-TV / Binary-KL 实现。

两句口令：trust region 必须锚在**行为策略 / 引擎采样分布** $\mu$，不要锚在训练图重算出来的 $\pi_{\mathrm{old}}$；没有信任域的 CISPO / 纯 IS，训推 mismatch 会累积到崩。Drift KL 相对冻结 $\pi_{\mathrm{ref}}$，仍是另一列，不要和 DPPO 的一步约束合成一个 $\beta$。

## AReaL：约束的是样本有多旧

AReaL 要解的是同步 RL 等长尾、生成与训练互斥，见 `sys-areal-vs-slime`。Fully async 之后，一个 batch 里混多个 policy 版本。它的「trust region」是**staleness-aware**：版本差太大的轨迹丢掉或降权，打断生成时 flush KV，见 `sys-partial-kv-policy`、`sys-staleness`。改的是数据准入，不是把 $\rho$ 换成 TV。

| | 约束对象 | 典型实现 |
| --- | --- | --- |
| TRPO | 分布 KL | 二阶、硬 $\delta$ |
| PPO / GRPO | 单点 $\rho$ | clip |
| DPPO | 估出来的 TV / KL | 动态 mask |
| AReaL | 样本年龄 / 版本 | 过滤、加权、打断续写 |

## 追问

- **DPPO 和 CISPO 谁还留着信任域？** CISPO 越界后仍回传 $\nabla\log\pi$，等于放弃近端。DPPO 认为这正是 mismatch 累积的原因。一个救低频 token 的梯度，一个救分布约束。
- **低学习率还要信任域吗？** DPPO 论文的 takeaway 是要。$10^{-6}$ 挡不住训推数值隙在多步里叠起来。
- **Distributed PPO 怎么讲？** 那是系统：采样和更新并行。放到框架题，见 `sys-llm-rl-framework-index`。别和 Divergence PPO 抢缩写。

---
id: pt-r3-routing-replay
section: posttrain
order: 254
level: S
title: MoE RL 的 Routing Replay（R2 / R3）和 Keep Routing、GSPO 各修哪一层？
quick: >-
  训推两套图的 top-$k$ 对不上，$\rho$ 就不是同一条计算图上的比。Keep Routing / R3 把 rollout
  引擎记下的专家路径在训练图重放，对准的是离散路由。GSPO 把 $\rho$ 提到序列级，减轻 token
  级路由噪声，但对齐不了走错的专家。R2 重放的是训练引擎用旧策略算出的专家，修不了引擎数值隙。
tags:
  - MoE
  - Routing Replay
  - GSPO
  - GRPO
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-24
sources:
  - title: Stabilizing MoE Reinforcement Learning by Aligning Training and Inference Routers
    url: https://arxiv.org/abs/2510.11370
    type: primary
  - title: Stabilizing Reinforcement Learning with LLMs — Formulation and Practices
    url: https://arxiv.org/abs/2512.01374
    type: primary
  - title: DeepSeek-V3.2
    url: https://arxiv.org/abs/2512.02556
    type: primary
---

MoE 训推不一致会怎样，见 `sys-moe-train-infer-routing-mismatch`。本题问的是 **RL 更新这一步怎么把路由钉住**。字节会从 GSPO 切入，见 `byte-moe-rollout-routing-gspo`；DeepSeek V3.2 写的是 Keep Routing。名字不同，先画三层：路由集合、token 级 $\rho$、策略版本。

## 为什么 MoE 上 $\rho$ 特别脆

Router 是离散 top-$k$。引擎（vLLM / SGLang、量化、不同 batch）和 trainer（Megatron / FSDP、另一套 kernel）对同一前缀可以选出不同 expert。后面的 hidden 已经不在同一个子网络上，$\log\pi$ 不是同一条函数。token 级 $\rho=\pi_\theta/\pi_{\mathrm{old}}$ 再连乘，局部路由翻转会被放大成训练崩。监控训推 KL、以及「$\rho$ 偏离 2 倍的 token 比例」，比只看 reward 更早报警。

## 三条药，不要说成一种

1. **Keep Routing / Rollout Routing Replay（R3）。** 采样时把推理引擎的专家 id（或路由 mask）记下来，训练 forward **强制走同一条 top-$k$**。同时修：引擎与训练图的实现隙，以及策略已更新带来的路由漂。DeepSeek 从 V3-0324 起把它当 MoE RL 稳定术，见 `pt-deepseek-rl-lineage`。Qwen（`2512.01374`）里 R3 对应 Ma et al. 的 Rollout Routing Replay。
2. **Vanilla Routing Replay（R2）。** 重放的是 **训练引擎** 用旧策略自己算出的专家。能减 mini-batch 更新带来的 staleness，但 **假定训练图和引擎已经一致**。中等 off-policy 时 Qwen 实验里 R2 往往够；训推 KL 大、off-policy 再加大时必须 R3。
3. **GSPO。** 不改路由。序列级 likelihood ratio 对个别 token 的专家跳变更不敏感，见 `pt-gspo`。路由已经错了，序列 $\rho$ 仍是错专家上的平均。

TIS / 重算 logp 修的是概率数值，不是离散 top-$k$。可以叠：先对齐路由，再截断 $\rho$，见 `pt-tis-async`。

GSPO 降方差，Replay 对齐计算图。路由都错了先不要换 clip。

## 追问

- **重放路由还要训 router 吗？** 钉住的是离散 top-$k$ 集合；gating 分数通常仍从训练图算，梯度还能流到 router 权重。但被优化的已经是「在旧 / 引擎路由上的 $\pi$」，不是自然路由的 $\pi_\theta$，Qwen 把这叫对目标策略的偏置。长期仍要让 router 自己学会稳定 top-$k$，否则只是把不匹配藏进 replay。
- **LoRA 只训 expert、冻 router？** 能减小翻转，但训推精度隙还在。不要当成 R3 的替代。
- **EP all-to-all 慢是不是同一题？** 不是。那是吞吐，见 `sys-expert-parallel`。本题是数值与离散路径。

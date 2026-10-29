---
id: pt-r3-routing-replay
section: posttrain
order: 254
level: S
title: MoE RL 的 Routing Replay（R2 / R3）和 Keep Routing、GSPO 各修哪一层？
quick: "Keep Routing / R3 在训练图里重放推理引擎记下的专家，把离散路由对齐；R2 只重放训练引擎自己的旧路由，前提是训练图和引擎本来一致。GSPO 用序列级 $\\rho$ 降噪，专家已经走错它修不了。"
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

三个方法修的是不同层：R3 / Keep Routing 让训练时走的专家对齐推理引擎 sampling 时走的专家；R2 只对齐训练引擎自己前后两次的路由；GSPO 不碰路由，只把 token 级 ratio 换成序列级来降噪。路由都错了，先对齐路由，别急着换 clip。画图时分三层：路由集合、token 级 $\rho$、策略版本。

先说 MoE 上的 $\rho$ 为什么特别脆。router 是离散 top-$k$，推理引擎（vLLM / SGLang、量化、不同 batch）和 trainer（Megatron / FSDP、另一套 kernel）对同一个前缀可能选出不同的 expert。比如某个 token 在引擎里走了一组专家，到训练图里换成了另一组，后面的 hidden 已经不在同一个子网络上，两边的 $\log\pi$ 不是同一个函数。token 级 $\rho=\pi_\theta/\pi_{\mathrm{old}}$ 再连乘，局部的路由翻转会被放大成训练崩溃。监控训推 KL 和「$\rho$ 偏离 2 倍的 token 比例」，比只看 reward 更早报警。MoE 训推不一致整体会造成什么后果，见 `sys-moe-train-infer-routing-mismatch`，这题只问 RL 更新这一步怎么把路由钉住。

R3，也就是 Rollout Routing Replay，做法是 sampling 时把推理引擎的专家 id（或路由 mask）记下来，训练 forward 时强制走同一条 top-$k$。它同时修了两件事：引擎和训练图的实现差异，以及策略已经更新带来的路由漂移。DeepSeek 从 V3-0324 起把它当 MoE RL 的稳定手段，V3.2 里叫 Keep Routing，见 `pt-deepseek-rl-lineage`；Qwen 那篇（`2512.01374`）里的 R3 对应 Ma et al. 的 Rollout Routing Replay。

R2，即 Vanilla Routing Replay，重放的是训练引擎用旧策略自己算出的专家。它能减少 mini-batch 更新带来的 staleness，但默认训练图和引擎已经一致。Qwen 的实验里，中等 off-policy 时 R2 往往够用；训推 KL 大、off-policy 程度再加大时就必须上 R3。

GSPO 不改路由。序列级 likelihood ratio 对个别 token 的专家跳变没那么敏感，见 `pt-gspo`；字节的面试常从 GSPO 切入，见 `byte-moe-rollout-routing-gspo`。可路由已经错了，序列 $\rho$ 也只是错专家上的平均。TIS 和重算 logp 修的是概率数值，同样管不到离散的 top-$k$。这些办法可以叠着用：先对齐路由，再截断 $\rho$，见 `pt-tis-async`。

## 追问

**重放路由以后还要训 router 吗？**
还在训。钉住的是离散 top-$k$ 集合，gating 分数通常仍从训练图算，梯度照样流到 router 权重。不过被优化的已经是「在旧 / 引擎路由上的 $\pi$」，和自然路由下的 $\pi_\theta$ 有差别，Qwen 把这叫对目标策略的偏置。长期还是要让 router 自己学会稳定的 top-$k$，否则只是把不匹配藏进了 replay。

**LoRA 只训 expert、冻住 router 行不行？**
能减少翻转，但训推的精度差异还在，替代不了 R3。

**EP all-to-all 慢是同一个问题吗？**
不是。那是 throughput 问题，见 `sys-expert-parallel`；这题讲的是数值和离散路径。

---
id: pt-rejection-sampling-vs-rl
section: posttrain
order: 33
level: S
title: 什么时候应先做 rejection-sampling fine-tuning，什么时候必须进入 on-policy RL？
quick: 先看 base policy 的正确候选覆盖率。若较小 K 已能产出足够多高质量样本，RS 简洁稳定；若正确轨迹稀少、需跨多步探索或 reward 依赖当前策略状态，RS 会 support 收缩，应转向 on-policy RL 或先改善 seed / verifier。
tags:
  - Rejection Sampling
  - RL
  - Data Selection
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: Llama 2 Technical Report
    url: https://arxiv.org/abs/2307.09288
    type: primary
---

RS 的流程是对 prompt 采样 K 个回答，以 reward 或人工规则过滤，再把成功样本作为 SFT 数据。它计算简单、可离线审计，特别适合格式、风格或已有高覆盖率的可验证任务；但它学习的是“现有 policy 已会生成的成功子集”。

关键诊断是 K–success 曲线和数据 support。若只有极大 K 才偶尔成功，筛出来的数据少且分布窄，重复 RS 容易过拟合到少数题型。on-policy RL 则可在当前策略附近持续采样、利用相对 reward 优化，但需要处理 rollout 成本、staleness 与 reward hacking。

实践常用 RS 做冷启动或回收稳定样本，再上 RL 扩展边界；切换点要由 held-out coverage、reward 可信度和总算力，而不是算法潮流决定。

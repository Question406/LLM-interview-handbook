---
id: pt-rl-vs-tts-explore
section: posttrain
order: 245
level: S
title: RL 训练探索和 test-time scaling 探索差在哪？
quick: "RL 训练的探索靠采样、打分、更新 $\\pi_\\theta$，改的是分布本身，主要抬 pass@1。test-time 探索不改参数，用 best-of-N、树搜索、verifier rerank 在固定 $\\pi$ 上多花算力换覆盖。"
tags:
  - Exploration
  - Test-time Scaling
  - RLVR
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters
    url: https://arxiv.org/abs/2408.03314
    type: primary
  - title: Evaluating Large Language Models Trained on Code
    url: https://arxiv.org/abs/2107.03374
    type: primary
  - title: Does RL Really Incentivize Reasoning Beyond the Base Model?
    url: https://arxiv.org/abs/2504.13837
    type: primary
---

这块容易把「多采样」说成同一种探索。一个改参数，一个不改。训练 scaling 和 test-time scaling 花的都是采样预算，但一个把概率质量搬到好轨迹上，一个在冻结分布上把好轨迹捞出来。

## 训练时：探索发生在 采样轨迹（rollout），学习发生在更新

强化学习（RL） 的探索旋钮是 temperature、top-$p$、group size $G$、熵奖励、KL、输入提示（prompt） 难度。同一题采多条，验证器（verifier） / 奖励模型（RM） 给 $R$，策略梯度把质量推向高 $R$ 区域。探索强度不够，组内全错，$\hat A=0$，见 `byte-grpo-all-same-zero-adv`。KL 太紧或温度太低，会过早熵塌，后面怎么加 $G$ 都还是同一条链。

这一阶段的产品目标通常是 **pass@1**：部署时只生成一次也要够用。若只是把 base 长尾里已有的正确链提权，大 $K$ 的 pass@K 曲线会和 base 重合，见 `pt-rlvr-discovery-vs-reweighting`。

## 测试时：参数冻结，用计算换覆盖

Test-time scaling 不更新 $\theta$。典型拓扑：best-of-N、majority vote、树搜索、工具循环、verifier rerank。预算怎么在生成器和选择器之间分，见 `pt-test-time-search-topology`。

若单次成功率为 $p$ 且样本独立，

$$
P(\text{至少一次成功})=1-(1-p)^N.
$$

LLM 样本高度相关，这条公式是上界不是实测。$N$ 加大后边际收益很快掉。无偏的 pass@K 估计要用组合公式，不要用前 $K$ 次有没有对的均值，见 `fund-passk`。

## 两者怎么配合

训练把 $p$ 本身抬高，同样的 $N$ 更值钱；测试把已经学到的分布采得更满。只堆 test-time 而 $p$ 极低，是在用实际耗时补一个不会的模型。只堆 RL 而部署仍要很大 $N$，说明默认解码还没对准，或者多样性塌了、选择器在捡同一条链。

training explore 改 $\pi$，test-time explore 搜 $\pi$。比较两者时固定总 token 数 / 实际耗时 / verifier 成本，不要锁「都采了 8 次」。

## 追问

- **RL 之后 pass@1 涨、pass@K 掉说明什么？** 概率质量过度集中，探索空间缩小。SimKO / 熵奖励 / 更高温度是训练侧的药；部署侧再加大 $N$ 救不回已经塌的 support，见 `pt-grpo-family-sapo-simko`。
- **R1 的长 思维链（CoT，即分步推理过程） 算哪一种？** 训练用 RL 激励长思考，推理时仍是一次前向（可再套 best-of-N）。长度本身不是 test-time search，是被 RL 改过的解码行为。
- **和 rejection sampling 呢？** RS 用 verifier 滤样本再 监督微调（SFT），改的是离线数据，不是在线 $\pi$ 更新，也不是推理时搜索。三条路见 `pt-rejection-sampling-vs-rl`。

---
id: pt-rl-vs-tts-explore
section: posttrain
order: 245
level: S
title: RL 训练探索和 test-time scaling 探索差在哪？
quick: "RL 训练的探索是采样、打分、更新 $\\pi_\\theta$，改的是分布本身，主要抬 pass@1。test-time 探索不改参数，用 best-of-N、树搜索、verifier rerank 在固定的 $\\pi$ 上多花算力换覆盖。两者比较时要固定总 token、耗时和 verifier 成本。"
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

差别在改不改参数。RL 训练时的探索是采样、打分、再更新 $\pi_\theta$，把概率质量搬到好轨迹上；test-time 探索不动参数，在冻结的分布上多采、多搜，把好轨迹捞出来。两边花的都是采样预算，一个改 $\pi$，一个搜 $\pi$。

训练时，探索发生在采样轨迹（rollout），学习发生在更新。强化学习（RL）的探索旋钮有 temperature、top-$p$、group size $G$、熵奖励、KL 和输入提示（prompt）难度。同一题采多条，验证器（verifier）或奖励模型（RM）给出 $R$，策略梯度把质量推向高 $R$ 的区域。探索不够时组内全错，$\hat A=0$，见 `byte-grpo-all-same-zero-adv`；KL 太紧或温度太低会过早熵塌，后面再加 $G$ 也还是同一条链。这一阶段的产品目标通常是 **pass@1**，部署时只生成一次也要够用。如果 RL 只是把 base 长尾里已有的正确链提权，大 $K$ 的 pass@K 曲线会和 base 重合，见 `pt-rlvr-discovery-vs-reweighting`。

测试时参数冻结，用计算换覆盖，典型做法是 best-of-N、majority vote、树搜索、工具循环和 verifier rerank；预算怎么在生成器和选择器之间分，见 `pt-test-time-search-topology`。若单次成功率为 $p$ 且样本独立，

$$
P(\text{至少一次成功})=1-(1-p)^N.
$$

LLM 的样本高度相关，这条公式只是上界，实测达不到，$N$ 加大后边际收益很快就掉。无偏的 pass@K 估计要用组合公式，别用「前 $K$ 次里有没有对的」的均值，见 `fund-passk`。

两者是配合关系。训练把 $p$ 本身抬高，同样的 $N$ 更值钱；测试把已经学到的分布采得更满。比如一个模型单次成功率极低，只靠加大 $N$，就是在用实际耗时补一个不会的模型；反过来 RL 做了很多、部署时仍要很大的 $N$，说明默认解码还没对准，或者多样性塌了、选择器一直在捡同一条链。比较两边时要固定总 token 数、实际耗时和 verifier 成本，「都采了 8 次」这种对齐没有意义。

## 追问

**RL 之后 pass@1 涨、pass@K 掉，说明什么？**
概率质量过度集中，探索空间缩小了。SimKO、熵奖励、更高温度是训练侧的药；部署侧再加大 $N$ 救不回已经塌掉的 support，见 `pt-grpo-family-sapo-simko`。

**R1 的长思维链（CoT，即分步推理过程）算哪一种？**
算训练侧的结果。训练用 RL 激励长思考，推理时仍是一次前向（可以再套 best-of-N）。长度本身不是 test-time search，是被 RL 改过的解码行为。

**和 rejection sampling 呢？**
RS 用 verifier 过滤样本再做监督微调（SFT），改的是离线数据，既不是在线更新 $\pi$，也不是推理时搜索。三条路的对比见 `pt-rejection-sampling-vs-rl`。

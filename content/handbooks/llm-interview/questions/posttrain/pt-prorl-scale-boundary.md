---
id: pt-prorl-scale-boundary
section: posttrain
order: 247
level: S
title: 结合 ProRL，怎样把 RL 训练边界真正拉开？
quick: "短程 强化学习（RL） 经常只把 base 已有正确链提权。ProRL 的点是把稳定训练拉到数千步：难度卡在组内奖励方差非零的临界区，配 clip-higher / 动态采样防熵塌，KL 加周期性 reference reset 避免正则过强而阻碍更新，同时提高轨迹采样吞吐。只加 GPU 不算 scale RL。"
tags:
  - ProRL
  - RLVR
  - Exploration
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: ProRL — Prolonged Reinforcement Learning Expands Reasoning Boundaries
    url: https://arxiv.org/abs/2505.24864
    type: primary
  - title: Does RL Really Incentivize Reasoning Beyond the Base Model?
    url: https://arxiv.org/abs/2504.13837
    type: primary
  - title: DAPO
    url: https://arxiv.org/abs/2503.14476
    type: primary
---

「RL 能否拓展能力边界」不要先站队。短训、只刷数学、base 已经过拟合的题上，pass@1 涨、大 $K$ 持平，看起来就是 reweighting，见 `pt-rlvr-discovery-vs-reweighting`。ProRL 的反驳是：很多否定结论来自训得太短、题太熟。它把 GRPO 拉到两千步以上，并在数学 / 代码之外加 STEM、逻辑谜题、指令遵循。

## 五件事一起 scale，不是只加卡

1. **可学习数据。** 组内要 $0\lt\mathrm{Var}(R_1,\ldots,R_G)$。全对没梯度，全错也没梯度。课程应跟着当前策略的临界区走，DAPO 动态采样就是在买非零方差组，见 `pt-dapo`。长期滤掉全错桶会变成隐性 curriculum，要周期性把超难题探回来。
2. **探索预算。** $G$、温度、输入提示（prompt） 多样性。熵一旦塌，后面的步数只是在同一条链上刷分。
3. **稳定时长。** ProRL 认为提前停是把「还没探索完」写成「RL 不能发现新路径」。要看 holdout pass@K 是否还在涨，而不是看训练 奖励分数（reward） 平台。
4. **可验证 reward。** 边界能否扩，取决于 验证器（verifier） 有没有洞。刷到 奖励模型（RM） 表面特征不算新能力。
5. **采样轨迹（rollout） 吞吐。** 实际耗时受最长样本限制，系统跟不上，算法再稳也训不长。异步、partial、长度分组统计见 `byte-grpo-rollout-tail-gpu`。

## ProRL 具体稳住了什么

熵塌是长训第一杀手。只加温度往往只是推迟塌缩。ProRL 用了 DAPO 的 clip-higher 和动态采样，并 **保留** KL：它从已经会 思维链（CoT，即分步推理过程） 的蒸馏起点接着训，不是 R1-Zero 那种从 base 冷启动。KL 项逐渐主导 损失（loss） 时，周期性把 $\pi_{\mathrm{ref}}$ 重置成当前 $\pi_\theta$ 并清优化器，让正则重新变成「别一步走太远」，而不是「永远钉死在旧 SFT」。这和「DAPO 去掉 KL」不矛盾：起点和任务不同，见 `xiaohongshu-grpo-drop-kl`。

论文还报告：base 无论采多少次都过不了的题，长训后可以过；轨迹与预训练语料的重叠下降。这是「边界可能扩大」的证据，不是定理。实验协议仍要锁温度、$K$、verifier，否则又把计算不足写成 discovery。ProRL 给的是长训配方：临界区数据、探索、稳定步数、可靠 verifier、rollout 吞吐一起 scale，不是「无限训就会变强」。

## 追问

- **和「RL 只是重加权」怎么同时讲？** 允许混合结论：熟题上是 reweighting，base 本来就不会的逻辑谜题上更可能出新路径。按任务切片报，不要一个形容词概括整个 run。
- **reference reset 会不会让 KL 失效？** 会改变锚点。它换的是「相对最近稳定快照的近端约束」，不是相对原始 监督微调（SFT） 的 drift。两套 KL 仍要分开，见 `pt-trust-region-vs-drift-kl`。
- **没有 2k 步预算怎么办？** 先保证有效组比例和熵，再谈步数。步数堆在零方差组和熵塌上，只是浪费 rollout。

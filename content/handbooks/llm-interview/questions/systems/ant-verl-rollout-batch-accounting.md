---
id: ant-verl-rollout-batch-accounting
section: systems
order: 101
level: S
title: 蚂蚁 26 秋招：VeRL 的 rollout 与 update batch 参数如何共同决定每卡样本数？
quick: "$B_r$ 个 prompt 经 `rollout.n` 扩成 $B_r n$ 条轨迹，再按 global batch 切成若干次 update；每卡实际拿到多少样本，由 DP 度、micro-batch、梯度累积和 packing 一起决定。"
tags:
  - Ant Group
  - 2026 Campus Recruiting
  - VeRL
  - RL Infrastructure
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 26秋招蚂蚁金服大模型算法一面（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/e2585943c7874b3081b0878b646b6f01
    type: candidate-first-hand
---

## 真题记录

- 公司：蚂蚁集团
- 团队 / 岗位：大模型算法
- 届别 / 流程：26 届秋招；一面
- 面试时间：原帖未披露；帖子发布于 2025-11-05
- 来源类型与可信度：牛客候选人原帖，A（公司、届别、岗位与轮次明确）
- 原始措辞：**“是不是用的Verl框架做的rl?详细讲一下verl框架的训练流程。并讲一下配置文件中rollout batchsize, global batch_sizemicro_batch_size_per_device_for_update，rollout.n等等参数的关系，以及他们如何影响最终更新时每张显卡上的样本数。”**

这几个参数是一条乘法链：一个采样轨迹（rollout）batch 有 $B_r$ 个 prompt，每个 prompt 生成 $n$ 条轨迹（`rollout.n`），一轮就得到 $B_r n$ 条 trajectory；这些轨迹再按 global update batch 切开。数据并行度为 $D$、每卡 micro-batch 为 $m$、累积步数为 $a$ 时，不考虑 packing，一次 optimizer update 大约能装 $Dma$ 条样本，配置要让它和 global batch 对上，或者讲清楚尾 batch 怎么处理。

讲之前我会先把名字归一成四个概念：prompt batch、每个 prompt 的 rollout 数、全局 update batch、每卡的 update micro-batch。不同框架的字段名不一定同义，别假设它们一一对应。

按条数核算只是第一步。completion 长短不一，token 数、显存和有效 token batch 就对不上；开了 packing，每卡实际的序列数也会变；PPO/GRPO 跑多个 epoch，又会重复消费同一批 rollout。所以我一般会列一张 accounting 表：prompt 数、trajectory 数、有效 tokens，actor、reference 和奖励分数（reward）各自的每卡 micro-batch、accumulation 和 update 次数。然后用监控核对有没有 OOM、空卡、drop-last，或者预期之外的样本复用。

用过 slime 的话，顺手对一下字段：`--rollout-batch-size` × `--n-samples-per-prompt` 是轨迹数，`--global-batch-size` 按样本算、不按 prompt 算，`--num-steps-per-rollout` 把一批 rollout 切成多步更新。详表见 slime batch 对照卡。

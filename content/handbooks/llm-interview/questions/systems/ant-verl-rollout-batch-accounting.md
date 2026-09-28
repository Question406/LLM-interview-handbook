---
id: ant-verl-rollout-batch-accounting
section: systems
order: 101
level: S
title: 蚂蚁 26 秋招：VeRL 的 rollout 与 update batch 参数如何共同决定每卡样本数？
quick: >-
  我会先画清样本的两条路：prompt 经 `rollout.n` 扩成 group，再经 global batch 切成 update。每个
  rank 的 micro-batch 由数据并行度、gradient accumulation 和 sequence packing 一起决定。不能只报一个
  batch size，得核对 token 数、有效样本数和各阶段吞吐。
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

先把名称归一成「prompt batch、每 prompt 的 rollout 数、全局 update batch、每卡 update micro-batch」，但不会假设所有框架字段同义。若一个 rollout batch 含 $B_r$ 个 prompt、每个生成 $n$ 条轨迹，则一轮产生 $B_r n$ 条 trajectory；这些轨迹再按 global update batch 切分。对于数据并行度 $D$、每卡 micro-batch $m$、累积步数 $a$，未考虑 packing 时一次 optimizer update 的容量近似为 $Dma$ 条样本，配置必须满足，或者明确尾 batch 怎么处理。

「样本」不能只按条数核算：变长 completion 会让 token 数、显存和有效 token batch 对不上，packing 会改每卡实际序列数，PPO/GRPO 的多 epoch 又会重复消费同一批 rollout。一般会输出一张 accounting 表：prompt、trajectory、有效 tokens、actor / reference / reward 各自每卡 micro-batch、accumulation 和 update 次数；再用监控核对有没有 OOM、空卡、drop-last 或预期外的样本复用。

用过 slime 时对一下字段：`--rollout-batch-size` × `--n-samples-per-prompt`，`--global-batch-size` 按样本不是 prompt，`--num-steps-per-rollout` 切多步。详表见 slime batch 对照卡。

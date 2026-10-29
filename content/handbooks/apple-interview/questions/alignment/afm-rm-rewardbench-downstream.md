---
id: afm-rm-rewardbench-downstream
section: alignment
order: 104
level: A
title: RM 榜单高分但 RL 变差：RewardBench 到底测到了什么？
quick: 我会拿当前模型生成的同一批候选，让两个 RM 分别选，再实际检查它们选出的答案。榜单上的排序能力未必覆盖当前模型的错误。
companies:
  - apple
tags:
  - Apple
  - AFM 补全 2026-10
  - Reward Modeling
  - 口述版
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-26'
sources:
  - title: RewardBench
    url: 'https://arxiv.org/abs/2403.13787'
    type: primary
  - title: RewardBench 2
    url: 'https://arxiv.org/abs/2506.01937'
    type: primary
---

## 面试官可能这样问

RewardBench 分数更高的 RM，为什么用起来反而差？

## 可以这样回答

我会先固定一批当前模型的候选回答，让两个 RM 都来选，然后实际检查被选中的答案。这样比较的是它们在同一批选择上的表现。

一种可能是，分数高的 RM 很擅长明显的好坏对，却特别容易给少数错误答案打极高分。做 best-of-N 时，这些错误就容易被选出来。还有一种可能是，当前模型的回答风格和它训练时见过的不一样。

所以我会看当前候选上的选择质量和高分错例，再决定要不要补 preference data。公共 benchmark 仍有参考价值，但我不会用它的总分代替这个任务里的结果。

## 技术备查

## 场景与问题
RM-A 在公开基准胜过 RM-B，但用 A 做 best-of-32 和 RL 后工具成功率更低。是 benchmark 没用，还是 RM 训练错了？

## 参考答案
先确认基准版本、模板和计分，不能混比 RewardBench 与 RewardBench 2 数字。前者建立了分能力的奖励评价；后者增加更难的新数据并研究与下游选择、RL 的联系，关联不是对所有部署条件的保证。

固定同一批 current policy 候选，比较 pairwise 准确率、top-1 执行成功率、错误高分的尾部和 N 从 1 增到 32 的曲线。A 可能擅长明显好坏对，却把少数作弊 trajectories 打极高；优化恰好放大这些尾部。再控制策略初始化、KL、rollout 和预算做小型 RL 对照。最后用独立任务与盲测判断真正收益，不能用同一个 RM 自证。

## 追问
**要为本任务重建所有 benchmark 吗？** 保留公共可比性，再加许可来源的新 prompt、nearest neighbors hard examples 及工具执行评价。
**最高分就是 calibration 最好吗？** 不是，排序准确率不评估概率置信程度。


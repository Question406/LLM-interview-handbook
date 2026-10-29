---
id: afm-rm-active-label-selection
section: alignment
order: 111
level: A
title: 主动采偏好：一万条标注预算该花在最大分歧还是最不确定的样本？
quick: 我会优先选有可能改变训练决策的例子，同时留一部分随机样本，防止只看模型最困惑的那一小类题。
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
  - title: 'WARM: On the Benefits of Weight Averaged Reward Models'
    url: 'https://arxiv.org/abs/2401.12187'
    type: primary
  - title: RewardBench 2
    url: 'https://arxiv.org/abs/2506.01937'
    type: primary
---

## 面试官可能这样问

只有一千对人工标注预算，你会选哪些？

## 可以这样回答

我会先看当前模型的错误和已有数据覆盖。高风险失败、几个 RM 明显意见不同的例子，以及新任务里缺标签的部分，都可能值得优先标。

但我不会把预算全部花在分歧最大的地方。有些题本来就几乎一样，标了很多次也很难得到有用区分；几个模型也可能一起犯错。所以我会留一部分随机样本和已知困难 evaluation slices，用来检查没被主动选中的地方。先标一小批，看这些标签是否真的改善独立评价，再决定下一批怎么分。

## 技术备查

## 场景与问题
三个 RM 对一批新 rollout 有分歧。预算只够标 1000 对，全部选分差最大或预测最接近 0.5 的行吗？

## 参考答案
先分清模型间分歧和单模型 0.5：前者是模型不确定性的线索，后者可能是真 tie。先做任务 deduplication、风险 evaluation slices 和可标注性筛选，再在覆盖约束下组合代表性样本、困难 nearest neighbors、高风险失败与随机审计。比例通过小批试验确定，不宣称存在万能百分比。

WARM 讨论分布变化及偏好不一致下的 robustness，但本题的主动 sampling 方案是原创延伸。用新策略的冻结候选集测每标注小时带来的独立选择质量增益；记录 sampling 概率，估计总体分布时考虑 selection bias。专家无法判断的任务优先补证据或 executor，而非强行打标签。

## 追问
**三个 RM 一致是不是无需标？** 不一定，它们可能共享错误，应保留随机和对抗抽查。
**只选高风险会怎样？** 可提升安全覆盖，但不能用其准确率直接估计自然流量表现。


---
id: afm-rm-rating-versus-pairwise
section: alignment
order: 102
level: A
title: 同预算选 RM：绝对打分、成对偏好，还是多属性回归？
quick: 如果我关心两条回答哪条更好，会先考虑成对比较；如果要知道错在正确性还是表达上，分项评分会更有帮助。
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
  - title: 'HelpSteer2-Preference: Complementing Ratings with Preferences'
    url: 'https://arxiv.org/abs/2410.01257'
    type: primary
  - title: HelpSteer2
    url: 'https://arxiv.org/abs/2406.08673'
    type: primary
---

## 面试官可能这样问

让人打1到5分，还是两两比较，怎么选？

## 可以这样回答

我会先看需要什么信息。只是选出两条回答里更好的一条，成对比较比较直接；但如果我还想知道它为什么好，是事实正确、信息更全，还是表达更清楚，分项评分会更有用。

我不会拿两批完全不同的数据来比较两种方法。可以先抽同一批问题和回答，同时收评分和偏好，记录标注时间，再用差不多的预算训练。最后看哪种反馈更能帮模型选出好答案，而不是只比较哪个 loss 更低。

## 技术备查

## 场景与问题
预算只够 2000 人时，要比较 1–5 分回归与 Bradley–Terry。现有回归数据来自短摘要，preference pairs 来自长推理。你如何让实验可解释？

## 参考答案
先固定同一批 prompt 和候选，为子集同时收属性评分与 pairwise 选择；记录耗时，而不是只固定条数。按 prompt 家族切分，用相同 backbone、训练预算与验证规则，比较回归、pairwise 和组合目标。HelpSteer2-Preference 的意义在于可以用匹配数据比较范式，而非证明换一种标签天然更强。

评价至少包含标注重测一致率、nearest neighbors 候选排序、calibration、固定 N 的 best-of-N 与新策略候选上的表现。正确性、帮助性、简洁性分别标注，避免用一个总分掩盖冲突。上线用哪个属性权重须由任务约束定义，并做权重敏感性分析。

## 追问
**成对比较一定比打分可靠？** 不一定，候选差异、专家知识和协议决定难度。
**如何防止组合目标只学到评分尺度？** 单独报告各项 loss 与验证指标，调系数只用 development set，并检验每种 annotator 风格的迁移。


---
id: dt-curriculum-moving-target
section: panel
order: 46
level: A
title: Panel 情景：昨天的高价值难题，今天都变简单了，如何更新合成课程？
quick: 假设昨天只有两成回答做对的一批题，今天已经九成都对。继续用同一份难度标签分配生成预算，可能大多在重复模型已经学会的内容。
companies:
  - apple
tags:
  - Apple
  - AFM 专项 2026-10
  - AFM 加练第二批
  - 情景练习
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Evaluating Large Language Models Trained on Code
    url: 'https://arxiv.org/abs/2107.03374'
    type: primary
---

## 题目描述

原创合成课程题，建议 30 分钟。你每周生成 100 万条推理任务，按 teacher 估计的难度筛选。student 训练三周后，这些任务首答通过率从 20% 升到 90%，但新组合任务仍差。生成器倾向反复出同类题。你不能增加总 token 预算。

请设计动态任务选择、难度估计和覆盖监控，解释如何避免把固定 evaluation set 变成课程生成器的提示材料。

## 回答思路

> **问题与场景：** 假设昨天只有两成回答做对的一批题，今天已经九成都对。
>
> **做法与原因：** 我会定期用当前模型重估通过率，结合题型覆盖与验证成本更新课程。
>
> **检查与取舍：** 更新课程不等于更新最终测试。

## 可以这样回答

假设昨天只有两成回答做对的一批题，今天已经九成都对。继续用同一份难度标签分配生成预算，可能大多在重复模型已经学会的内容。

我会定期用当前模型重估通过率，结合题型覆盖与验证成本更新课程。保留适量容易题做能力维护，也为困难题提供示范或更合适的探索预算。

更新课程不等于更新最终测试。固定独立评测观察迁移，避免反复挑对当前分数最有利的任务。

## 技术备查

## 解题思路与参考答案

teacher 的难度评分可能衡量解释复杂度，并非当前 student 的 learnability。首答上涨也可能来自模板熟悉。先按任务家族分组，检查重复 cluster、解题程序和独立新组合的成功率，不能只看样本措辞是否变化。

### 更新任务池

维护 seed、生成程序、能力标签与派生家族。周期性用当前 student 在开发任务池 sampling，估计首答、多次 sampling 成功率及不确定性，提升有学习空间的任务权重。简单任务保留一定比例保证基础与稳定，过难任务少量探索并分析是否缺知识、工具或示范，而不是无限 resampling。

### 用覆盖限制替代无限扩量

预算固定时，减少同家族重复，增加跨技能组合与新环境状态。对每个候选桶同时看通过验证的独立任务数、student 表现、学习后迁移和生成成本。不是只有通过率在 50% 的题才有价值：样本数少时估计不稳定，重要的 security constraints 也可能需覆盖。权重需要试验，不设未经验证的最佳常数。

### 评测隔离

课程可以用训练／开发错误标签和抽象能力定义，不能把最终测试原题或答案喂回生成器。保留不参与课程选择的盲测家族，固定 regression tasks 观察基础能力是否回退。若重复看同一 development set 选课程，应最终用新家族验证，不能把开发分数当无偏泛化证明。

## 面试追问

**任务越来越难是否说明进步？** 不一定。生成器可能只加无关长度、混乱前提或不可解约束，需检验可解性、verifier 有效性和知识需求。

**student 自己估难度靠谱吗？** 可作为低成本信号，但 confidence 需 calibration。优先用实际多次生成与独立验证，并记录探索成本。

**没有收益怎么办？** 回到学习收益而非难度评分，比较新覆盖、示范质量和任务目标是否匹配，停掉只增加表面复杂度的生成规则。

---
id: dt-judge-ranking-reversal
section: panel
order: 32
level: S
title: Panel 情景：自动 judge 胜率涨了，human evaluation 却反转，先修模型还是修测量？
quick: 假设自动 judge 认为新模型更好，人工却更喜欢旧模型。我会先暂停扩大训练，检查两边是否比较相同任务、候选和评分标准。
companies:
  - apple
tags:
  - Apple
  - AFM 专项 2026-10
  - 情景练习
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: Direct Preference Optimization
    url: 'https://arxiv.org/abs/2305.18290'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

## 题目描述

原创情景题，数字为练习约定。建议限时 35 分钟。

新策略对 old policy 的自动 judge 胜率是 65%，但 200 对人工评审只得到 46% 胜率。新回答平均更长，且 judge 与生成 synthetic data 的 teacher 来自同一模型家族。训练团队建议扩大这套合成 preference data。

请设计一周内能执行的调查，说明如何 calibration 评价、如何处理标注分歧，以及哪些证据出现前不能继续放大训练。

## 回答思路

> **问题与场景：** 假设自动 judge 认为新模型更好，人工却更喜欢旧模型。
>
> **做法与原因：** 再把候选匿名、交换 A/B 顺序，并控制长度与格式，看分歧是否随这些因素变化。
>
> **检查与取舍：** 确定测量可靠后再决定修模型还是修标签。

## 可以这样回答

假设自动 judge 认为新模型更好，人工却更喜欢旧模型。我会先暂停扩大训练，检查两边是否比较相同任务、候选和评分标准。

再把候选匿名、交换 A/B 顺序，并控制长度与格式，看分歧是否随这些因素变化。事实与执行结果可以用独立证据检查；确实存在的风格差异则不必强行变成唯一偏好。

确定测量可靠后再决定修模型还是修标签。调整 judge 的数据与最终盲测分开，不能反复调到这一批人评上吻合就宣布问题解决。

## 技术备查

## 解题思路与参考答案

先保留现有策略 checkpoint 与输出。46% 不自动等于真实退化：要说明 tie 处理、任务 sampling、annotator 人数，并计算不确定区间；若多个评审评价同一 prompt，不能把评审数量当独立任务数量。

### 排查评价偏差

在相同 200 对上匿名隐藏来源，随机左右位置，追加交换位置的复评，检查同一 judge 对顺序是否敏感。按回答长度差、任务类型、正确性是否可验证做 evaluation slices。对事实与工具任务单独执行验证，不能让“解释漂亮”覆盖“结果错误”。匹配长度或让人工只评事实内容是诊断方法，不能偷偷更改正式指标后只报告最好结果。

同一家族可能有共同盲点，但不能仅凭家族关系 assertion 偏差。补充独立评审来源和专家裁定，检查 judge 偏好的风格是否恰好来自 teacher。用 human evaluation 作为 calibration 依据，报告 judge 对人类偏好的区分能力和各 evaluation slice 偏差。

### 分歧怎么处理

先区分任务有歧义、评分标准模糊和个体审美不同。事实错误要回到证据，不用多数票把错误变正确；合法的风格偏好多样性可以保留 soft labels、tie 或多维评分。不能把所有分歧对都扔掉，否则数据会只剩容易达成共识的简单题。

### 训练和评测如何隔离

calibration 集不参与策略训练，也不反复调 judge 后仍当最终测试。另留一份盲测集合确认 calibration 效果。在自动指标与 human evaluation 冲突未解释前暂停扩大同源 preference data，先小规模比较原标签、重新标注标签与长度受控标签，固定训练预算。

## 面试追问

**换一个更强 judge 就行吗？** 只能作为额外证据。强模型同样可能有位置、冗长和自我偏好，仍要针对目标任务 calibration。

**自动 judge 还能用吗？** 可以用于快速回归和候选筛选，但发布结论应由独立可靠评价支撑，并定期检查分布变化。

**面试官在看什么？** 能否把测量错误与模型错误分开，避免将训练使用的代理指标当成独立效果证据。

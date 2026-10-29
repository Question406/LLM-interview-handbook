---
id: afm-web-benchmark-two-points
section: evaluation
order: 706
level: S
title: Benchmark Debugging：500 题提高 2 个点，真的变强了吗？
quick: >-
  分析同题 paired outcomes、重复 sampling 与数据独立性，再做定向验证。 报告 effect size 和
  uncertainty，不能只凭总分做发布决策。
companies:
  - apple
tags:
  - Apple
  - AFM 网站参考题
  - AFM Web References 2026-10-27
  - evaluation
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: 'TechAIInterview — Question bank: benchmark improvement'
    url: 'https://www.techaiinterview.com/questions/'
    type: reference
---

## 来源与范围

参考 [TechAIInterview — Question bank: benchmark improvement](https://www.techaiinterview.com/questions/) 的公开题目、案例或课程章节。以下题面、场景和参考答案为手册改写及 AFM 扩展；参考答案为手册设计示例。

## AFM 练习题面
两个模型在同一 500 题 benchmark 上分别得到 70% 与 72%。你需要哪些信息才能判断，并设计下一步诊断？总分条件来自网站题意；以下数字是手算例子。

## 技术备查
令 $b$ 为旧错新对，$c$ 为旧对新错，则净变化为 $(b-c)/500$。例子一 $b=10,c=0$；例子二 $b=50,c=40$，都是 2 个点，但 paired evidence 不同。

可用 matched binary outcomes 的 exact McNemar test，或按任务单位做 paired bootstrap，报告 confidence interval 与 effect size。若题目存在 within-group correlation，要按 cluster resampling。对于随机生成还要区分 prompt variation 与 rollout variation。

## 面试追问
**提高不显著是否证明没用？** 不是；可能样本不足。看 uncertainty 是否仍包含有实践意义的收益或损失。

**总分涨、tool-use 跌怎么办？** 按产品任务权重与关键风险单独验收；总分不能覆盖必须保留的能力。

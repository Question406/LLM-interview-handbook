---
id: dt-honest-fluent
section: labs
order: 44
level: S
title: Anthropic：怎么评模型是诚实，还是只是流畅？
quick: "把两者拆开测、分开报。诚实是按证据回答、没依据时承认不知道，流畅只是读着顺。做法是把「流畅但事实错误」和「简短但正确」的回答配成对，分别评价事实忠实度和表达质量。Arena 或满意度得分不能单独证明诚实：模型附和用户的错误前提，也可能得到高分。"
companies:
  - apple
tags:
  - Anthropic
  - Evaluation
  - Honesty
  - Apple
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Anthropic AI Research Engineer Full Loop (HackTheRounds, 2025)
    url: https://www.hacktherounds.com/blog/anthropic-ai-research-engineer-full-loop-interview-experience-2025-offer
    type: candidate-first-hand
  - title: "TruthfulQA: Measuring How Models Mimic Human Falsehoods"
    url: https://arxiv.org/abs/2109.07958
    type: primary
  - title: Towards Understanding Sycophancy in Language Models
    url: https://arxiv.org/abs/2310.13548
    type: primary
---

诚实要求模型按证据回答，没有足够依据时承认不知道；流畅只说明回答读起来顺。两者要用不同的题目测试，分别报告结果。

公开面经记录了一场 2025 年 Anthropic RE 电话面试，口头题就是「how would you evaluate whether a model is being honest versus merely fluent」；同场 CodeSignal 还涉及基于人类反馈的强化学习（RLHF）可能奖励不诚实行为的问题。value drift 那张卡是同一场的另一道短答，见 `dt-value-drift`。

## 为什么 Arena 和满意度会误判

人有时更喜欢客气的长回答，或者对错误前提的附和；奖励模型（RM）学到这种偏好，就会鼓励流畅却不真实的回答。只报 Arena 或满意度，可能把迎合误判成进步。TruthfulQA 也写过：更大的模仿模型更会复述常见误解，因为训练分布里假话很多。

## 怎么测

1. **错误前提配对。** 让用户带着错误前提提问，把简短纠正错误的回答标为 chosen，把客气附和的回答标为 rejected。
2. **覆盖几类失败。** 评测包含 TruthfulQA 式的常见误解、模型是否迎合用户，以及是否凭空补出源文档里没有的好消息。
3. **分维度标注。** 人工评价分别标事实忠实度、礼貌程度和完整性，每项单独给分；合成一个「更好」会把事实错误藏起来。
4. **分开报告。** 流畅这一维仍然要测，产品回答也需要易读。两项结果分开报告，发版时明确讨论各自权重，不能让一个 RM 分数掩盖事实质量的变化。

## 实践中的变化

摘要任务最容易出现「读着顺、事实错」，要单独配对测。偏好对可以来自研究数据和许可脚本。回答可以语气温和，训练标签仍要区分表达和事实。

## 追问

- **TruthfulQA 会不会被污染？** 会。公开题适合做回归测试；发布检查要加入内部设计的误解题，以及按时间隔离的新闻题，见 `dt-contamination`。
- **模型说「我不知道」算诚实还是无能？** 要分开测。题目要求搜索而模型没有搜，是能力问题，见 `dt-when-to-search`；对不该编的事实说不知道，是诚实。

相关：`dt-sycophancy-data`、`dt-grounding-data`。

---
id: dt-honest-fluent
section: labs
order: 44
level: S
title: Anthropic：怎么评模型是诚实，还是只是流畅？
quick: "两者拆开测、分开报。诚实是按证据回答、没依据时承认不知道，流畅只是读着顺。做法是把「流畅但错」和「简短但对」的回答配成对，事实忠实度和表达质量分开打分；只看 Arena 或满意度，附和错误前提的回答也可能拿高分。"
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

诚实要求模型按证据回答，没有足够依据时承认不知道；流畅只说明回答读着顺。两者要用不同的题测，结果分开报。

举个例子，用户带着一个错误前提来问：「既然维生素 C 能治感冒，每天吃多少合适？」一个回答很客气地顺着给了剂量建议，读起来很顺；另一个只有两句，先指出这个前提站不住，再给一般建议。前者在 Arena 上很可能赢，后者才是诚实的。

Arena 和满意度会误判，是因为人有时更喜欢客气的长回答，或者对错误前提的附和；奖励模型（RM）学到这种偏好，就会鼓励流畅却不真实的回答。只报这两个分，可能把迎合误判成进步。TruthfulQA 也写过，更大的模仿模型更会复述常见误解，因为训练分布里假话很多。

测法就是把上面那种情况造成配对：用户带着错误前提提问，简短纠正的回答标 chosen，客气附和的标 rejected。评测里放 TruthfulQA 式的常见误解、模型是否迎合用户，以及是否凭空补出源文档里没有的好消息。

人评分别标事实忠实度、礼貌程度和完整性，每项单独给分，合成一个「更好」会把事实错误藏起来。流畅这一维照样要测，产品回答也需要易读。两项结果分开报，发版时明确讨论各自的权重，别让一个 RM 分数盖住事实质量的变化。

这题的来源是公开面经里一场 2025 年的 Anthropic RE 电话面试，口头题就是「how would you evaluate whether a model is being honest versus merely fluent」；同场 CodeSignal 还问到基于人类反馈的强化学习（RLHF）可能奖励不诚实行为。value drift 那张卡是同一场的另一道短答，见 `dt-value-drift`。

## 追问

**TruthfulQA 会不会被污染？**
会。公开题适合做回归测试；发布检查要加入内部设计的误解题，以及按时间隔离的新闻题，见 `dt-contamination`。

**模型说「我不知道」算诚实还是无能？**
要分开测。题目要求搜索而模型没有搜，是能力问题，见 `dt-when-to-search`；对不该编的事实说不知道，是诚实。

**哪类任务最容易「读着顺、事实错」？**
摘要，要单独配对测。偏好对可以来自研究数据和许可脚本。

**语气温和的回答会被扣分吗？**
不会。回答可以语气温和，训练标签照样要区分表达和事实。

相关：`dt-sycophancy-data`、`dt-grounding-data`

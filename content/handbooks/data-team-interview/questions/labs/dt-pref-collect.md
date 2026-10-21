---
id: dt-pref-collect
section: labs
order: 51
level: S
title: Cohere / xAI：偏好数据怎么采，一致率低了改什么？
quick: "先写清标注标准：比较哪些维度、什么算平局，再让当前模型生成待比较的回答。一致率 $\\kappa$ 低时，先查题目、标准和示例是否含糊，改完再采；分歧来自标准本身时，加标注员也压不下去。能执行验证的任务优先用规则奖励，人工只判断自动检查不了的维度。"
companies:
  - apple
tags:
  - Cohere
  - xAI
  - Preference
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: "Training a Helpful and Harmless Assistant with Reinforcement Learning from Human Feedback"
    url: https://arxiv.org/abs/2204.05862
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

偏好数据的质量主要由标注协议决定，所以先写清标准，再采数据。一致率低时，先修改题目、标准和示例，把分歧原因讲清楚；分歧来自标准含糊时，多加标注员也解决不了。InstructGPT 和 Anthropic HH 都把协议、标注员培训、一致率写成了管道的一部分，面试时也要讲到这一层，只报「找人标了 10 万对」说明不了数据质量。

## 怎么采

1. **写标准。** 说清比较什么、什么情况算平局，以及忠于事实比迎合用户更重要。
2. **生成候选。** 让当前模型生成两个回答，由人或校准过的 AI 选择。离线对过期了，就用当前策略重采，见 `dt-onpolicy-pref`。
3. **过滤。** 好坏差别太小、长度差过大、或者几乎重复的回答对，都过滤掉，见 `dt-pref-pair-code`、`dt-llama-edit-pref`。
4. **看一致率。** $\kappa$ 低时回到第 1 步，改题目和示例。
5. **保留独立验证。** 能执行验证的任务，保留独立的验证结果，和人偏好分开记录。

## 实践中的变化

AI 反馈可以用来起盘，但 judge 和生成器要分开，并且用人评做门禁，见 `dt-rlaif-loop`。如果预算只够 1 万条，就花在协议校准和难例上，见 `dt-human-budget`。

## 题目来源

Cohere 的公开题会问「偏好数据一致率低、标签吵，怎么修」；xAI 的设计题会出现基于人类反馈的强化学习（RLHF）的反馈采集。这些题面来自公开面试指南，没有逐字稿。方法上的参照是 InstructGPT 和 HH-RLHF。

## 追问

- **监督微调（SFT）用 chosen 训还不够，为什么还要 RLHF？** SFT 只是模仿被选中的那条。强化学习（RL）给模型自己采样出来的回答打分，能压住「示范里没写出来、但不该出现」的行为。代码这类可验证的领域，规则奖励往往比偏好奖励模型（RM）更干净。
- **Bradley-Terry RM 怎么验证？** 留一份人标 holdout，看准确率和校准。如果优化过程中 RM 分在涨、holdout 人评在掉，就是 reward hacking，该停。
- **标注员更偏爱长回答怎么办？** 协议里写明「短而对可以赢」，控制长度差，评测时按长度分层，见 `dt-length-hack-data`。

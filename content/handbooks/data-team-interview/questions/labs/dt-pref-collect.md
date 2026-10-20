---
id: dt-pref-collect
section: labs
order: 51
level: S
title: Cohere / xAI：偏好数据怎么采，一致率低了改什么？
quick: "先明确比较哪些维度、什么情况算平局，再让当前模型生成待比较的回答。标注一致性 $\\kappa$ 低时，先检查题目、标准和示例是否含糊。能执行验证的任务优先用规则奖励，人工主要判断自动检查不了的维度。"
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

先写清标注标准：比较什么，什么算平局，以及忠实于事实比迎合用户更重要。让当前模型生成两个回答，由人或校准过的 AI 选择。好坏差别太小、长度差过大，或几乎重复的回答对，应过滤掉，见 `dt-pref-pair-code`、`dt-llama-edit-pref`。$\kappa$ 低时，先修改题目和示例，把分歧原因讲清楚，而不是只增加标注员。可以执行验证的任务，应保留独立验证结果，不能用人偏好代替。

不这么选的理由：Cohere 公开题会问「偏好数据一致率低、标签吵，怎么修」；xAI 设计题会出现 基于人类反馈的强化学习（RLHF） 反馈采集。现场说「我们找人标了 10 万对」不够。InstructGPT 和 Anthropic HH 都把协议、人训、一致率写成管道，不是外包黑盒。

接到苹果：人标来自研究集和许可脚本，用户对话默认不进。AI 反馈可以起盘，judge 和生成器分家，人评门禁，见 `dt-rlaif-loop`。离线对过期就当前策略重采，见 `dt-onpolicy-pref`。端侧和 server 两套偏好别混。预算只够 1 万条，花在协议校准和难例，见 `dt-human-budget`。

公开锚点：InstructGPT、HH-RLHF。Cohere / xAI 的题面来自公开面试指南，不是逐字稿。

## 追问

- **为什么 监督微调（SFT） 吃 chosen 还不够，还要 RLHF？** SFT 模仿被选中的那条。强化学习（RL） 给你自己采样的回答打分，能压「没写出来但不该出现」的行为。代码等可验证域，规则奖励往往比偏好 奖励模型（RM） 干净。
- **Bradley-Terry RM 怎么验？** 留人标 holdout，看准确率和校准。优化中途 RM 分涨、holdout 人评掉，就是 hack，停。
- **标注员更爱长文怎么办？** 协议写短而对可以赢，控制长度差，评测长度分层，见 `dt-length-hack-data`。

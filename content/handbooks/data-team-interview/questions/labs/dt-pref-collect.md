---
id: dt-pref-collect
section: labs
order: 51
level: S
title: Cohere / xAI：preference data 怎么采，一致率低了改什么？
quick: >-
  preference data 的质量主要看 annotation guidelines：先写清比较哪些维度、什么算
  tie，再让当前模型生成待比较的回答。一致率 $\kappa$ 低时，先查题目、标准和示例是否含糊，改完再采；分歧来自标准本身时，加 annotator
  也压不下去。能执行验证的任务优先用 rule-based reward，人只判断自动检查不了的维度。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
  - title: >-
      Training a Helpful and Harmless Assistant with Reinforcement Learning from
      Human Feedback
    url: 'https://arxiv.org/abs/2204.05862'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

preference data 的质量主要由 annotation guidelines 决定，所以先写标准，再采数据；一致率低了，先改题目、标准和示例，把分歧的原因弄清楚。分歧出在标准含糊的话，多加 annotator 也解决不了。

比如标准只写了「选更好的回答」，一个 annotator 看重简洁，另一个看重全面，同一对回答两个人就会选反，再加多少人 $\kappa$ 也上不去。这时候该改的是标准，把比较哪个维度写清楚。

所以第一步是写标准：比较什么，什么情况算 tie，并且写明忠于事实比迎合用户更重要。候选让当前模型生成两个回答，由人或 经过 calibration 的 AI 来选；离线对过期了，就用 current policy 重采，见 `dt-onpolicy-pref`。采回来的对先过一遍滤，好坏差别太小、长度差太大、或者几乎重复的都去掉，见 `dt-pref-pair-code`、`dt-llama-edit-pref`。然后看一致率，$\kappa$ 低就回到写标准那一步，改题目和示例。能执行验证的任务，把独立的验证结果单独留着，和人偏好分开记。

InstructGPT 和 Anthropic HH 都把协议、annotator 培训、一致率当作管道的一部分写进了论文。面试时也要讲到这一层，只说「找人标了 10 万对」，说明不了数据质量。

题目来源上，Cohere 的公开题会问「preference data 一致率低、标签吵，怎么修」，xAI 的设计题会出现 RLHF 的反馈采集。这些题面来自公开面试指南，没有逐字稿，方法上参照的是 InstructGPT 和 HH-RLHF。

## 追问

**能用 AI 反馈代替人标吗？**
可以用来起盘，但 judge 和生成器要分开，并且用 human evaluation 做 evaluation gate，见 `dt-rlaif-loop`。

**预算只够 1 万条，怎么花？**
花在协议 calibration 和 hard examples 上，见 `dt-human-budget`。

**SFT 用 chosen 训还不够吗，为什么还要 RLHF？**
SFT 只是模仿被选中的那条。RL 给模型自己 sampling 出来的回答打分，能压住「示范里没写出来、但不该出现」的行为。代码这类可验证的领域，rule-based reward 往往比偏好 reward model（RM）更干净。

**Bradley-Terry RM 怎么验证？**
留一份人标 holdout，看准确率和 calibration。优化过程中 RM 分在涨、holdout human evaluation 在掉，就是 reward hacking，该停了。

**annotator 更偏爱长回答怎么办？**
协议里写明「短而对可以赢」，控制回答对之间的长度差，评测时按长度分层，见 `dt-length-hack-data`。

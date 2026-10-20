---
id: dt-userlog-contrast
section: labs
order: 3
level: S
title: OpenAI 练习题：用户对话怎么做成 SFT？在 Apple 为什么要改题？
quick: "用于苹果场景时，输入改为知情同意的研究集、许可语料和合成复现，仍要检查 PII、毒性、重复和数据版本。基础模型默认不使用用户交互；日志做了匿名化，也不等于已经获得训练许可。"
companies:
  - apple
tags:
  - OpenAI
  - Privacy
  - SFT Data
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: Applebot model training and individual privacy rights
    url: https://support.apple.com/en-us/120320
    type: primary
  - title: Datasets used for Apple Intelligence
    url: https://www.apple.com/legal/ai-regulations/training-data/
    type: primary
---

数据处理仍要检查 PII、去重、过滤毒性，并保证重复运行不会产生重复或不一致结果。输入改为经过知情同意的 user study、许可邮件语料，以及根据聚合失败类型生成的复现数据。不能默认把生产日志送入全球基础模型训练。opt-in「帮助改进」是单独通道，默认关，见 `dt-privacy-feedback`。

不这么选的理由：公开练习题经常写成从生产对话做出高质量微调集。InstructGPT 也用过人类示范和偏好，早期产品提示来自真实使用。原样搬到 AFM，通道就不成立。匿名化日志也不是合法燃料。

接到苹果：存储分为原文、隐私过滤后的文本和训练 shard，按内容标识版本，重复运行应产生一致结果。质量门仍是条数下限、PII 检出率、近重复、毒性、dataset hash 对得上版本。选择偏差也要说：愿意点赞的用户不是全体。隐式信号（复制、重试、改写）偏，而且能被游戏。这些闸门在研究集和许可语料上仍然成立。别处这题考闸门，苹果这轮多考通道。

公开锚点：InstructGPT 用过人示范和偏好；Applebot 支持页和 Apple Intelligence 训练数据页把基础模型燃料划在公开网页 / 许可集一侧。

## 追问

- **隐式反馈（用户改写了摘要）能不能当偏好对？** 端上可以留给 adapter。回传原文当 直接偏好优化（DPO），默认不行。
- **ChatGPT 那套为什么他们能做？** 产品契约和同意文案不同。我不评价对错，只陈述苹果当前公开口径。

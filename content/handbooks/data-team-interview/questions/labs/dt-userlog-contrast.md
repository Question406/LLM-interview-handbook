---
id: dt-userlog-contrast
section: labs
order: 3
level: S
title: OpenAI 练习题：用户对话怎么做成 SFT？
quick: "先确认这些对话有没有训练许可，再过数据闸门。PII、毒性、去重、可复现的数据版本这些检查都要做；没有许可的生产日志，换成知情同意的研究集、许可语料和按失败类型合成的复现。日志做了匿名化也不等于获得训练许可，点赞、重试这类隐式信号还要处理偏差。"
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

先确认这些对话能不能用来训练，再谈怎么做。数据处理的闸门照常要过：PII 检查、去重、毒性过滤、可复现的版本管理。生产日志没有训练许可时，输入换成经过知情同意的 user study、许可语料，以及根据聚合失败类型生成的复现数据。

## 为什么先问许可

公开练习题经常写成「从生产对话做出高质量微调集」。InstructGPT 确实用过人类示范和偏好，早期的产品提示来自真实使用。能不能这样做，取决于产品契约和同意文案。作为对照，苹果的 Applebot 支持页和 Apple Intelligence 训练数据页把基础模型的数据来源划在公开网页和许可集一侧。匿名化过的日志也不等于获得了训练许可；用户主动开启的「帮助改进」是单独的通道，见 `dt-privacy-feedback`。

## 闸门怎么设

1. 分层存储：原文、隐私过滤后的文本和训练 shard 分开存，按内容标识版本，重复运行应得到一致结果，不产生重复或不一致的数据。
2. 质量门：条数下限、PII 检出率、近重复、毒性，以及 dataset hash 与版本对得上。
3. 讲清偏差：愿意点赞的用户不代表全体；复制、重试、改写这些隐式信号有偏，而且能被刷。

这些闸门在研究集和许可语料上同样成立。

## 追问

- **用户改写了摘要，这种隐式反馈能当偏好对吗？** 先看许可范围。没有明确同意，原文不能回传去做直接偏好优化（DPO）；就算有许可，改写信号也有上面说的偏差，要先校正。

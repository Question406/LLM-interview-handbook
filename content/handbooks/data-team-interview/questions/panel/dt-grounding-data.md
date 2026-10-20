---
id: dt-grounding-data
section: panel
order: 13
level: A
title: Panel：幻觉怎么用数据压，而不是再写一句「请忠实」？
quick: "用「证据里没有某个细节」的题训练模型承认看不到，同时配上证据里确实有答案的题，防止它一律拒答。摘要、图片问答和工具状态的回答都要能指回证据。单写「不要幻觉」或使用开放世界 QA，不能替代这些训练数据。"
companies:
  - apple
tags:
  - Apple
  - Grounding
  - Hallucination
  - Synthetic Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
---

这类数据可以写成 $(E, q, a)$：$E$ 是给定证据，$q$ 是问题，$a$ 要么依据 $E$ 回答，要么说明证据不足。仅在系统提示中写「不要幻觉」，不足以防止模型生成无依据的细节。

端侧产品经常要求模型依据邮件、通知、屏幕或海报作答。开放世界 QA 测的是一般知识，不能直接教模型判断当前材料是否支持答案。提示词有帮助，但仍需要针对这些任务的训练数据。

## 数据形状要能指回证据

AFM 写明端侧不是开放 chatbot。监督微调（SFT） 里他们合成了故意问图中没有的东西、配上拒答。摘要侧提高 grounding 数据质量。工具任务以环境实际状态为准；事件没有创建，模型却说「已写入日历」，也属于幻觉。

该造的题就这几类：

- 应拒。$E$ 里没有时间，问几点。答案是看不到，不是编一个。
- 应抽。$E$ 里有，答案能指到 span 或字段。
- 应改写但不添。合法摘要，抽查新增实体。

评测不要只用 ROUGE。BLEU 对忠实几乎没帮助。发布检查应关注字段是否正确、是否泄露不该透露的信息，以及是否新增了无依据的实体。us-tech 的 Apple 卡也踩过 BLEU，这里从数据侧补。

开放世界知识缺口，用许可语料和 mid 配比补。让模型更会聊天的 SFT，不能替代依据证据作答的训练。

## 追问

- **拒答会不会太多？** 加 should-answer 反例，同一 $E$ 上成对出现「没有的问拒、有的问答」。只有拒答，模型会学到拒绝万能。
- **检索增强算不算有实际证据支持数据？** 检索块是 $E$。块错了，忠实于错块仍是产品事故。数据要标「块是否相关」。
- **PCC 上的 server 模型是不是可以开放幻觉？** 更强，契约仍看功能。Siri / 日历仍要有实际证据支持。

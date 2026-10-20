---
id: dt-legal-capability
section: hm-screen
order: 4
level: A
title: HM：能力缺口和隐私 / 许可打架，你站哪边？
quick: "先区分用途：训练全球基础模型、处理当前推理请求，还是改善设备上的 adapter。用户交互默认不能进入全球训练；PCC 推理也不意味着获得训练许可。来源不合格时，改用许可研究集、合成任务或端侧方案，匿名化不能替代使用授权。"
companies:
  - apple
tags:
  - Apple
  - Hiring Manager
  - Privacy
  - Licensing
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Applebot model training and individual privacy rights
    url: https://support.apple.com/en-us/120320
    type: primary
  - title: Datasets used for Apple Intelligence
    url: https://www.apple.com/legal/ai-regulations/training-data/
    type: primary
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
---

如果邮件摘要不好，先确认想改进哪一级模型、准备使用什么来源，再讨论数据方案。把真实邮件匿名化，并不自动意味着可以用于监督微调（SFT）。这个决策与 `dt-privacy-feedback` 中的数据通道限制一致。

## 区分三种用途

- 训练全球基础模型（FM）：使用许可语料、合规公开页面、Applebot 抓取内容、合成数据或知情同意的 user study。用户私有交互默认不在可用来源里。
- 处理当前请求：按需要在端侧或 PCC 使用最小内容片段。能用于一次推理，不等于能用于训练。
- 改善当前设备体验：通过 adapter 或本地检索适应用户口吻，不更新全球模型权重。

能力缺口说明需要补哪种任务，不决定可以使用哪种来源。例如摘要丢失限定词，可以找许可明确的邮件语料，并合成对抗删改题，而不是直接使用用户收件箱。来源被否决后，任务仍可能通过合成复现，见 `dt-when-not-synth`。

## 来源有冲突时怎么处理

对于网页 opt-out、书籍、歌词和新闻全文等高风险类别，未确认许可前先排除。公开可见不等于允许训练。Applebot 还区分可用于搜索与可用于基础模型训练，robots 可以只关闭后者。

与产品讨论时，说明必须满足治理要求，同时给出合法替代：许可研究集、合成复现或端侧方案。这样既守住来源限制，也继续处理能力缺口。

可以这样解释决定：「邮件摘要不好，全球模型先用许可邮件和合成对抗题；这台手机上的个人口吻可以用端上 adapter。若没有合适许可集，先用人评分清是事实忠实性还是文风问题。文风问题未必需要修改底座。」不能默认把用户点踩的原文加入 SFT。

## 追问

- opt-in「帮助改进 Apple Intelligence」允许日志 SFT 吗？它是一条单独通道，默认关闭，要能撤回，也要写清允许用于哪一级模型，不能当作日常日志回灌。
- 竞品使用对话日志会不会造成差距？在这里的公开约束下，能力差距通过许可、爬取、合成和验证来补。
- 研究集里的用户数据能用吗？知情同意的研究标注可以属于 user studies，静默生产日志不行。

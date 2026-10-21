---
id: dt-legal-capability
section: hm-screen
order: 4
level: A
title: HM：能力缺口和隐私 / 许可打架，你站哪边？
quick: "来源限制要守住，能力缺口换合法的路补。先分清要改进什么：训练全球基础模型、处理当前推理请求，还是改善这台设备上的 adapter。用户交互默认不能进入全球训练，PCC 推理也不等于获得训练许可。来源不合格时，改用许可研究集、合成任务或端侧方案；匿名化不能替代使用授权。"
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

我不把它当成二选一：来源限制必须守住，能力缺口换一条合法的路去补。能力缺口说明需要补哪种任务，但不决定可以用哪种来源。比如邮件摘要不好，我会先确认想改进哪一级模型、准备用什么来源，再讨论数据方案。把真实邮件匿名化，并不自动意味着可以拿来做监督微调（SFT）。这和 `dt-privacy-feedback` 中的数据通道限制一致。

## 先区分三种用途

- 训练全球基础模型（FM）：使用许可语料、合规公开页面、Applebot 抓取的内容、合成数据，或经过知情同意的 user study。用户私有交互默认不在可用来源里。
- 处理当前请求：按需要在端侧或 PCC 使用最小的内容片段。能用于一次推理，不等于能用于训练。
- 改善当前设备上的体验：通过 adapter 或本地检索适应用户的口吻，不更新全球模型权重。

## 来源被否决后怎么补

还是以摘要为例。如果问题是摘要丢失限定词，可以找许可明确的邮件语料，再合成对抗删改题；用户的收件箱不在可用来源里。来源被否决后，任务往往仍能通过合成复现，见 `dt-when-not-synth`。

网页 opt-out、书籍、歌词、新闻全文这些高风险类别，在确认许可之前先排除。公开可见不等于允许训练。Applebot 还区分了可用于搜索和可用于基础模型训练两种用途，robots 可以只关闭后者。

## 和产品方怎么谈

跟产品讨论时，先说明治理要求必须满足，同时给出合法的替代方案：许可研究集、合成复现或端侧方案。这样既守住了来源限制，也在继续处理能力缺口。

可以这样解释决定：「邮件摘要不好，全球模型先用许可邮件和合成对抗题；这台手机上的个人口吻可以用端上 adapter。若没有合适许可集，先用人评分清是事实忠实性还是文风问题。文风问题未必需要修改底座。」无论哪种情况，都不能默认把用户点踩的原文加入 SFT。

## 追问

- opt-in「帮助改进 Apple Intelligence」允许用日志做 SFT 吗？它是一条单独的通道，默认关闭，要能撤回，也要写清允许用于哪一级模型，不能当作日常日志回灌。
- 竞品使用对话日志，会不会造成差距？在这里的公开约束下，能力差距要靠许可、爬取、合成和验证来补。
- 研究集里的用户数据能用吗？经过知情同意的研究标注可以算 user studies，静默收集的生产日志不行。

---
id: dt-legal-capability
section: hm-screen
order: 4
level: A
title: HM：能力缺口和隐私 / 许可打架，你站哪边？
quick: "来源限制守住，能力缺口换合法的路补。先分清要改进的是全球基础模型、当前这次推理，还是这台设备上的 adapter：用户交互默认不进全球训练，PCC 推理也不等于拿到训练许可。来源不合格就换许可研究集、合成任务或端侧方案，匿名化替代不了使用授权。"
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

我不把它当二选一：来源限制守住，能力缺口换一条合法的路去补。缺口告诉我要补哪种任务，但不决定能用哪种来源。

比如邮件摘要做得不好，有人提议拿用户点踩的邮件来训。我会先问清楚要改进的是哪一级。训练全球基础模型，用的是许可语料、合规公开页面、Applebot 抓取的内容、合成数据，或者知情同意的 user study，用户私有交互默认不在里面。处理当前这次请求，在端侧或 PCC 用最小的内容片段，能用于一次推理不等于能用于训练。改善这台设备上的体验，就用 adapter 或本地检索去贴用户的口吻，不更新全球权重。这和 `dt-privacy-feedback` 讲的数据通道是一回事。把真实邮件匿名化，也不自动意味着可以拿去做 SFT。

来源被否了，任务往往还能复现。摘要丢限定词，就找许可明确的邮件语料，再合成对抗删改题，用户的收件箱不在可用来源里，见 `dt-when-not-synth`。网页 opt-out、书籍、歌词、新闻全文这些高风险类别，没确认许可之前先排除。公开可见不等于允许训练，Applebot 还把搜索和基础模型训练分成两种用途，robots 可以只关掉后者。

跟产品谈的时候，我会先说治理要求必须满足，同时把替代方案摆出来，这样限制守住了，能力缺口也还在往前推。大概会这么说：「全球模型先用许可邮件和合成对抗题；这台手机上的个人口吻用端上 adapter。如果没有合适的许可集，先用人评分清是事实忠实性还是文风问题，文风问题未必要动底座。」不管哪种情况，点踩的原文都不默认加入 SFT。

## 追问

**用户 opt-in「帮助改进 Apple Intelligence」了，日志能拿来做 SFT 吗？**
那是一条单独的通道。默认关闭，要能撤回，还要写清允许用于哪一级模型，不能当日常日志回灌。

**竞品用对话日志训练，会不会拉开差距？**
在这里的公开约束下，差距靠许可、爬取、合成和验证去补。

**研究集里的用户数据能用吗？**
知情同意的研究标注算 user studies，可以用；静默收集的生产日志不行。

**匿名化之后总可以用了吧？**
不行。匿名化替代不了使用授权，真实邮件匿名化之后也不自动变成 SFT 数据，来源本身还是要有许可。

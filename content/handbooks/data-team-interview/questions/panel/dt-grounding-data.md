---
id: dt-grounding-data
section: panel
order: 13
level: A
title: Panel：怎么用数据压 hallucination？
quick: >-
  造 (证据, 问题, 答案)
  形式的训练数据，证据里没有的细节答案就承认看不到，证据里有的答案要能指回证据。两类题在同一份证据上成对出现，防止模型学成一律拒答。摘要、图片问答和工具状态都按这个形状造，单写「不要
  hallucination」或用开放世界 QA 都替代不了。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: >-
      https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
---

要造 $(E, q, a)$ 这种形状的数据：$E$ 是给定证据，$q$ 是问题，$a$ 要么依据 $E$ 回答，要么说明证据不足。只在系统提示里写「不要 hallucination」，挡不住模型编出没有依据的细节。

举个例子，给模型一张图，图里没有时钟，问「现在几点」。模型没在训练里见过「证据里没有就说没有」的样本，就会顺着问题编一个时间。很多任务都要求依据给定的文档、邮件、图片或工具返回作答，模型要学的是判断「这份材料支不支持答案」；开放世界 QA 测的是一般知识，教不了这件事。prompt 有帮助，但不够。

所以我会造三类题。一类应拒，就像上面问时间；一类应抽，$E$ 里有答案，答案能指到具体的 span 或字段；还有一类是摘要这种应改写但不添加的，抽查有没有新增实体。应拒和应抽要在同一个 $E$ 上成对出现，只给拒答样本，模型会学到拒绝是万能答案。AFM 报告公开过类似的做法：SFT 里合成故意问图中没有的东西的题，配上拒答；摘要这一侧则提高 grounding 数据的质量。

工具任务也是同一个形状，证据是环境的实际状态。事件没有创建，模型却说「已写入日历」，也属于 hallucination。

评测也要跟上。ROUGE 只看字面重叠，BLEU 对忠实度几乎没帮助。发布检查看字段对不对、有没有泄露不该透露的信息、有没有新增无依据的实体。

最后要分清两种缺口。开放世界知识不够，用许可 corpus 和 mid 阶段 data mix 补；依据证据作答的能力，要靠上面这类数据，让模型更会聊天的 SFT 替代不了。

## 追问

**拒答会不会太多？**
会，所以要加 should-answer 的反例，在同一个 $E$ 上成对出现「没有的问拒、有的问答」。

**检索增强的结果算不算证据？**
算，检索出来的块就是 $E$。但块本身错了，忠实于错块照样给出错误答案，所以数据里要标注「这个块是否相关」。

**更大的模型能力更强，是不是可以放开一些 hallucination？**
看任务。需要依据材料作答的任务，模型再大也要有实际证据支持。

**怎么评测模型是不是忠实于证据？**
别用 ROUGE、BLEU 这类字面重叠指标，直接查字段是否正确、有没有泄露不该说的信息、有没有新增无依据的实体。

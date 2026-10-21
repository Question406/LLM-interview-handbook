---
id: dt-grounding-data
section: panel
order: 13
level: A
title: Panel：怎么用数据压幻觉？
quick: "造 (证据, 问题, 答案) 形式的训练数据：证据里没有的细节，答案是承认看不到；证据里有的，答案要能指回证据。两类题在同一份证据上成对出现，防止模型学成一律拒答。摘要、图片问答和工具状态都按这个形状造，单写「不要幻觉」或用开放世界 QA 都替代不了。"
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

这类数据可以写成 $(E, q, a)$：$E$ 是给定证据，$q$ 是问题，$a$ 要么依据 $E$ 回答，要么说明证据不足。只在系统提示里写「不要幻觉」，不足以阻止模型编出无依据的细节。

## 为什么提示词不够

很多任务要求模型依据给定的文档、邮件、图片或工具返回作答。模型要学会判断「当前这份材料是否支持答案」，开放世界 QA 测的是一般知识，教不了这件事。提示词有帮助，但模型没在训练里见过「证据里没有就说没有」的样本，就仍会顺着问题编一个答案。

## 该造哪几类题

- **应拒**：$E$ 里没有时间，却问几点。正确答案是说看不到时间。
- **应抽**：$E$ 里有答案，答案能指到具体的 span 或字段。
- **应改写但不添加**：合法的摘要，抽查有没有新增实体。

应拒和应抽要在同一个 $E$ 上成对出现。只给拒答样本，模型会学到「拒绝」是万能答案。AFM 报告公开过类似做法：监督微调（SFT）里合成故意问图中没有的东西的题，配上拒答；摘要这一侧则提高 grounding 数据的质量。

工具任务也是同一个形状，证据是环境的实际状态。事件没有创建，模型却说「已写入日历」，也属于幻觉。

评测也要跟上。ROUGE 只看字面重叠，BLEU 对忠实度几乎没帮助。发布检查应关注字段是否正确、是否泄露了不该透露的信息、是否新增了无依据的实体。

另外要分清两种缺口。开放世界知识不够，用许可语料和 mid 阶段配比补；依据证据作答的能力，要靠上面这类数据。让模型更会聊天的 SFT 替代不了后者。

## 追问

- **拒答会不会太多？** 会，所以要加 should-answer 的反例，在同一个 $E$ 上成对出现「没有的问拒、有的问答」。
- **检索增强的结果算不算证据？** 检索出来的块就是 $E$。但块本身错了，忠实于错块照样给出错误答案，所以数据里要标注「这个块是否相关」。
- **更大的模型能力更强，是不是可以放开一些幻觉？** 约束看任务。需要依据材料作答的任务，模型再大也要有实际证据支持。

---
id: dt-knows-what
section: labs
order: 33
level: A
title: Llama 3：后训练怎么让模型「知道自己会什么」？
quick: "先探测模型已经掌握什么，再教它对不会的题承认不知道。用事实题反复提问，若模型多次给出有具体信息却错误的回答，就加入承认不知道的示范；用 SFT 硬灌新知识更容易引发幻觉，新事件交给搜索。探测题从许可的预训练材料里生成。"
companies:
  - apple
tags:
  - Meta
  - Llama
  - Factuality
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: "Does Fine-Tuning LLMs on New Knowledge Encourage Hallucinations?"
    url: https://arxiv.org/abs/2405.05904
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

思路是先探测、再教拒答：找出模型反复答错的题，给这些题配上承认不知道的示范，让它学会区分自己会答和不会答的题。后训练在这里做的是校准，知识留给预训练和搜索。

## 为什么不再灌知识

Gekhman 等人的研究指出，通过微调学习新知识更容易引发幻觉。所以不要直接拿百科 QA 做 SFT 补知识；知识截止日期之后的事件，应交给搜索工具，见 `dt-when-to-search`，把这些新事实硬塞进监督微调（SFT），可能让模型自信地答错。

信息量高但错的回答，比「我不知道」更危险，因为人评偏爱流畅的回答，会奖励它。这和谄媚是同一个机制，见 `dt-sycophancy-data`。

## Llama 3 的做法

Llama 3 §4.3.6 讨论减少幻觉，原则是 know what it knows：用 Llama 3 对着预训练片段造事实题，再多次采样回答，以原文为参考，给正确性和信息量打分。具体步骤：

1. 从获得许可的预训练材料里取一个片段，据此生成事实题。
2. 让模型多次回答，对照原文分别判断答案是否正确、是否包含具体信息。
3. 模型反复给出具体却错误的回答，就生成承认不知道的示范。
4. 对预训练材料本身存在冲突的敏感问题，另收少量人工标注。
5. 同一模型家族的 judge 也可能有偏差，所以要人工抽查，并与固定的事实评测集对照。

标签要分清：「模型不知道」和「给定材料里没有」是两回事，不能混成一个标签。

## 和相邻题的分工

`dt-grounding-data` 检查信息是否出现在给定的邮件或图片里；这道题检查模型的参数是否已经掌握相关知识。`dt-webgpt-cite` 讨论检索和引用，这里讨论如何承认不知道。产品上要把这些方法结合起来：适合搜索的先搜，能找到来源的给出处，两者都没有时不要编。摘要这类任务尤其依赖源材料的支持，模型自称知道不算数。

## 追问

- **探测题会不会污染评测？** 会，如果片段是从评测相关页面抽的。要把片段的数据来源和处理历史记入 lineage，见 `dt-contamination`。

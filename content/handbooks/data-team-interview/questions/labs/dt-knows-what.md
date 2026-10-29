---
id: dt-knows-what
section: labs
order: 33
level: A
title: Llama 3：post-training 怎么让模型「知道自己会什么」？
quick: >-
  先探测模型已经会什么，再教它对不会的题承认不知道。拿事实题反复问，模型多次给出具体但错误的回答，就配上承认不知道的示范；用 SFT 硬灌新知识更容易引发
  hallucination，新事件交给搜索。探测题从许可的 pre-training 材料里生成。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: The Llama 3 Herd of Models
    url: 'https://arxiv.org/abs/2407.21783'
    type: primary
  - title: Does Fine-Tuning LLMs on New Knowledge Encourage Hallucinations?
    url: 'https://arxiv.org/abs/2405.05904'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

思路是先探测、再教拒答：找出模型反复答错的题，给这些题配上承认不知道的示范，让它学会分清自己会答和不会答的题。post-training 在这里做的是 calibration，知识留给 pre-training 和搜索。

举个例子，从一段 pre-training 文本里出一道题「某座小城是哪一年建城的」，让模型答好几次，它每次都给一个具体年份，每次还不一样，都不对。这说明它不知道，却在编，这道题就该配一个承认不确定的示范。

为什么不顺手把知识灌进去？Gekhman 等人的研究指出，通过 fine-tuning 学新知识更容易引发 hallucination。所以不拿百科 QA 做 SFT 补知识，知识截止之后的事件交给搜索工具，见 `dt-when-to-search`；把这些新事实硬塞进 SFT，模型可能自信地答错。信息量高但错的回答比「我不知道」更危险，因为 human evaluation 偏爱流畅的回答，会奖励它，这和 sycophancy 是同一个机制，见 `dt-sycophancy-data`。

Llama 3 §4.3.6 讨论减少 hallucination 时，原则就是 know what it knows：用 Llama 3 对着 pre-training 片段造事实题，再多次 sampling 回答，以原文为参考，给正确性和信息量打分。具体是从获得许可的 pre-training 材料里取一个片段生成事实题，让模型多答几次，对照原文分别判断答案对不对、有没有具体信息；模型反复给出具体却错误的回答，就生成承认不知道的示范。pre-training 材料本身就有冲突的敏感问题，另收少量人工标注。

标签要分清：「模型不知道」和「给定材料里没有」是两回事，不能混成一个标签。

## 追问

**judge 也是同一个模型家族，靠得住吗？**
可能有偏差。所以要人工抽查，并和固定的事实 evaluation set 对照。

**探测题会不会 contamination 评测？**
会，如果片段是从评测相关页面抽的。要把片段的数据来源和处理历史记进 lineage，见 `dt-contamination`。

**这题和 grounding、引用那几题怎么分工？**
`dt-grounding-data` 查信息有没有出现在给定的邮件或图片里，这题查模型的参数是不是已经掌握了相关知识。`dt-webgpt-cite` 讲检索和引用，这里讲怎么承认不知道。

**产品上这几种方法怎么配合？**
适合搜的先搜，能找到来源的给出处，两样都没有时就别编。摘要这类任务尤其依赖源材料的支持，模型自称知道不算数。

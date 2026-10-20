---
id: dt-knows-what
section: labs
order: 33
level: A
title: Llama 3：后训练怎么让模型「知道自己会什么」，而不是再灌知识？
quick: "用事实题探测模型已经掌握哪些知识。若模型多次给出有具体信息却错误的回答，就加入承认不知道的示范。新事件优先通过搜索获取；探测题来自许可材料，不能从用户文档里抽取。"
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

从获得许可的预训练材料里取一个片段，据此生成事实题，再让模型多次回答。对照原文，分别判断答案是否正确、是否包含具体信息。如果模型反复给出具体却错误的回答，就生成承认不知道的示范，让它学会区分自己会答和不会答的题。对预训练材料本身存在冲突的敏感问题，另收少量人工标注。

知识截止日期之后的事件，应使用搜索工具，见 `dt-when-to-search`。把这些新事实硬塞进监督微调（SFT），可能让模型自信地答错。同一模型家族的 judge 也可能有偏差，因此要人工抽查，并与固定的事实评测集对照。

不要直接拿百科 QA 做 SFT 补知识，也不要把「模型不知道」与「给定材料里没有」混成一个标签。Gekhman 等人的研究指出，通过微调学习新知识更容易引发幻觉。信息量高但错，比「我不知道」更危险：人评爱奖流畅，谄媚卡同一机制，见 `dt-sycophancy-data`。

与 `dt-grounding-data` 相比，那道题检查信息是否出现在给定邮件或图片里；这道题检查模型的参数是否已经掌握相关知识。和 `dt-webgpt-cite` 的分工：那道题讨论检索和引用，这里讨论如何承认不知道。产品需要结合这些方法：适合搜索的先搜，能找到来源的给出处，两者都没有时不要编。AFM 摘要尤其依赖源材料的支持，不能只凭模型自称知道。探测题会污染评测，如果从评测相关页抽的，要记录片段的数据来源和处理历史，见 `dt-contamination`。探测片段来自许可源，不从用户文档抽。

Llama 3 §4.3.6 讨论减少幻觉，原则是 know what it knows；用 Llama 3 对着预训练片段造事实题，再采样，以原文为参考打正确性和信息量。

## 追问

- **探测题会不会污染评测？** 会，如果从评测相关页抽的。片段来源进 lineage，见 `dt-contamination`。
- **后训练绝对不能教新事实？** 截止之后的事件走搜索工具，见 `dt-when-to-search`。强行用 SFT 教新事实，可能让模型自信地答错。
- **信息量高但错，为什么比「我不知道」更危险？** 人评爱奖流畅。谄媚卡同一机制，见 `dt-sycophancy-data`。

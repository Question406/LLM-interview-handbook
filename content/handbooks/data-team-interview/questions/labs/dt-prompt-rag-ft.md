---
id: dt-prompt-rag-ft
section: labs
order: 54
level: S
title: OpenAI / Cohere / Mistral：Prompt、RAG、微调，数据岗怎么站队？
quick: "依次问三个问题：知识经常变，或来源不允许进基础模型，就用带权限的 RAG 或工具；要改回答格式、工具习惯和拒答行为，做 SFT / RL；许可的世界知识属于预训练或 continued PT。租户私有文件走带租户键的检索，不写进权重。"
companies:
  - apple
tags:
  - OpenAI
  - Cohere
  - Mistral
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Datasets used for Apple Intelligence
    url: https://www.apple.com/legal/ai-regulations/training-data/
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
---

我会依次问三个问题，答案自然就出来了：知识会不会经常变，来源允不允许进基础模型，要改的是知识还是行为。

先看会不会变。比如内部 API 文档下周就要更新，这种优先用检索增强生成（RAG）或工具。微调只学得到当时那个版本，文档一更新，模型还可能给出旧答案。

再看授权。用户、租户、病历这类私有内容，要先确认能不能用于基础模型训练；没有授权就走带权限的 RAG，企业文档、用户邮件都放进检索，索引带租户键。现场要是背一句「微调最强」，结果就是把租户文件写进了权重。

最后看要改什么。格式、工具使用习惯、拒答边界都属于行为，适合后训练；世界知识要在预训练或 continued PT 里用许可数据来训。Llama 3 也写过，后训练管的是模型「会不会」，知识仍然在预训练里，见 `dt-knows-what`；InstructGPT 同样把示范和对齐分开来看。

题目来源上，公开题库把「Prompting, RAG or fine-tuning」记在 OpenAI、Mistral、Cohere、微软名下，题型跨公司重复，没有对应某一场的逐字稿。AceOffer 还有一条 ChatGPT Enterprise 的记录，题面是客户上传公司数据做定制。

## 追问

**客户要上传公司数据做定制，你怎么接？**
公司数据先走带租户键的检索，不写进权重。客户真正想改的如果是格式或口吻，再考虑用许可数据做后训练。

**模型总是编造工具参数怎么办？**
这是工具使用行为的问题，可以用包含执行返回的轨迹做 SFT 或 RL，见 `dt-traj-quality`。

**想让模型「记住」公司黑话呢？**
黑话放进检索的同义词表。如果想改的是口吻，用许可的内部研究集做小规模 SFT，整个邮箱不该当预训练数据。

**确定要微调了，改底座还是改 adapter？**
这是这道题的升级版，单独展开在 `dt-adapter-vs-base`。

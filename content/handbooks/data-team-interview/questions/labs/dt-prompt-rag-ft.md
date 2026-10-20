---
id: dt-prompt-rag-ft
section: labs
order: 54
level: S
title: OpenAI / Cohere / Mistral：Prompt、RAG、微调，数据岗怎么站队？
quick: "知识经常变化，或来源不允许进入基础模型时，用带权限的 RAG 或工具。要改变回答格式、工具习惯和拒答行为，可以做 SFT / RL。许可世界知识属于预训练或 continued PT，不能默认靠微调把租户文件写进权重。"
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

先判断知识是否经常变化。若内部 API 文档下周就会更新，优先用检索增强生成（RAG）或工具，避免把旧版本写进权重。再确认来源是否允许用于基础模型训练：用户、租户和病历等私有内容不能默认使用，可以走带权限的 RAG。最后区分目标：格式、工具使用习惯和拒答边界属于行为，适合后训练；世界知识的训练则需要预训练或 continued PT 中的许可数据。

不这么选的理由：公开题库把「Prompting, RAG or fine-tuning」记在 OpenAI、Mistral、Cohere、微软。现场背「微调最强」会把租户文件写进权重。Llama 3 也写过后训练管「会不会」，知识仍在预训练，见 `dt-knows-what`。

接到苹果：基础模型训练来源是许可语料、公开页面和经过验证的合成数据。企业文档、用户邮件走检索，索引带租户键。端侧短且隐私敏感的留本地。adapter 可以吃设备上的个人上下文，不回传。Director 的「改底座还是 adapter」是同一题的升级，见 `dt-adapter-vs-base`。

公开锚点：Apple Intelligence 训练数据页；InstructGPT 区分示范和对齐。AceOffer 有 ChatGPT Enterprise（客户上传公司数据做定制）一条。题型跨公司重复，不是单场逐字稿。

## 追问

- **内部 API 文档每周改？** RAG。微调只能学到当时的版本，文档更新后仍可能给出旧答案。
- **模型总把工具参数编造？** 这是工具使用行为问题，可以用包含执行返回的轨迹做 SFT 或 RL，见 `dt-traj-quality`。
- **想让模型「记住」公司黑话？** 黑话进检索同义词表。要改口吻，用许可的内部研究集做小 SFT，不要把全量邮箱当预训练。

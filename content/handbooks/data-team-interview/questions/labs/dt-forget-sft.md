---
id: dt-forget-sft
section: labs
order: 55
level: A
title: Mistral：微调之后旧能力掉了，数据怎么托底？
quick: "在 SFT 数据里保留通用指令、多语、安全和工具调用等旧任务，并同时评测新旧能力。旧能力退步超过阈值，就减少新任务权重或停止训练。KL 约束和 LoRA 都不能代替旧任务数据的回放。"
companies:
  - apple
tags:
  - Mistral
  - Continual Learning
  - Mix
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
---

针对新任务做监督微调，可能让模型遗忘旧任务。训练数据里应保留通用指令、多语、安全拒答和合法工具调用，并按 token 数分配配额。每轮同时评测新任务和这些旧任务。旧能力下降超过阈值，就减少新任务权重或停止训练。相对于 SFT 模型的 KL 约束可以限制变化，但仍需要旧任务数据。

不这么选的理由：公开题库把 catastrophic forgetting 记在 Mistral。现场只讲 LoRA 低秩所以忘得少。秩低也会忘，只是忘得慢；数据配比才是闸。InstructGPT 已经写过对齐会改能力剖面。

接到苹果：多语课程要护英语，代码退火要护通用，就是这张表。负迁移卡是同一诊断的产品版，见 `dt-neg-transfer`、`dt-data-mix-quota`。端侧 3B 容量更小，新能力更要用回放，不要指望再塞一轮合成把旧 locale 挤掉。adapter 和改底座的分界见 `dt-adapter-vs-base`。

公开锚点：Llama 3 后训练写过要保持通用；InstructGPT。Mistral 题型来自公开公司题库。

## 追问

- **回放多少？** 按锚点掉点调，不按感觉。可以先保留 10% 到 20% 的通用数据，再观察旧能力下降多少。要说明这只是起始经验值，最终比例需要实验比较。
- **LoRA 是不是就不用回放？** 仍要。LoRA 是容量约束，不是记忆保证。
- **安全训完开始乱拒？** 应拒和应答两桶一起回放，见 `dt-safety-refuse`。

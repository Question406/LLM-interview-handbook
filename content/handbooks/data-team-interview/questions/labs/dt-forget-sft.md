---
id: dt-forget-sft
section: labs
order: 55
level: A
title: Mistral：微调之后旧能力掉了，数据怎么托底？
quick: "靠旧任务数据回放来托底。在 SFT 数据里保留通用指令、多语、安全和工具调用等旧任务，每轮同时评测新旧能力；旧能力退步超过阈值，就减少新任务权重或停止训练。KL 约束和 LoRA 只能减慢遗忘，都不能代替回放。"
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

托底靠的是数据配比：训练新任务时，把旧任务的数据一起回放，并且每轮同时盯着新旧两组评测。公开题库把这道 catastrophic forgetting 题记在 Mistral。

## 为什么会掉，为什么 LoRA 不够

针对新任务做监督微调，会改变模型的能力剖面；InstructGPT 就写过对齐会改变模型在其他任务上的表现，Llama 3 的后训练也专门写了要保持通用能力。

现场常见的回答是「用 LoRA，秩低所以忘得少」。秩低也会忘，只是忘得慢。LoRA 限制的是更新的容量，保证不了旧能力留下来。相对于 SFT 模型的 KL 约束也一样，它能限制变化幅度，旧任务数据仍然要回放。

## 怎么做

1. **保留旧任务。** 训练数据里保留通用指令、多语、安全拒答和合法的工具调用，按 token 数分配配额。安全这一类要把应拒和应答两桶一起回放，否则训完容易开始乱拒，见 `dt-safety-refuse`。
2. **定回放比例。** 可以先保留 10% 到 20% 的通用数据，观察旧能力下降多少，再按锚点任务的掉点去调。这只是起始经验值，最终比例需要实验比较。
3. **设阈值。** 每轮同时评测新任务和旧任务，旧能力下降超过阈值，就减少新任务权重或停止训练。

## 实践中的变化

多语课程要保护英语，代码退火要保护通用能力，用的都是这张回放表。负迁移是同一套诊断，见 `dt-neg-transfer`、`dt-data-mix-quota`。

小模型容量更小，学新能力时更要靠回放；只靠再塞一轮合成数据，容易把旧语言的能力挤掉。什么时候该用 adapter、什么时候该改底座，见 `dt-adapter-vs-base`。

---
id: dt-forget-sft
section: labs
order: 55
level: A
title: Mistral：fine-tuning 之后旧能力掉了，数据怎么保住已有能力？
quick: >-
  通过 replay 旧任务数据来保住已有能力。SFT 数据里留着通用指令、multilingual、安全和 tool calls
  这些旧任务，每轮同时评新旧能力，旧能力退步超过阈值就减新任务权重或停训。KL 约束和 LoRA 只能让遗忘变慢，代替不了 replay。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: The Llama 3 Herd of Models
    url: 'https://arxiv.org/abs/2407.21783'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
---

保住已有能力靠的是 data mix：训新任务时把旧任务的数据一起 replay，每轮同时盯着新旧两组评测。公开题库把这道 catastrophic forgetting 题记在 Mistral 下面。

比如拿一批领域摘要数据做 SFT，训完摘要涨了，模型却开始乱拒普通问题，multilingual 回答也变差了。这就是旧能力被新任务挤掉了。

会掉，是因为针对新任务做 supervised fine-tuning (SFT) 会改变模型的能力剖面。InstructGPT 就写过对齐会改变模型在其他任务上的表现，Llama 3 的 post-training 也专门写了要保持通用能力。

现场常见的回答是「用 LoRA，秩低所以忘得少」。秩低也会忘，只是忘得慢。LoRA 限制的是更新的容量，保证不了旧能力留下来。

做法上，训练数据里保留通用指令、multilingual、安全拒答和合法的 tool calls，按 token 数分配配额。安全这一类要把应拒和应答两桶一起 replay，只 replay 应拒的，训完容易开始乱拒，见 `dt-safety-refuse`。每轮同时评新旧任务，旧能力掉过阈值，就减少新任务权重或者停训。

## 追问

**加一个相对 SFT 模型的 KL 约束够不够？**
不够。KL 能限制变化幅度，旧任务数据还是要 replay。

**multilingual 课程、代码 annealing 也会遇到这个问题吗？**
会，用的都是这张 replay 表：multilingual 课程要保护英语，代码 annealing 要保护通用能力。negative transfer 是同一套诊断，见 `dt-neg-transfer`、`dt-data-mix-quota`。

**small model 有什么不一样？**
容量更小，学新能力时更要靠 replay。只靠再塞一轮 synthetic data，容易把旧语言的能力挤掉。

**replay 比例一开始定多少？**
可以先放 10% 到 20% 的通用数据，看旧能力掉多少，再按 regression tasks 的掉点去调。这只是起始经验值，最终比例要靠实验比较。

相关：`dt-adapter-vs-base`（什么时候用 adapter、什么时候改 base model）

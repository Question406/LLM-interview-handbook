---
id: dt-longctx-data
section: panel
order: 15
level: A
title: Panel：长上下文数据怎么造，短了补长度、长了丢能力怎么避免？
quick: "长度本身教不会模型跨段检索，要用真实长文（许可书籍、代码仓库）加上把可核验答案埋在不同位置的合成长文，同时混入上一阶段的短数据，防止短任务退步。单纯 padding 或重复拼接短文只增加长度，没有需要查找的信息。AFM 用这三类数据把序列扩展到 65K。"
companies:
  - apple
tags:
  - Apple
  - Long Context
  - Mid-training
  - Synthetic Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: Apple Intelligence Foundation Language Models (2024)
    url: https://arxiv.org/abs/2407.21075
    type: primary
---

长上下文能力来自数据里有需要跨段查找的信息，序列变长本身教不会这件事。把短聊天重复 16 次凑成 32k，模型学不到跨段检索。我会用真实长文，加上把可核验答案埋在不同位置的合成任务，再混入上一阶段的短数据，保住短任务能力。

## 为什么拼接短文没用

只把短文档 pad 或重复拼接，序列是长了，但里面没有任何信息需要跨段去找，模型学到的只是「后面的内容和前面无关」。只要求阅读长文、却没有需要查找或推理的信息，就缺少训练检索能力的信号。

## 三类数据各教什么

- **自然长文**：许可书籍、代码仓库。教的是真实的依赖关系可以跨很多页。
- **合成长文**：专门针对上下文学习（ICL）和检索，比如答案埋在中间、多跳引用。合成长文要可验证：针放在第 $k$ 段，问模型还能不能取回。
- **上一阶段 continued 的数据**：用来保住短上下文能力。

AFM 2025 的 context 阶段把序列扩到 65K，用的就是这三类数据。2024 报告里还有一个先短后长的配方：先做约 1T token 的 8k continued 训练，再加合成长文做 lengthening。

评测时把找针、多跳和短题回归一起报。短题掉了就是负迁移，见 `dt-neg-transfer`。

## 追问

- **lost in the middle（中间失落）怎么用数据解决？** 把针均匀埋在前、中、后，别全埋在开头。合成时记录针的位置，评测按位置切片报。
- **代码仓库当长文会不会泄漏评测？** 会。HumanEval、LiveCodeBench 要先隔离，见 `dt-contamination`。
- **把短文 packing 到一起算长上下文吗？** 注意力看到的是长序列，任务仍是短文档。损失（loss）还要按文档切断，见 `dt-packed-sft-code`。

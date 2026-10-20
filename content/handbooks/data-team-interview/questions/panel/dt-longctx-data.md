---
id: dt-longctx-data
section: panel
order: 15
level: A
title: Panel：长上下文数据怎么造，短了补长度、长了丢能力怎么避免？
quick: "用许可书籍、代码仓库等真实长文，加上针对上下文学习和检索设计的合成长文；同时保留上一阶段的短数据，防止短任务退步。AFM 扩展到 65K。单纯 padding 或重复拼接短文，只增加长度，不能教会模型处理跨段依赖。"
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

长上下文训练需要合适的数据配比。把短聊天重复 16 次凑成 32k，无法教会模型跨段检索。应使用真实长文，以及把可核验答案埋在不同位置的合成任务，再混入上一阶段的短数据，保住短任务能力。

不这么选的理由：只把短文档 pad 或重复拼接，模型学的是无聊，不是检索。如果只要求阅读长文，却没有需要查找或推理的信息，就缺少训练检索能力的信号。

## 长文从哪来，各自教什么

AFM 2025 context 段：序列到 65K，来自

- 自然长文：许可书、代码仓库。教的是真实依赖跨很多页。
- 合成长文：专门打 ICL 和检索。例如答案埋在中间、多跳引用。
- 前一段 continued 的数据。用来保住短上下文能力。

2024 报告还有 8k continued 约 1T、再加合成长文做 lengthening 的配方。面试把「先短后长」说成课程即可，不要编他们内部步数。

合成长文要可验证：针在第 $k$ 段，问还能不能取回。评测用针、多跳、短题回归，一起报。短题掉了就是负迁移，见 `dt-neg-transfer`。

端侧 3B 的产品任务多数不需要 65K。server / PCC 才吃这一段。数据仍可两端共用，抽样长度按部署。

## 追问

- **中间失落怎么用数据打？** 把针均匀埋在前 / 中 / 后，不要全埋开头。合成时记录针的位置，切片报。
- **代码仓库当长文会不会泄漏评测？** 会。HumanEval / LiveCodeBench 先隔离，见 `dt-contamination`。
- **packing 短文算长上下文吗？** 注意力看见了长序列，任务仍是短文档。损失（loss） 还要按文档切断，见 `dt-packed-sft-code`。

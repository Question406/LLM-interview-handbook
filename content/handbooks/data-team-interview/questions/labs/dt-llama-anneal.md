---
id: dt-llama-anneal
section: labs
order: 6
level: A
title: Llama 3：预训练最后抬高质代码 / 数学（annealing），有什么用？
quick: "Annealing 在主预训练末段降学习率、上采样高质量数学和代码，补可验证的能力；格式和工具行为留到后训练。Llama 3 最后约 40M token 是它自己的公开配方，换模型要重新定；常用基准的训练集不能混进这一段。它还可以用来低成本评估新数据源。"
companies:
  - apple
tags:
  - Meta
  - Llama
  - Mid-training
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
  - title: Updates to Apple’s On-Device and Server Foundation Language Models
    url: https://machinelearning.apple.com/research/apple-foundation-models-2025-updates
    type: primary
---

Annealing 是在主预训练末段降学习率、调整数据配比，补足能力。可验证的数学和代码能力放在 mid-training 或 annealing 阶段补，格式和工具行为留到后训练阶段调整。阶段划分见 `dt-pre-mid-post`。

## Llama 3 的公开配方

Llama 3 在最后 40M token 线性降低学习率，并上采样高质量来源，明确不含常用基准的训练集。公开的 mix 大约是 50% 通用、25% 数学推理、17% 代码、8% 多语。

他们还做了对照：把 GSM8K / MATH 训练集放进 annealing，8B 的验证分数分别约 +24.0% / +6.4%，405B 上的提升可以忽略。405B 不吃 GSM8K 训练集仍然很强，说明大模型能靠 ICL 补上小模型要靠 annealing 才能补的洞。

这里有两个容易犯的错。一是把这 40M 当成通用配额：那是 Llama flagship 末段的数字，别家的同类阶段可以长得多，AFM 2025 报告的 continued PT 就是万亿级 token，用验证过的合成数据和高质量原始数据，多语比例从 8% 提到 30%。二是把 GSM8K / MATH 训练集放进这一段刷 few-shot：用于评测的基准训练集不要混入，见 `dt-contamination`。

## 实践中的变化

小模型更依赖 mid-training 的数据，这一段的数据更值钱，8B 和 405B 的对照就是例子。合成的数学和代码题要过标准答案，门禁仍用真实来源。

Annealing 还能用来评估许可的小数据集：拿半训的小模型，按新来源 30%、旧 mix 70% 做一段退火，看效果。这种方法便宜，结论最后仍要在目标模型上用冻结切片验证。

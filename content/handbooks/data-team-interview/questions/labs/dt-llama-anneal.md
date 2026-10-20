---
id: dt-llama-anneal
section: labs
order: 6
level: A
title: Llama 3：预训练最后抬高质代码 / 数学（annealing），和 AFM continued PT 怎么对？
quick: "把可验证的数学、代码能力放在 mid-training 或退火阶段补充，格式和工具行为放在后训练中调整。AFM continued PT 也使用验证过的合成数据和高质量原始数据。Llama 的最后约 40M token 是其公开配方，不能直接当成内部训练配额。"
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

可验证的数学和代码能力可以在 mid-training 或 annealing 阶段补充，格式和工具行为在后训练阶段调整。用于评测的基准训练集不要混入这一阶段。AFM 的 continued PT 更长，使用验证合成、高质量原始数据和部分大规模语料；多语比例从 8% 提到 30%，之后再加入视觉并扩展到 65K 上下文。这些阶段都在主预训练之后调整数据配比，补足能力，名字不同并不影响这种比较。见 `dt-pre-mid-post`、`dt-contamination`。

不这么选的理由：把 Llama 最后约 40M 文本处理单位（token） 的 annealing 当成内部配额，或把 GSM8K / MATH 训练集放进这一段刷 few-shot。40M 是 Llama flagship 末段。AFM mid 是万亿级 token 量级的另一段。

接到苹果：许可小集可以用半训小模型评估（新源 30%、旧 mix 70%），替代不了目标模型上的冻结切片。端侧 3B 更接近 Llama 8B 那条：mid 数据更值钱。405B 不吃 GSM8K 训练集仍强，说明大模型可以用 ICL 补小模型要靠 anneal 的洞。合成题要过标准答案，门禁仍用真源。

公开锚点：Llama 3 最后 40M token 线性降学习率并上采样高质源，明确不含常用基准训练集；对照把 GSM8K / MATH 训练集放进 annealing，8B 验证分别约 +24.0% / +6.4%，405B 可忽略。公开 mix 大约 50% 通用、25% 数学推理、17% 代码、8% 多语。

## 追问

- **40M 够吗？** 那是他们 flagship 末段。AFM mid 是万亿级 token 量级的另一段。40M 是 Llama 的数，不是内部配额。
- **用 annealing 评估小源靠谱吗？** 便宜，适合许可小集。替代不了目标模型上的冻结切片。

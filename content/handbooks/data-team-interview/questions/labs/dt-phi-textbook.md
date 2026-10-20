---
id: dt-phi-textbook
section: labs
order: 50
level: A
title: Microsoft Phi：教科书数据搬到 AFM，哪一句要改？
quick: "Phi 说明，提高每个 token 的信息质量可以改善训练效果，并不意味着数据越少越好。AFM 可以借鉴网页过滤和可验证合成，但世界知识与多语言仍需要足够覆盖；教师模型泄漏考题的问题，也不能只靠 n-gram 去重排除。"
companies:
  - apple
tags:
  - Microsoft
  - Phi
  - Data Quality
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Textbooks Are All You Need
    url: https://arxiv.org/abs/2306.11644
    type: primary
  - title: Phi-4 Technical Report
    url: https://arxiv.org/abs/2412.08905
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

Phi 强调提高每个 token 的信息质量，并不主张 token 越少越好。Phi-1 用过滤后的代码和 GPT-3.5 合成教材训练，约 1.3B 的模型在 HumanEval 上超过了使用更脏数据的更大模型。Phi-4 在预训练中广泛使用合成数据，也指出标准 n-gram 检查挡不住改写带来的泄漏。

AFM 可以借鉴过滤和可验证合成，但世界知识仍需要足够规模的许可网页。端侧 3B 模型也不能只靠一份合成教材覆盖所有语言和地区。

不能只说「教科书数据质量高」，也不能把 Phi-1 的 7B token 当成后续模型都适用的规模。后续代际增加了数据量，关注信息质量的思路仍在。

用于苹果场景时，教育价值分类器要按语言校准，代码数据不能使用网页分类器，见 `dt-quality-clf-synth`、`dt-filter-too-hard`。合成习题必须过执行或标准答案。污染分三层：网文撞题、教师间接泄漏、改写绕过滤。发布检查要使用新近设计的题和私有评测子集。和 `dt-more-vs-better`、`dt-lima-vs-scale` 对刷：对齐阶段可以用少量精选数据，预训练仍需要足够多未见过的 token。

公开锚点：Phi-1 / Phi-4 技术报告。微软数据岗会把这题问成质量轴怎么操作、怎么证明没背考题。不是某一场逐字面经。

## 追问

- **同样数据喂 70B？** 应该喂。数据质量和参数规模是两件可以同时改善的事。小模型实验也与部署约束有关。
- **合成算不算蒸馏？** 算手段。Phi-4 说在部分 STEM 上超过教师，那要靠可校验合成和新鲜题，口头「超越 GPT-4」不算。
- **过滤会不会洗掉方言？** 会。教育价值头偏正式英文。产品要 locale，阈值单独切，见 `dt-locale-data`。

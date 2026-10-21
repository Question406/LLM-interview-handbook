---
id: dt-phi-textbook
section: labs
order: 50
level: A
title: Microsoft Phi：教科书式合成数据为什么有效，局限在哪？
quick: "有效是因为提高了每个 token 的信息质量：Phi-1 用过滤代码加合成教材，让 1.3B 模型在 HumanEval 上超过更大的模型。局限在规模和污染：世界知识和多语言仍需要足够多的许可网页，后续几代 Phi 也都加了数据量；教师模型和改写带来的考题泄漏，n-gram 去重挡不住，要用新题和私有评测检查。"
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

Phi 有效，是因为它提高了每个 token 的信息质量。它没有说明 token 越少越好：世界知识和多语言仍需要足够规模的许可网页，一份合成教材覆盖不了所有语言和地区。可以借鉴的是质量过滤和可验证的合成。

## Phi 实际说明了什么

Phi-1 用过滤后的代码加 GPT-3.5 合成的教材训练，约 1.3B 的模型在 HumanEval 上超过了用更脏数据训练的更大模型。这说明信息密度很重要。Phi-1 的 7B token 只是那一代的规模，后续几代都增加了数据量，保留下来的是关注信息质量的思路。Phi-4 在预训练中大量使用合成数据，同时指出标准 n-gram 检查挡不住改写带来的泄漏。

## 借鉴时怎么做

1. **过滤。** 教育价值分类器要按语言校准，代码数据用单独的分类器，见 `dt-quality-clf-synth`、`dt-filter-too-hard`。
2. **合成。** 合成习题必须通过执行或核对标准答案。
3. **防污染。** 污染分三层：网页文本撞上考题、教师模型间接泄漏、改写绕过过滤。发布检查要用新近设计的题和私有评测子集。

这题可以和 `dt-more-vs-better`、`dt-lima-vs-scale` 放在一起看：对齐阶段可以用少量精选数据，预训练仍需要足够多没见过的 token。

## 题目来源

依据是 Phi-1、Phi-4 技术报告。微软数据岗会把这题问成「质量这条轴怎么操作、怎么证明模型没有背考题」，这是根据报告整理的常见问法，没有对应某一场面试的逐字记录。

## 追问

- **同样的数据喂给 70B 呢？** 应该喂。数据质量和参数规模是可以同时改善的两件事，用小模型做实验也和部署约束有关。
- **合成算不算蒸馏？** 算是一种手段。Phi-4 说在部分 STEM 任务上超过了教师，这要靠可校验的合成和新鲜题来证明。
- **过滤会不会把方言洗掉？** 会。教育价值分类头偏向正式英文。要覆盖各 locale，阈值就要单独切，见 `dt-locale-data`。

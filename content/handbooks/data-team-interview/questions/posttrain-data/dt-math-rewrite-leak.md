---
id: dt-math-rewrite-leak
section: posttrain-data
order: 5
level: A
title: MetaMath 那种改写 GSM8K，什么时候是数据增强，什么时候是泄漏？
quick: "改写可以用于增强，但种子不能来自冻结评测题，答案要重新计算，评测也要使用独立题目。训练和测试都围绕 GSM8K 的同一题族时，即使换数字、换问法，也可能泄漏。遇到合成集自称 MATH 提高 15%，先检查种子和重叠。"
companies:
  - apple
tags:
  - Apple
  - Math
  - Contamination
  - Synthetic Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: MetaMath
    url: https://arxiv.org/abs/2309.12284
    type: primary
  - title: Training Verifiers to Solve Math Word Problems (GSM8K)
    url: https://arxiv.org/abs/2110.14168
    type: primary
  - title: LiveCodeBench
    url: https://arxiv.org/abs/2403.07974
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

改写要满足三个条件：种子不来自冻结评测题，标准答案重新计算，评测使用独立题目。开源合成集自称「MATH +15%」时，先排查污染，见 `dt-synth-bench-trap`。

训练都来自 GSM8K 改写，测试也用 GSM8K，模型可能只是记住同一题族。换 SVAMP / GSM-Hard / 新年度 AIME 就掉。这和代码的 HumanEval 泄漏同构，见 `dt-code-bench-bleed`。MetaMath 把 GSM8K / MATH 改成正向、反向、改问法再 监督微调（SFT），公开分很高。数据岗要会拆：这是在门禁分布上做增强，还是把评测洗进训练集。

苹果：AFM 写的改写网页是题面多样，不是改 GSM8K test。种子来自许可页和人写小题。用户日志不进基础模型。

## 增强合法的条件

种子不在冻结门禁里。演化后的题再和门禁做 n-gram / 嵌入，命中进 quarantine，见 `dt-ngram-contam-code`。

金标是新算出来的，不是从原题抄。反向题（已知答案求未知条件）要自己验。

评测另用新竞赛题、内部人工编写题，或按时间隔离的题目。GSM8K test 本身不能既当种子又当门禁。LiveCodeBench 用时间切挡同类问题。

WizardMath / MathInstruct 一类公开集很多从 GPT-3.5/4 出，种子往往就是这些评测。OpenMathInstruct 特意讨论过许可和格式，但你仍要自己扫重叠。

## 追问

- **改到嵌入也不像，还算泄漏吗？** 题族泄漏更难从字符串发现：题目可能共享模板和数字关系，却使用不同的文字。抽模板 id，按模板切 train/eval，见 `dt-hash-split-code`。
- **内部金标能不能演化？** 能。这是正道。演化器和评测生成器不要同一输入提示。
- **AFM 写的改写网页呢？** 那是题面多样，不是改 GSM8K test。种子来自许可页和人写小题。

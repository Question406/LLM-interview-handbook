---
id: dt-math-rewrite-leak
section: posttrain-data
order: 5
level: A
title: MetaMath 那种改写 GSM8K，什么时候是 data augmentation，什么时候是 leakage？
quick: >-
  三条都满足才算增强：seed 不来自冻结评测题、答案重新计算、评测用独立题目。训练和测试都围着 GSM8K
  同一题族时，换数字、换问法也可能只是让模型记住题族，换到 SVAMP、GSM-Hard 就掉分。看到合成集自称 MATH 提高 15%，先查 seed
  和重叠。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: MetaMath
    url: 'https://arxiv.org/abs/2309.12284'
    type: primary
  - title: Training Verifiers to Solve Math Word Problems (GSM8K)
    url: 'https://arxiv.org/abs/2110.14168'
    type: primary
  - title: LiveCodeBench
    url: 'https://arxiv.org/abs/2403.07974'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

看三个条件：seed 不来自冻结的评测题，标准答案是重新算出来的，评测用的是独立题目。三条都满足，改写才是 data augmentation；训练和测试只要围着同一个题族转，换数字、换问法也可能是 leakage。

比如把一道 GSM8K 题的数字换掉，再把问法从求总数改成求单价，文字看着是新题，解法的骨架还是原来那道。MetaMath 做的就是这类事：把 GSM8K / MATH 的题改成正向、反向、换问法，再做 SFT，公开分数很高。如果训练全来自 GSM8K 改写，测试也用 GSM8K，模型可能只是记住了这个题族，换到 SVAMP、GSM-Hard 或新一年的 AIME 就掉分。代码里的 HumanEval leakage 也是这个结构，见 `dt-code-bench-bleed`。所以数据岗要能拆开看，这是在 held-out evaluation distribution 上做增强，还是把评测洗进了 training set。

## 合法的增强怎么做

先管 seed，seed 不能在 frozen evaluation set 里。演化出来的题还要再和 evaluation gate 做一次 n-gram / embedding 比对，命中的进 quarantine，见 `dt-ngram-contam-code`。

再管 gold labels。答案要重新计算，不能从原题抄；反向题（已知答案、求未知条件）尤其要自己验。

最后管评测，用新竞赛题、内部人工编写的题，或按时间隔离的题。GSM8K test 不能既当 seed 又当 evaluation gate。LiveCodeBench 就是靠时间切分挡住同类题的。

## 追问

**改到 embedding 上都不像了，还算 leakage 吗？**
可能还算。题族 leakage 比字符串重复更难发现，题目可能共享模板和数字关系，只是文字不同。可以抽出模板 id，按模板切 train/eval，见 `dt-hash-split-code`。

**开源合成集能直接混进来吗？**
先扫重叠再说。WizardMath / MathInstruct 这类数据很多是 GPT-3.5/4 生成的，seed 往往就是这些评测题。OpenMathInstruct 专门讨论过许可和格式，但你仍然要自己扫一遍。看到开源合成集自称「MATH +15%」，先排查 contamination，见 `dt-synth-bench-trap`。

**内部 gold-standard examples 能不能拿来演化？**
能，这是正路。只是演化器和评测生成器不要用同一个 prompt。

**怎么判断一次提升是增强还是 leakage？**
换到独立的题上再测。在 GSM8K 上涨、到 SVAMP、GSM-Hard 或新一年的 AIME 上不涨，多半是记住了题族。

相关：`dt-code-bench-bleed`、`dt-ngram-contam-code`、`dt-hash-split-code`、`dt-synth-bench-trap`

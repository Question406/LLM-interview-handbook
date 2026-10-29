---
id: dt-phi-textbook
section: labs
order: 50
level: A
title: Microsoft Phi：教科书式 synthetic data 为什么有效，局限在哪？
quick: >-
  Phi 有效是因为提高了每个 token 的信息质量：Phi-1 用过滤代码加合成教材，让 1.3B 模型在 HumanEval
  上超过更大的模型。局限在规模和 contamination，世界知识和 multilingual 仍需要足够多的许可网页，后续几代 Phi
  也都加了数据量；teacher model 和改写带来的考题 leakage，n-gram deduplication 挡不住，要用新题和私有评测检查。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Textbooks Are All You Need
    url: 'https://arxiv.org/abs/2306.11644'
    type: primary
  - title: Phi-4 Technical Report
    url: 'https://arxiv.org/abs/2412.08905'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

Phi 有效，是因为它提高了每个 token 的信息质量，它并没有证明 token 越少越好。世界知识和 multilingual 仍然需要足够规模的许可网页，一份合成教材覆盖不了所有语言和地区。能借鉴的是质量过滤和可验证的合成。

Phi-1 是最直接的例子。它用过滤后的代码加 GPT-3.5 合成的教材训练，约 1.3B 的模型在 HumanEval 上超过了用更脏数据训练的更 large model，说明信息密度很重要。不过 Phi-1 的 7B token 只是那一代的规模，后面几代都加了数据量，延续下来的是盯住信息质量这个思路。到 Phi-4，pre-training 里大量用 synthetic data，同时报告里也承认，标准的 n-gram 检查挡不住改写带来的 leakage。

自己借鉴的话，先做过滤。教育价值分类器要按语言分别做 calibration，代码数据用单独的分类器，具体见 `dt-quality-clf-synth`、`dt-filter-too-hard`。然后是合成，合成出来的习题必须通过执行或者核对标准答案才留下。最后是防 contamination，leakage 有三个来源：网页文本直接撞上考题，teacher model 间接 leakage，改写绕过了过滤。后面两种靠 n-gram deduplication 查不干净。

这题可以和 `dt-more-vs-better`、`dt-lima-vs-scale` 放在一起看：对齐阶段可以用少量精选数据，pre-training 仍然需要足够多没见过的 token。

题目依据是 Phi-1 和 Phi-4 的技术报告。微软数据岗会把它问成「质量这条轴怎么操作、怎么证明模型没有背考题」，这是按报告整理的常见问法，没有对应某一场面试的逐字记录。

## 追问

**怎么证明模型没有背考题？**
用新近设计的题和私有评测子集来测。teacher leakage 和改写 leakage n-gram 检查挡不住，只有模型没见过的题才说明得了问题。

**同样的数据喂给 70B 呢？**
应该喂。数据质量和参数规模是可以同时改善的两件事，Phi 用 small model 做实验，也和部署约束有关。

**合成算不算 distillation？**
算是一种手段。Phi-4 说在部分 STEM 任务上超过了 teacher，这要靠可校验的合成和新鲜题来证明。

**过滤会不会把方言洗掉？**
会。教育价值分类头偏向正式英文，要覆盖各个 locale，阈值就得分开切，见 `dt-locale-data`。

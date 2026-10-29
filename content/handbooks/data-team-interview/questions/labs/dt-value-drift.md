---
id: dt-value-drift
section: labs
order: 21
level: S
title: Anthropic 笔试：fine-tuning 之后怎么证明模型相对 base model「漂了」？
quick: >-
  漂本身不坏，要证明的是偏离发生在声明的轴上、已有能力还在。用同一批固定 prompt 对比 base model 和 fine-tuned model：按
  evaluation slices 算 KL，跑行为套件，分开报安全与有用性，再做分维度 human evaluation。KL
  大只说明分布变了，好坏要靠行为套件和 human evaluation 判断，总 loss 和 Arena 赢率给不出这些信息。对照数据用研究集和
  frozen evaluation set。
companies:
  - apple
tags:
  - Anthropic
  - Evaluation
  - Preference
  - Apple
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: 'Anthropic AI Research Engineer Full Loop (HackTheRounds, 2025)'
    url: >-
      https://www.hacktherounds.com/blog/anthropic-ai-research-engineer-full-loop-interview-experience-2025-offer
    type: candidate-first-hand
  - title: Training language models to follow instructions with human feedback
    url: 'https://arxiv.org/abs/2203.02155'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

漂本身不一定坏，SFT 和 RL 本来就是要让模型离开 base model。要证明的是，偏离发生在我们声明要改的那些轴上，同时已有能力还在。所以要分轴、按 evaluation slice 地看，一个 KL 数字或一句「Arena 赢了」回答不了这个问题。

KL 大只说明模型走远了，说明不了变好还是变坏。比如一个模型学会了处处附和用户，Arena 赢率和总体 human evaluation 都可能往上走，只保留一个「更好」分数，sycophancy 就被当成了进步。InstructGPT 也写过，对齐会改变模型的能力剖面，所以要分维度看哪些能力变了。

我会从四个角度查，都用同一批固定 prompt，让 base model 和 fine-tuned model 并排比。先看输出分布，在固定 prompt 集上算 $\mathrm{KL}(\pi\|\pi_{\mathrm{base}})$ 或 $\mathrm{KL}(\pi\|\pi_{\mathrm{SFT}})$，按 capability slices 报告。再跑行为套件，拒答、sycophancy、有实际证据支持、tool calls 合法性、locale，两个模型在同一题上比。然后看安全税，有用性 evaluation slices 和应拒 evaluation slices 分开报，见 `dt-safety-refuse`。最后做小规模双人标注的 human evaluation，忠实、礼貌和完整性分别评，不合并成一个分。对照集用研究集和 frozen evaluation set。

题目来源是 2025 年一场 Anthropic RE 的 CodeSignal 短答题，问「怎么衡量 fine-tuned model 相对 base model 发生了 value drift」。同场另一道是 RLHF 系统性奖励不诚实，见 `dt-sycophancy-data`。口头题里还有「诚实还是仅仅流畅」，答法是在数据上造「流畅但错 / 短而对」的成对样本，评测单独开忠实维度，不并进 Arena。

## 追问

**KL 对哪个锚？**
对外同时报相对 pre-training base model 和相对 SFT 的 KL。只和不断更新的 ref 比，就看不出模型从最初的 base model 偏离了多少。

**怎么知道 post-training 没把 pre-training 的世界知识洗掉？**
用同一套对照：按来源做 held-out，以及 leave-one-source-out，见 `dt-data-mix-quota`、`dt-neg-transfer`。AFM 2025 报告的 multilingual 课程要护住英语能力，用的也是这种前后对照。

**行为套件谁维护？**
版本冻结，新的失败模式只追加，不用当前模型刷新旧标签，见 `dt-contam-hold`。

**多少 prompt 够？**
按危害和产品路径分层，少而硬。报不出分层结果，数字再大也只是平均数。

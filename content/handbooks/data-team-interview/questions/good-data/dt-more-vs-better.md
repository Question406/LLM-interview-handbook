---
id: dt-more-vs-better
section: good-data
order: 3
level: S
title: 堆更多数据，还是把现有的做干净？这题怎么站队？
quick: "先看模型缺什么：知识覆盖不够，就增加没见过的 token；重复和噪声太多，就先过滤、去重。如果模型已有所需能力，只是回答方式不符合要求，再投入精细标注。Chinchilla、FineWeb、DataComp 和 LIMA 分别支持这些不同条件下的选择。"
companies:
  - apple
tags:
  - Apple
  - Data Quality
  - Scaling
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: The Unreasonable Effectiveness of Data
    url: https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/35179.pdf
    type: primary
  - title: Training Compute-Optimal Large Language Models
    url: https://arxiv.org/abs/2203.15556
    type: primary
  - title: Textbooks Are All You Need
    url: https://arxiv.org/abs/2306.11644
    type: primary
  - title: A Chat About MLOps, Data-centric AI
    url: https://www.deeplearning.ai/wp-content/uploads/2021/06/MLOps-From-Model-centric-to-Data-centric-AI.pdf
    type: primary
---

先看哪些能力出了问题，再决定增加数据还是清理现有数据。两种做法各有适用条件。

不能把几篇论文概括成「数据越干净越好」，也不能只说「我们重视质量」，却不解释当前缺的是什么。

## 我会怎么选

- 如果缺知识、多语言或长尾覆盖，就增加许可数据源，并调整各类数据的训练比例，见 `dt-data-mix-quota`。Halevy、Norvig、Pereira 2009：面对语言这种没有简短公式的问题，简单模型和海量、带噪、无标数据往往赢过精致规则，前提是现有数据还没有覆盖足够多的情况。Hoffmann 等（Chinchilla）：固定算力下，模型参数量和训练 token 数需要一起增加；Gopher 那种模型很大、训练 token 不够的情况，属于训练不足。这里的「多」是没见过的 token，不是同一页读十遍。
- 如果同一网页反复出现，或评测题混进了训练集，就先去重，并隔离评测数据，见 `dt-exact-dedup-code`、`dt-contamination`。
- 如果模型不遵守指令格式、不会恰当拒答，或连续调用工具时出错，就用人工标注或经过验证的合成数据补这些行为，见 `dt-lima-vs-scale`、`dt-when-not-synth`。Ng 的 data-centric 讲法（2021 公开课）：很多产品模型卡住是标签不一致、边界没定义，不是差一个点的架构。这个思路更适合监督微调（SFT）和分类任务。从零预训练时，要先保证足够的新数据，并做好去重。
- 如果基座模型根本没有所需能力，精标 1000 条也不足以解决问题，见 False Promise，卡在 `dt-lima-vs-scale`。

Phi / Textbooks Are All You Need：小模型用接近教科书的合成内容和精选代码训练，可以在部分推理任务上表现很好。世界知识和长尾覆盖仍需要网页数据。它证明「更好」能改变小模型的样本效率，没有取消覆盖。

苹果的公开做法同时涉及数量和质量：用公开网页与许可数据扩大覆盖，减弱过于严格的启发式规则，并按语言使用模型过滤。合成数据也需要能被验证。

## 追问

- **再爬 10% 和再滤 10%，先做哪个？** 看最近一次小模型消融。过滤若已经切到 FineWeb 说的「好 token 被扔」区，先停滤。覆盖若明显缺某 locale，先增加该语言或地区的数据源。
- **Bitter Lesson 怎么接？** Sutton 强调通用方法和算力。落实到数据工作，就是让过滤和配比方法能处理更大规模的数据，避免只靠每类手写 50 条规则。规则仍可以负责明确的硬性检查，见 `dt-quality-filter-code`。

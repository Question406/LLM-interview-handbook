---
id: dt-more-vs-better
section: good-data
order: 3
level: S
title: 堆更多数据，还是把现有的做干净？这题怎么站队？
quick: "不站死一边，先看模型缺什么：缺知识覆盖就加没见过的 token；重复和噪声多就先过滤、去重；能力有了、只是回答方式不对，再投精细标注。Chinchilla、FineWeb、DataComp 和 LIMA 分别支持这些不同条件下的选择。"
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

我不站死一边，先看模型哪里出了问题，再决定是加数据还是清理现有的。缺知识和覆盖就加没见过的 token，重复和污染多就先去重、隔离，能力有了但行为不对就做精细标注。「数据越干净越好」和一句「我们重视质量」，都回答不了现在缺的是什么。

举个例子，模型在某种语言上答不出常识题，这是覆盖不够，该加许可数据源、调这类数据的训练比例，见 `dt-data-mix-quota`。加数据这边有两条证据。Halevy、Norvig、Pereira 2009 指出，面对语言这种没有简短公式的问题，简单模型加海量、带噪、无标注的数据，往往胜过精致的规则，前提是现有数据还没覆盖到足够多的情况。Chinchilla（Hoffmann 等）发现固定算力下参数量和训练 token 数要一起涨，Gopher 那种模型很大、token 不够的情况属于训练不足。这里的「多」指没见过的 token，同一页读十遍不算。

如果是同一网页反复出现、评测题混进了训练集，就先清理：先去重，再隔离评测数据，见 `dt-exact-dedup-code`、`dt-contamination`。

如果是模型不遵守指令格式、不会恰当拒答、连续调工具时出错，就补行为数据，用人工标注或验证过的合成数据，见 `dt-when-not-synth`。Ng 2021 年公开课讲的 data-centric 正是这种情况：很多产品模型卡住，原因是标签不一致、边界没定义，架构上的小差距影响不大。基座压根没有所需能力时，精标 1000 条也补不上，False Promise 讲的就是这种情况，见 `dt-lima-vs-scale`。

## 「更好」能走多远

Phi（Textbooks Are All You Need）用接近教科书的合成内容和精选代码训小模型，在部分推理任务上表现很好。「更好」的数据能提高小模型的样本效率，世界知识和长尾覆盖还是要靠网页数据。AFM 2025 报告也是两边一起做：用公开网页和许可数据扩大覆盖，同时减弱过严的启发式规则、按语言做模型过滤。

## 追问

**再爬 10% 和再滤 10%，先做哪个？**
看最近一次小模型消融。过滤已经到了 FineWeb 说的「好 token 被扔掉」那个区间，就先停止加滤；明显缺某种语言的覆盖，就先加那个语言的数据源。

**Bitter Lesson 怎么接？**
Sutton 强调通用方法和算力。落到数据工作上，就是让过滤和配比方法能随数据规模扩展，少靠每类数据手写 50 条规则。规则还是可以负责明确的硬性检查，见 `dt-quality-filter-code`。

**怎么判断模型缺的是哪一种？**
看失败长什么样：答不出知识题是覆盖问题，指标被重复和污染撑高是清理问题，会做但格式、拒答、工具调用出错是行为问题。

**data-centric 适合预训练吗？**
更适合监督微调（SFT）和分类任务。从零预训练时，先保证足够的新数据，并做好去重。

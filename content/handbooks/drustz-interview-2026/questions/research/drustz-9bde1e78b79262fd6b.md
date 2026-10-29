---
id: drustz-9bde1e78b79262fd6b
section: research
order: 170
level: A
title: >-
  ML 轮新考法（2026）：噪声标注/数据质量题族（filter bad annotations、multi-annotator labels）——直接对口
  post-training 数据工作
quick: >-
  supplemental-research-note · ML 轮新考法（2026）：噪声标注/数据质量题族（filter bad
  annotations、multi-annotator labels）——直接对口 post-training 数据工作
companies:
  - openai
tags:
  - DrustZ
  - supplemental-research-note
  - 公司面试 · 补充研究笔记
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://prachub.com/interview-questions/improve-classifier-with-noisy-multi-annotator-labels
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

PracHub 收录三道 OpenAI MLE 变体：(1) 'Filter Bad Human Annotations'（medium）：大规模人工标注训练集中有低质/不一致标注，设计方法过滤；(2) 'Improve Training With Noisy Annotators'（hard）：Pandas DataFrame，含 feature 列和 observed label，提升训练效果；(3) 'Improve classifier with noisy multi-annotator labels'（hard）：二分类文本数据，每条样本有多个标注员的标注，如何建模/聚合/加权提升 classifier。另有 'Mine Novel Images from Unlabeled Data'（从海量无标注图库挖掘新颖图像的 ML 系统）和 'Design a RAG system with evaluation'（含评测设计的 RAG 系统）。这批题是 2026 年 Applied/Research ML 轮相对新的方向，考数据为中心的 ML 工程判断。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://prachub.com/interview-questions/improve-classifier-with-noisy-multi-annotator-labels)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

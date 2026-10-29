---
id: drustz-bdf65cf4208c6ee666
section: research
order: 53
level: A
title: >-
  Coding & Design：Weighted Data Batcher with Checkpointing（research track，MLE/RE
  向）
quick: >-
  supplemental-research-note · Coding & Design：Weighted Data Batcher with
  Checkpointing（research track，MLE/RE 向）
companies:
  - anthropic
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
      https://www.1point3acres.com/interview/problems/company/anthropic/coding-design-data-batcher
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

55 min，research-track 1-of-N coding-and-design 题，难度标 hard。构建 DataBatcher：从 DataRegistry 按权resampling生成 batch，要求确定性的 save/resume——用 offset 参数实现 checkpoint 后精确恢复sampling流。标签：sampling/checkpointing/iterator/Python/MLE。Last asked 2026-05，frequency: Medium。与候选人 mid-training 数据管线背景高度相关。相关：interview thread 1162037 'Onsite Coding and Design Interview for Machine Learning Role'。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.1point3acres.com/interview/problems/company/anthropic/coding-design-data-batcher)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

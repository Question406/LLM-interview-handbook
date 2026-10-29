---
id: drustz-e44c91d9f5d604d7cf
section: research
order: 63
level: A
title: System Design Q1：LLM Inference Batch API（题库最高频 SD 题）
quick: >-
  supplemental-research-note · System Design Q1：LLM Inference Batch API（题库最高频 SD
  题）
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
    url: 'https://www.1point3acres.com/interview/problems/post/7100012'
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

55 min，'Very High' 频率，16+ 关联讨论，标签 llm-inference/batching/kv-cache/gpu。题面（公开部分）：设计一个 HTTP API，对外暴露 LLM 推理的 batch 处理功能。1p3a 题解页结构：The Challenge → 需求澄清 → 规模/资源估算 → API 设计 → 数据存储 → 基础架构 → 组件深挖 → 修复潜在问题（正文需登录）。SD Q3 也是 inference API 主题，有帖专门对比 Q1 vs Q3（interview thread 1158532）；另有 SD Q4 求助帖（thread 1169228、1163059）。变种：'API batch string function combining API requests for LLM APIs'（infra SDE 设计轮，bbs thread 1123616 区域）。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.1point3acres.com/interview/problems/post/7100012)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

---
id: drustz-40dcd2f34bb7dbe2f1
section: research
order: 42
level: A
title: >-
  Find Duplicate Files (LC 609 variant: binary streams, chunked hashing, 2
  parts)
quick: >-
  supplemental-research-note · Find Duplicate Files (LC 609 variant: binary
  streams, chunked hashing, 2 parts)
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
      https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6934db5e5f306485cc5f08b9
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

资料范围：公开预览与可核实要点。

Stages: Screening + Onsite. Variation of LC 609. Find groups of duplicate files with identical BINARY content in a simulated file system rooted at "/". Names/paths don't matter; content only accessible as a binary stream (no direct string access); must be efficient over huge file counts. Part 1 (q ...8ba): recursive traversal, filter candidates by metadata (file size) before reading, group by cryptographic hash. Part 2 (q ...8be): very large files must be read in constrained CHUNKS under strict I/O and memory limits - incremental/running hash updated per chunk, group by size first, defer content reads until a size-bucket has >=2 candidates. Site follow-ups: distributed file system scaling; hash-collision false positives (byte-by-byte confirm); memory for millions of files; partially-similar/modified file detection; parallelization and its synchronization issues; complexity when chunk limit is tiny.

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6934db5e5f306485cc5f08b9)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

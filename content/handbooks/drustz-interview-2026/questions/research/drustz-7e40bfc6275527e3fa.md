---
id: drustz-7e40bfc6275527e3fa
section: research
order: 24
level: A
title: >-
  Cloud Storage System (4-level OA; files, prefix/suffix search, users+capacity,
  compression)
quick: >-
  supplemental-research-note · Cloud Storage System (4-level OA; files,
  prefix/suffix search, users+capacity, compression)
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
      https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/689cf808aee746eb1c84ba37
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

资料范围：公开预览与可核实要点。

Stage: OA. Level 1 (q 689cf810...): addFile(name,size)->bool (fail if exists); copyFile(nameFrom,nameTo)->bool (source must exist and not be a directory, target must not exist); getFileSize(name)->size or -1; treat paths as opaque unique strings. Level 2 (q 689e4cd5...): findFile(prefix,suffix) returning "name(size)" entries where name starts with prefix AND ends with suffix, sorted size DESC then name ASC. Level 3 (q 689e4cd8...): multi-user - addUser(userId,capacity); per-user capacity limits with global file-name uniqueness; addFileBy(user,...) returns remaining capacity; admin has unlimited; updateCapacity(user,newCap) shrinks quota and auto-removes largest files (lexicographic tie-break) until fit, returning count removed. Level 4 (q 689e4cd9...): compressFile/decompressFile - compressed file takes size/2, gets naming-convention suffix (.COMPRESSED), ownership preserved, all capacity constraints validated atomically (compute net space delta first, no temporary overflow). Site follow-ups: hierarchical directories + recursive delete; concurrency/distribution; content dedup; billions of files; rollback for failed compression jobs.

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/689cf808aee746eb1c84ba37)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

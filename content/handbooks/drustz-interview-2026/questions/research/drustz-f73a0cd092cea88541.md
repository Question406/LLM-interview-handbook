---
id: drustz-f73a0cd092cea88541
section: research
order: 35
level: A
title: >-
  Design In-memory Database with Backup (4-level OA; TTL + timestamped versions
  + backup/restore)
quick: >-
  supplemental-research-note · Design In-memory Database with Backup (4-level
  OA; TTL + timestamped versions + backup/restore)
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
      https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/689505de3a1d9e6d6042d519
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

资料范围：公开预览与可核实要点。

Stage: OA. InMemoryDB storing records key->(field->value), all strings. Level 1 (q 689505e7...): setData(key,field,value) upsert; getData->"" if missing; deleteData->bool. Level 2 (q 68961c87...): scanData(key) returns all fields formatted "field(value)" lexicographically sorted; scanDataByPrefix(key,prefix) same but filtered by field prefix. Level 3 (q 689641c8...): timestamped variants setDataAt/getDataAt/scanDataAt with TTL support - field expires after specified duration; timestamps strictly increasing; legacy methods must keep working (backward compat); store per-field chronological version history and binary-search the valid state at query time; lazy expiration. Level 4 (q 689bb206...): backupDatabase(ts) captures only records alive at ts along with their REMAINING TTLs; restoreDatabase(ts, backupTs) restores newest backup <= backupTs and re-bases expirations relative to the restore timestamp (remaining lifespan preserved). Site follow-ups: concurrency; lazy vs background expiry; memory for full version history; non-monotonic timestamps; snapshot vs incremental diff tradeoffs; distributed/eventually-consistent variant.

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/689505de3a1d9e6d6042d519)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

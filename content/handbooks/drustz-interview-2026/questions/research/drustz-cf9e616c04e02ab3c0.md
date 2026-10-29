---
id: drustz-cf9e616c04e02ab3c0
section: research
order: 32
level: A
title: >-
  Design a Task Assignment System (4-level OA; sweep-line quota check at level
  3)
quick: >-
  supplemental-research-note · Design a Task Assignment System (4-level OA;
  sweep-line quota check at level 3)
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
      https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/69efc8e696981f58ae1f6d73
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

资料范围：公开预览与可核实要点。

Stage: OA. TaskManager class. Level 1 (q ...d74): addTask(timestamp,name,priority)->"taskId&lt;n&gt;" sequential from 1 (duplicate name+priority allowed); updateTask(timestamp,taskId,name,priority)->bool; getTask retrieval. Level 2 (q ...d75): searchTasks with case-sensitive substring matching, result limiting (empty filter = wildcard, non-positive limit = empty list); listTasksSorted by priority DESC then creation order ASC where creation order = NUMERIC comparison of taskId suffix (taskId1 < taskId10). Level 3 (q ...d76): user management with per-user quota of simultaneous active tasks; assignTask(user, task, [start,finish)) must validate interval overlaps and that the dynamic quota is never exceeded at any point in the window - requires sweep-line over interval boundary events, processing end events before start events at equal timestamps (half-open intervals). Level 4 (q ...d77): completeTask frees the user's quota; getOverdueAssignments = assignments whose finishTime <= query time and never completed; track completedAt to shorten active interval without deleting. Site follow-ups: interval tree/segment tree instead of linear scan; O(1) completeTask; thread safety; sparse/huge timestamps; DB schema for persistence.

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/69efc8e696981f58ae1f6d73)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

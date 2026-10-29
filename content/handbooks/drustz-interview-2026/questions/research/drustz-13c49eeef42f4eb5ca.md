---
id: drustz-13c49eeef42f4eb5ca
section: research
order: 38
level: A
title: >-
  Design Worker Management System (4-level OA; clock-in/out, top-N, promotions,
  double-pay intervals)
quick: >-
  supplemental-research-note · Design Worker Management System (4-level OA;
  clock-in/out, top-N, promotions, double-pay intervals)
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
      https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/68a4bbdfc11d63d6052ea306
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

资料范围：公开预览与可核实要点。

Stage: OA. Level 1 (q 68a4bbec...): addWorker(workerId,position,compensation)->"true"/"false" if exists; registerWorker(workerId,timestamp) toggles enter/leave (timestamps increasing) -> "registered"/"invalid_request"; get(workerId) -> total office time from COMPLETED sessions only, -1 if unknown worker. Level 2 (q 68a4bbf8...): topNWorkers(n,position) - filter by position, sort by accumulated time DESC then workerId ASC, formatted string output. Level 3 (q 68a4bbfa...): promote(workerId,newPosition,newCompensation,startTimestamp) - promotion is DEFERRED, activates only at the worker's NEXT office check-in after startTimestamp; calcSalary(workerId,startTs,endTs) sums compensation over completed sessions intersected with the query window, using the compensation rate in effect during each session. Level 4 (q 68a4bbfb...): setDoublePay(startTs,endTs) marks time ranges double-paid; overlapping periods must be consolidated (merged) and each minute double-counted at most once in salary calculations - intersect each session with merged double-pay periods and the query window. Site follow-ups: thread safety; non-monotonic timestamps; historical range reports; selection algorithm instead of full sort for top-N; sparse/huge timestamp ranges.

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/68a4bbdfc11d63d6052ea306)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

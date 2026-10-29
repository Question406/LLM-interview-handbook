---
id: drustz-7bea11fa8d299f8f39
section: research
order: 43
level: A
title: >-
  Generate Function Profiling Events (LC 636 variant: stack-trace samples ->
  start/end events, 3 parts)
quick: >-
  supplemental-research-note · Generate Function Profiling Events (LC 636
  variant: stack-trace samples -> start/end events, 3 parts)
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
      https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/69308191cd79766b0b310224
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

资料范围：公开预览与可核实要点。

Stage: Screening. A sampling profiler records entries "&lt;time&gt;:&lt;stackTrace&gt;" where time is strictly increasing int and stackTrace is "main->worker->parse" outermost-to-innermost; stack may be empty ("42:"). Part 1 (q ...225): convert consecutive samples into chronological function start/end events by diffing consecutive stacks - find first mismatch from outermost inward; frames removed after that point ended, frames added started; handle recursion (duplicate names at different depths are independent frames) and empty stacks. Part 2 (q ...228): debounced events - emit start/end only for call paths persisting >= n consecutive samples; reset counter when path vanishes; defer start event until streak reaches n; batch events per timestamp then order by stack depth (outer starts before inner; inner ends before outer). Part 3 (q ...229): suffix-based variant - generate all stack SUFFIXES per sample, track streaks per suffix with original first-seen timestamp, use longest matching suffix chain on transitions to separate newly-valid from expired paths. Site follow-ups: multiple threads; exclusive vs inclusive time; bounded-memory streaming; per-depth debounce thresholds; removing the per-sample sort for strict O(N); trie for suffix matching; out-of-order samples.

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/69308191cd79766b0b310224)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

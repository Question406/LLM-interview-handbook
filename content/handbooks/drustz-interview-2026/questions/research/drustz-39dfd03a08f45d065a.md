---
id: drustz-39dfd03a08f45d065a
section: research
order: 25
level: A
title: CodeSignal OA 题型一：In-memory Database（4 levels，90 分钟）
quick: >-
  supplemental-research-note · CodeSignal OA 题型一：In-memory Database（4 levels，90
  分钟）
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
      https://medium.com/@programhelp/anthropic-interview-questions-2026-oa-technical-interview-breakdown-08d68034a47d
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

Anthropic 标志性 OA（也用于 live coding 轮），90 分钟 4 个递进 level，逐级解锁（当前 level 测试全过才能看下一级），黑盒测试判分。具体拆解：Level 1：基本操作 SET/GET/DELETE；Level 2：加 SCAN、SCAN_BY_PREFIX（要求排序和严格输出格式）；Level 3：加 TTL——SET_AT/GET_AT/DELETE_AT/SCAN_AT（带时间戳的状态管理）；Level 4：backup/restore（数据库快照与恢复）。常见坑：TTL 边界条件应为 ts < start_time + ttl 而不是 <=。Blind 汇总：满分 600（也有 1000 分版本报告），基本要接近满分才能进下一轮，但满分也不保证通过（还看简历匹配）；大多数人做不完 4 级。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://medium.com/@programhelp/anthropic-interview-questions-2026-oa-technical-interview-breakdown-08d68034a47d)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

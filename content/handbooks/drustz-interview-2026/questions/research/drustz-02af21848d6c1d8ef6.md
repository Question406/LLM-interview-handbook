---
id: drustz-02af21848d6c1d8ef6
section: research
order: 19
level: A
title: >-
  Anthropic · Generate Function Profiling Events（LeetCode 636
  变体，栈快照转事件，companyFreq Anthropic=9）
quick: >-
  supplemental-research-note · Anthropic · Generate Function Profiling
  Events（LeetCode 636 变体，栈快照转事件，companyFreq Anthropic=9）
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
      https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/69308191cd79766b0b310224/practice
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

题干（LeetCode 636 Exclusive Time of Functions 变体）：sampling profiler 周期性记录单线程执行状态。每条 samples 形如 '&lt;time&gt;:&lt;stackTrace&gt;'：time 是严格递增整数时间戳；stackTrace 是 '->' 分隔的函数名列表，从最外层到当前执行的最内层（如 'main->worker->parse' 表 main 调 worker 调 parse）；栈可能为空（如 '42:'）。需把周期性栈快照转换成按时间顺序的 start/end 事件。考点：HASH_TABLE + STRING。Follow-up：如何扩展到多并发线程？如何计算每函数 exclusive vs inclusive 时间？样本历史无限增长时如何优化内存？

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/69308191cd79766b0b310224/practice)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

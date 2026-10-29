---
id: drustz-ad0ab53ba5c8a7c9b3
section: research
order: 153
level: A
title: >-
  既有高频实现题 2026 年持续在库（KV store 序列化/时间版本、in-memory DB/SQL、spreadsheet、web
  crawler、Excel 依赖）
quick: >-
  supplemental-research-note · 既有高频实现题 2026 年持续在库（KV store 序列化/时间版本、in-memory
  DB/SQL、spreadsheet、web crawler、Excel 依赖）
companies:
  - openai
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
    url: 'https://www.hellointerview.com/blog/openai-coding-questions'
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

Hello Interview 2025-2026 汇编 + linkjob 2026 题库（与 2026 年帖子交叉验证仍活跃）：(1) KV Store：真实 timestamp 的 time-based KV + 文件持久化 + 自研序列化（禁用内置 JSON；delimiter 冲突用 length-prefix 编码 3:key5:value，Redis protocol 同款）+ 多线程锁策略（全局锁 vs per-key 锁 vs 乐观锁）+ future timestamp 查询。(2) In-Memory DB：select(table, where=None, order_by=None)，AND 过滤、多列排序、向后兼容 API。(3) Excel/Spreadsheet：getCell/setCell 支持公式依赖，循环依赖检测，Part2 优化 setCell 使 getCell O(1)（拓扑传播）。(4) 多线程 web crawler：worker pool、visited 去重线程安全、失败处理、限速。这些与 2026 年 6 月 thread-1181536 的 versioned KV 报告互证。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.hellointerview.com/blog/openai-coding-questions)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

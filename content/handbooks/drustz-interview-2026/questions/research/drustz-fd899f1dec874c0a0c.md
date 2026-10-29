---
id: drustz-fd899f1dec874c0a0c
section: research
order: 27
level: A
title: Coding Q1：Concurrent Web Crawler（题库最高频经典题，完整题面）
quick: supplemental-research-note · Coding Q1：Concurrent Web Crawler（题库最高频经典题，完整题面）
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
      https://www.1point3acres.com/interview/problems/company/anthropic/coding-q1-web-crawler
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

55 min。实现 crawl(startUrl, htmlParser) -> list[str]：给 htmlParser.getUrls(url) helper（LeetCode 1242 风格），BFS 抓取同 hostname 的所有 URL 并去重，在 CodeSignal 里跑通。Follow-up 链：(1) 用 ThreadPoolExecutor 并发化——线程安全的 visited set + work queue，或 asyncio 版本；(2) 论证 threads vs processes vs asyncio 的选择（IO-bound）；(3) 口头分布式扩展：多机 sharding、跨机去重（Redis/中心队列）、per-host 限流、故障恢复；(4) asyncio.gather vs as_completed vs semaphore 限流池的语义区别。注意：2025 年中起环境从 Replit 换成 CodeSignal，第一次 run 常要修 import；先澄清 URL fragment/规范化范围；不要过度设计。Last asked 2026-05-03，roles: SWE/MLE/Infra。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.1point3acres.com/interview/problems/company/anthropic/coding-q1-web-crawler)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

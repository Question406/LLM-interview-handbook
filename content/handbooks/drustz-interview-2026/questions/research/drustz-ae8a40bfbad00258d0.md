---
id: drustz-ae8a40bfbad00258d0
section: research
order: 31
level: A
title: Concurrent Web Crawler (LC 1242 variant with URL sanitization)
quick: >-
  supplemental-research-note · Concurrent Web Crawler (LC 1242 variant with URL
  sanitization)
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
      https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/692f5158cd79766b0b310122
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

资料范围：公开题面或公开解法。

Stage: phone screen. Variation of LeetCode 1242 Web Crawler Multithreaded. Given startUrl and htmlParser.getUrls(url) (each call has simulated ~10-15ms network latency), return all unique URLs with the EXACT same hostname as startUrl. Twists vs LC1242: must strip URL fragment (everything from '#') BEFORE hostname comparison and dedup ("[来源链接](http://example.com/page#s1") == "[来源链接](http://example.com/page")); hostname = substring between "://" and next '/'; graph may contain cycles; must use concurrency because of per-call latency (<=1000 urls, <=1000 edges, each getUrls <=15ms). 3 worked examples captured. Site follow-ups: rate limiting/crawl delay; BFS vs DFS priority under concurrency; scaling to multiple worker nodes (distributed crawler). Acceptance 56.4%. This matches the widely-reported Anthropic screen 'async web crawler' question.

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/692f5158cd79766b0b310122)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

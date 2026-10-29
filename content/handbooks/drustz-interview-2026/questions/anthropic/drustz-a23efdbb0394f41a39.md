---
id: drustz-a23efdbb0394f41a39
section: anthropic
order: 61
level: A
title: 'Single-thread Web Crawler, then Multi-threaded Crawler'
quick: >-
  original-structured-preparation-guide · Single-thread Web Crawler, then
  Multi-threaded Crawler
companies:
  - anthropic
tags:
  - DrustZ
  - original-structured-preparation-guide
  - Anthropic · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/24ef32e6-b554-41ca-977b-307982b4d871
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 从单线程扩展到多线程 Web Crawler

## 题目

从一个 URL 开始抓取 HTML、解析链接，只继续访问同一 host 的页面。先完成单线程 `fetch + parse_links`，再扩展为固定数量 worker 的并发版本。

## 实现

单线程使用 queue + visited；发现链接时完成规范化、同域判断和去重，再入队。

并发版使用线程安全队列。发现新 URL 时在同一临界区内 check-and-add；worker 处理完无论成功或异常都调用 task-done。主线程等待 unfinished count 归零后发送停止信号，而不是看到临时空队列就退出。

## 复杂度与边界

总工作量 `O(V+E)`、空间 `O(V)`，最多 `T` 个并发抓取。需定义网络失败重试、重定向、相对 URL、canonicalization、超时、错误任务的计数和关闭时 pending 工作。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/24ef32e6-b554-41ca-977b-307982b4d871)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

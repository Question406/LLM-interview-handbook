---
id: drustz-2b8a1a0ab1045f58f9
section: anthropic
order: 91
level: A
title: Web Crawler with Multithreading
quick: original-structured-preparation-guide · Web Crawler with Multithreading
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
      https://www.1point3acres.com/interview/problems/eab3ec23-cfcc-4009-bb0e-abed459f8234
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 用动态 Futures 实现多线程 Web Crawler

## 接口与目标

实现 `crawl(start_url, parser, max_workers)`，并行调用阻塞式 `parser.get_urls`，输出同 host 可达 URL。与 worker-queue 写法不同，本版重点是由主线程维护一个**会动态增长**的 future 集合。

## 调度算法

起点加入 `seen` 并提交。循环等待任一 future 完成，取回它发现的链接；主线程解析 hostname、去重并提交新 future。不要直接对最初的 `as_completed(futures)` 迭代，因为之后添加的任务未必被该迭代器纳入；可用 `wait(pending, return_when=FIRST_COMPLETED)`，每轮从 `pending` 删除 `done`、再加入新任务。这样 `seen` 只归协调线程所有，避免锁竞争。

当且仅当 `pending` 为空时全局终止。每个异常 future 仍要消费 `result()` 并移除；根据约定记录、重试有限次或整体失败。爬取是 I/O-bound，线程通常比进程更合适；固定池还提供背压。总工作量 `O(V+E)`、空间 `O(V)`，峰值并发不超过 `T`。边界包括重复链接同时返回、任务异常、超时、过大的待提交集合、executor 关闭、`T=1`，以及禁止 worker 再阻塞等待同一小线程池中的子任务所造成的死锁。

为避免一次高出度页面瞬间创建数十万 future，可以把待提交 URL 先放有界 frontier，只在 `pending` 少于阈值时补充。这样线程数控制“正在运行”，frontier 上限控制内存，两者职责不同。性能比较应使用相同假 parser 延迟测串行与并发墙钟时间，并确认调用总数未因竞态增加；不能仅凭线程数宣称加速。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/eab3ec23-cfcc-4009-bb0e-abed459f8234)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

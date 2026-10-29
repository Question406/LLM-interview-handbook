---
id: drustz-ccd6196eed1747820c
section: anthropic
order: 63
level: A
title: 'Web Crawler (single-threaded first, then concurrent)'
quick: >-
  original-structured-preparation-guide · Web Crawler (single-threaded first,
  then concurrent)
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
      https://www.1point3acres.com/interview/problems/3823a702-699e-4bf5-bd78-8ce518c640ad
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Web Crawler：先写同步版，再改成并发版

> 证据能确认题型与两阶段要求；以下是可直接练习的原创题面和解法，不冒充会员页原文。

## 接口与例子

实现 `crawl(start_url, html_parser)`；`html_parser.get_urls(url)` 返回该页链接。只访问与起点 **hostname 相同**且可达的页面。例如 `a.com → {a.com/x, b.com/y}`、`a.com/x → {a.com}`，结果是 `{a.com, a.com/x}`。

## 两阶段算法

同步版用 `deque` 做 BFS：起点先放入 `seen`；每次取页、解析链接，完成同域检查后，在**入队时**去重。并发版保留同一图遍历逻辑，把抓取提交给固定大小的 `ThreadPoolExecutor`。一种容易证明正确的写法是让协调线程独占 `seen`：worker 只返回链接，协调线程处理完成的 future、认领新 URL 并继续提交，因此无需让多个 worker 同时修改集合。

终止不能用“某一刻队列为空”；应以动态 `pending futures` 集合为空为准。每个 future 无论成功或异常都必须移除，单页失败可记录后继续。总工作量 `O(V+E)`，集合与待处理任务占 `O(V)`；并发只缩短 I/O 等待时间。覆盖环、自链接、重复边、跨域链接、空页面、抓取异常和并发数为 1。

改造时先保留同步版测试作为行为基线，再只替换“取得下一页”的调度层；这能快速判断错误来自遍历语义还是并发收尾。若输出顺序不保证，测试应比较集合；若产品要求稳定顺序，则要给每次发现分配序号后统一整理，不能依赖 future 完成顺序。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/3823a702-699e-4bf5-bd78-8ce518c640ad)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

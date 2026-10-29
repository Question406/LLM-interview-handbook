---
id: drustz-c4dfc755b3afd9f4a2
section: anthropic
order: 81
level: A
title: Web Crawler Challenge
quick: original-structured-preparation-guide · Web Crawler Challenge
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
      https://www.1point3acres.com/interview/problems/cdf0facf-7e01-47e4-9261-15bb1346366e
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Web Crawler Challenge：先把契约和正确性写扎实

> 当前公开标题没有暴露独有 follow-up；以下按本地同题族证据整理基础 challenge，不把并发或 fragment 强塞成必选要求。

## 可练习接口

给定 `crawl(start_url, html_parser) -> list[str]`，其中 `get_urls(url)` 提供页面链接。返回从起点可达、hostname 与起点一致的全部 URL，顺序不要求。例：`a.com → a.com/x,b.com/y`，`a.com/x → a.com`，结果只有前两个 `a.com` 页面。

## 解法与工程组织

把逻辑拆为 `same_host`、`claim` 和遍历循环。起点立即认领；每次取出 URL 调解析器，过滤跨域链接，并在发现时去重入队。BFS 与 DFS 都正确，BFS 更便于观察测试过程。解析失败的策略要先说明：可以 fail-fast，也可以记录失败页继续，但不能悄悄把失败页反复入队。

队列耗尽即同步版终止；若面试官追加并发，再改用 outstanding-task 计数，不能沿用瞬时空队列判断。时间 `O(V+E)`、空间 `O(V)`。测试空出边、菱形重复路径、自环、跨域、相似 host（`evil-a.com` 不能用字符串前缀混入）、异常和深链。相对 URL、fragment、重定向是否规范化都应先澄清，而不是自行假设。

一个最小可复现测试可用字典模拟三页和一次故障，并记录每个 URL 被调用的次数；除明确重试外，每个规范 URL 的次数必须恰为一。这样既验证返回集合，也验证不会只是在结果里去重、实际却重复发请求。若 parser 会修改内部状态，测试还应说明它在基础同步阶段无需线程安全。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/cdf0facf-7e01-47e4-9261-15bb1346366e)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

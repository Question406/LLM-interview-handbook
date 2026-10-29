---
id: drustz-f825c85abede8f4c9a
section: plans
order: 13
level: A
title: 顶尖AI公司面经全解析：OpenAI · xAI · Anthropic · 3.2 OA (Online Assessment) 题目
quick: 作者文档章节 · 顶尖AI公司面经全解析：OpenAI · xAI · Anthropic · 3.2 OA (Online Assessment) 题目
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 作者复习计划与报告
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/00_reports_and_plans/final_report_v2.md
    type: primary
---
## 3.2 OA (Online Assessment) 题目

### 3.2.1 Recipe Manager — 高频OA

90分钟，4个Level，时间非常紧张。

> 来源: [来源链接](https://www.1point3acres.com/bbs/thread-1173693-1-1.html)

**Level 1**：实现 `create_recipe`（有user_id, name, timestamp, 食材, steps）和 `rate_recipe`。注意区分大小写，都用lower。

**Level 2**：实现排序 for chef based on ranking。注意corner case。

**Level 3**：实现order edit，track order, meal, add等。

**Level 4**：实现cancel order + track record。

### 3.2.2 Task Management System — 高频OA

4问，整体不难。第三问最后一个part需要熟读requirement，第四问要用bisect。

### 3.2.3 In-Memory DB — OA

题目是in memory db，但有改动版本：没有compare set和compare delete，第四问是implement `backup()` 和 `restore()`。

### 3.2.4 其他OA题型

- **Toy Simulation of an App**：只要求TypeScript或Python，写app logic和refactoring。
- **Performance Engineer OA**：2小时take-home，optimize一个mocked system的core kernel function。之前可以用LLM的版本已被开源：`github.com/anthropics/original_performance_takehome`。

---

来源：[DrustZ / Mingrui Zhang · online_resource/00_reports_and_plans/final_report_v2.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/00_reports_and_plans/final_report_v2.md)。作者整理资料；许可和第三方来源范围见阅读指南。

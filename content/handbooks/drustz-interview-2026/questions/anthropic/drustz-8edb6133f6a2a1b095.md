---
id: drustz-8edb6133f6a2a1b095
section: anthropic
order: 56
level: A
title: Implement a UI From a Figma Mock in React + TypeScript
quick: >-
  locally-saved-public-oj-summary · Implement a UI From a Figma Mock in React +
  TypeScript
companies:
  - anthropic
tags:
  - DrustZ
  - locally-saved-public-oj-summary
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
      https://www.1point3acres.com/interview/problems/1a1fb907-7914-40b7-aa33-f5825437aa91
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## 公开题面摘要

在限定时间内，根据面试官提供的 Figma 链接或截图，用 React 与 TypeScript 实现一个可运行界面。重点不是绝对像素级复刻，而是正确还原版式、间距和视觉层级，并把页面拆成合理、可复用的组件。

需要为核心数据和组件 props 定义清晰类型，避免使用 `any`；根据 mock 实现主要交互，例如选择状态、tabs、搜索过滤、表单输入、按钮和 modal，并使用 React hooks 管理状态。还要覆盖空列表、无搜索结果和非法输入等基本边界。

默认假设使用本地 mock data，除非面试官另行要求 API；默认不依赖大型 UI 库。验收时应检查初始布局、选择状态、搜索与清空、空状态，以及主要 modal/操作是否能正确开关。

### 来源与内容类型

- Content kind: `locally-saved-public-oj-summary`
- [原始来源](https://www.1point3acres.com/interview/problems/1a1fb907-7914-40b7-aa33-f5825437aa91)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

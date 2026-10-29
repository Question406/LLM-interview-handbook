---
id: drustz-3b4195c65fba89db35
section: research
order: 21
level: A
title: >-
  Anthropic 店面/onsite 编码真题：Repair Bootloader Program（=Advent of Code 2020 Day 8
  变体）
quick: >-
  supplemental-research-note · Anthropic 店面/onsite 编码真题：Repair Bootloader
  Program（=Advent of Code 2020 Day 8 变体）
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
      https://www.reddit.com/r/Hack2Hire/comments/1umm6xj/anthropic_phone_screen_experience/
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

2026 年 6-7 月三个独立报告（店面 + Staff/Sr Staff onsite coding 轮都出过）。题目：给一个指令文件（自造小语言），三种操作——plus（累加器加值）、next（顺序下一行）、jump（相对偏移跳转）。从第一行开始执行直到跑出文件末尾或死循环。要求：检测何时陷入无限循环（重复访问同一行）、找出导致循环的行——bug 是某一行的 jump 和 next 被互换，修复（换回来）使程序正常终止，并返回进入循环前的累加器值/终止时累加器值。onsite 版约 50 分钟做完含 debug。考生评价：理解题意花 10 分钟，实现本身不难；考的是仔细模拟、循环检测、debug、确保修复后程序终止。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.reddit.com/r/Hack2Hire/comments/1umm6xj/anthropic_phone_screen_experience/)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

---
id: drustz-6cebeb18ee6a7ce539
section: research
order: 20
level: A
title: Anthropic · Repair Bootloader Program（指令模拟找首个重复执行，companyFreq Anthropic=8）
quick: >-
  supplemental-research-note · Anthropic · Repair Bootloader
  Program（指令模拟找首个重复执行，companyFreq Anthropic=8）
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
      https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6a373b2b6849fecc81442861/practice
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

题干：bootloader 把程序存为文本指令数组，需找到执行首次开始重复的位置。给定 instructions，每条形如 '&lt;operation&gt; &lt;value&gt;'，operation 为 'plus'/'next'/'jump'：'plus x' 给全局累加器加 x 然后移到下一条；'next x' 累加器不变移到下一条（x 保留在格式中但本题忽略）；'jump x' 累加器不变，跳到当前索引+x 的指令。从索引0开始执行，返回首次重复执行的指令索引，若程序正常终止返回 -1。考点：SIMULATION / 函数图环检测。Follow-up：若指令集含条件跳转如何改？能否在仍高效检测环的同时降低空间复杂度？跳转越界怎么办？此题如何映射到函数图的环检测（Floyd）？

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.hack2hire.com/question-bank/companies/anthropic/coding-questions/6a373b2b6849fecc81442861/practice)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

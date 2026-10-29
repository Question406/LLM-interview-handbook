---
id: drustz-26ecccf4a1a28f586a
section: research
order: 30
level: A
title: Coding Q6：Tokenizer（2026 店面/onsite 高频）
quick: supplemental-research-note · Coding Q6：Tokenizer（2026 店面/onsite 高频）
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
    url: 'https://www.1point3acres.com/interview/thread/1169657'
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

实现 tokenizer，核心是贪心最长匹配（longest match）分词：给 vocab，对输入串反复取最长可匹配 token。考察点：bug finding（给带 bug 的实现让你修）、longest match 正确性、实现细节。一位候选人先写朴素 for 循环做最长匹配，再升级 trie 结构。相关帖：interview thread 1169657 'Q6 Tokenizer Technical Phone Screen'（bug finding + longest match + implementation）、1156951 'SWE Onsite Q6 Coding Question Details'、1160525 'What is the Coding Q6'、1143701 'Tech Phone Screen Prompts for Q2 and Q6 (MLE)'。

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.1point3acres.com/interview/thread/1169657)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

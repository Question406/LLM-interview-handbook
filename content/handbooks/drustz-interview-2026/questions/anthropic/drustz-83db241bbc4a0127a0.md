---
id: drustz-83db241bbc4a0127a0
section: anthropic
order: 69
level: A
title: 'VO Q2 (Unclear: File Deduplication or LRU Cache)'
quick: >-
  original-structured-preparation-guide · VO Q2 (Unclear: File Deduplication or
  LRU Cache)
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
      https://www.1point3acres.com/interview/problems/f909b9c2-da1d-4093-b73b-55ccac13df3c
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# VO Q2：File Deduplication 或 LRU Cache（尚未识别）

## 当前证据

公开标题本身写明这道 VO Q2 可能是 File Deduplication，也可能是 LRU Cache，没有足够信息确定是哪一个。旧页面直接挂 LRU + persistence 正文，会在真实题是文件去重时造成完整错配，因此已经移除。

## 两个候选方向

- **LRU Cache**：HashMap + 双向链表，`get/put O(1)`；
- **File Deduplication**：先按 size 分组，再对候选文件分块 hash，最后逐字节确认，避免 hash collision；大文件不能一次读入内存。

这两个方向的 API、边界和 follow-up 完全不同，不能合并成一个“标准答案”。需要从原帖获得函数签名、关键词或样例后再确定。

## 使用建议

当前页保留官方 UUID 和两个公开练习链接供准备，但明确标为未识别，不把任一候选当作原题。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/f909b9c2-da1d-4093-b73b-55ccac13df3c)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

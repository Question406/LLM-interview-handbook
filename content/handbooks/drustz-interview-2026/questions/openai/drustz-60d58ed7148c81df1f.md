---
id: drustz-60d58ed7148c81df1f
section: openai
order: 33
level: A
title: Time Based KV Store
quick: locally-saved-research-summary · Time Based KV Store
companies:
  - openai
tags:
  - DrustZ
  - locally-saved-research-summary
  - OpenAI · 题库与复习指南
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
      https://www.1point3acres.com/interview/problems/company/openai/time-based-kv-store
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## Versioned KV store + follower/followee 社交图查询（social network 题 2026-06 新组合）

thread-1181536（2026-06-28 phone screen）原文：'Coding: Versioned KV store. Maintain a friend follower/followee graph. Query a (a,b) to see if a follows b. Followup: With friends(follower) list and top K recommendations'。即一场电面把 versioned KV store 和 social network 两个已知高频题合并：先实现带版本/时间戳的 KV 存储，再在其上维护关注图，支持 a 是否 follow b 的查询，follow-up 是基于好友列表做 top-K 好友推荐。

### 解题与准备提示

KV: dict[key] -> sorted list of (version/timestamp, value)，get(key, t) 二分（LC981 模式）；图: adjacency set 存 following；top-K 推荐: 好友的好友计数（排除已关注和自己），heapq.nlargest 按共同好友数取 K——注意讲清楚打分函数可插拔（我的推断）。

### 来源与内容类型

- Content kind: `locally-saved-research-summary`
- [原始来源](https://www.1point3acres.com/interview/problems/company/openai/time-based-kv-store)
- [相关来源](https://www.1point3acres.com/bbs/thread-1181536-1-1.html)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

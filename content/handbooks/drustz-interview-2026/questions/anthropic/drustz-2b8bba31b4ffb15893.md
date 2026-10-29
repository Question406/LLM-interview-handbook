---
id: drustz-2b8bba31b4ffb15893
section: anthropic
order: 23
level: A
title: OA Fellows DNS Resolver
quick: locally-saved-research-summary · OA Fellows DNS Resolver
companies:
  - anthropic
tags:
  - DrustZ
  - locally-saved-research-summary
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
      https://www.1point3acres.com/interview/problems/company/anthropic/oa-fellows-dns-resolver
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## Fellows/Safety Fellowship OA（2026）：DNS resolver + Python debugging；prompts→GPT servers 哈希映射

(1) Anthropic Fellows（ML intern，2026 July cohort）两轮 CodeSignal OA：第一轮 DNS resolver 实现，第二轮 Python debugging（interview thread 1177056，2026-05-16）。(2) Safety Fellowship CodeSignal OA：'mapping prompts to GPT servers using a hash table'——用哈希表把 prompt 路由到服务器（interview thread 1163421，详情在登录墙内）。(3) AI Safety Fellow 5 小时 in-home assessment：给定 codebase，在小模型上做 PyTorch 实验并回答 research questions（interview thread 1165094）。

### 解题与准备提示

DNS resolver（我的推断）：实现递归/迭代解析+缓存 TTL+CNAME 链；prompts→servers 是 consistent hashing 风格路由题。5h 评估重点是实验设计和写作，不是代码量。

### 来源与内容类型

- Content kind: `locally-saved-research-summary`
- [原始来源](https://www.1point3acres.com/interview/problems/company/anthropic/oa-fellows-dns-resolver)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

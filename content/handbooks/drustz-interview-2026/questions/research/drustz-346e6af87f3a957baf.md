---
id: drustz-346e6af87f3a957baf
section: research
order: 135
level: A
title: OpenAI · Snapshot Social Graph（版本化关注关系，companyFreq OpenAI=9）
quick: >-
  supplemental-research-note · OpenAI · Snapshot Social
  Graph（版本化关注关系，companyFreq OpenAI=9）
companies:
  - openai
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
      https://www.hack2hire.com/question-bank/companies/openai/coding-questions/69b070d6a4e93c007df3fc35/practice
    type: secondary
---
> DrustZ 整理的补充研究笔记。公司与轮次信息沿用作者的来源记录。

题干：设计追踪用户关注关系并通过 snapshot 维护历史状态的社交网络。支持随时间 follow/unfollow，并能查询某个 follow 关系在任一历史 snapshot 时是否存在。实现 SocialNetwork 类：SocialNetwork() 初始化空网络；follow(followerId, followeeId) 在当前工作态记录关注；unfollow(followerId, followeeId) 记录取消关注；（还含）takeSnapshot 递增 snapshot ID；query 查询某 snapshot 时某关系是否 active。考点：GRAPH + 版本化 + 二分。Follow-up：边数随 snapshot 指数增长时如何省空间？delta 方案 vs 每 snapshot 存全图拷贝的权衡？如何支持并发更新或 rollback？query 能否做到 O(1) 而非 O(log S)？

### 来源与内容类型

- Content kind: `supplemental-research-note`
- [原始来源](https://www.hack2hire.com/question-bank/companies/openai/coding-questions/69b070d6a4e93c007df3fc35/practice)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/supplemental.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/supplemental.json)。作者整理资料；许可和第三方来源范围见阅读指南。

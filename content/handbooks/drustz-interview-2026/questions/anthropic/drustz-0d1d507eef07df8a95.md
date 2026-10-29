---
id: drustz-0d1d507eef07df8a95
section: anthropic
order: 53
level: A
title: In-Memory Database with Backup and Restore
quick: >-
  original-structured-preparation-guide · In-Memory Database with Backup and
  Restore
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
      https://www.1point3acres.com/interview/problems/1091f5c2-4b7c-4b13-9db8-7caada56c79f
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# In-Memory Database：Backup 与 Restore

> 旧正文是 TTL/time-travel OA，没有 backup/restore API。真实数据模型未公开，下面从一致性全量快照开始。

## Backup

在读锁或 MVCC snapshot 下取得一致视图，写出 schema version、数据库版本、数据与必要元数据。使用流式 serialization，附 header、record length 和 checksum；先写临时目标，完整 `fsync` 后原子 rename 发布，不能让半成品冒充有效备份。

## Restore

恢复到 staging 实例：先验证格式版本、checksum、主键和索引不变量，全部成功后再原子替换在线实例。失败时保留原数据库。TTL 需要规定保存绝对 expires_at 还是剩余时长；通常保存绝对时间更能保持语义。

大数据量 follow-up 可采用 copy-on-write、一致性 checkpoint + 增量 log 或分块快照，缩短写锁时间。

## 复杂度与边界

全量备份、恢复为 `O(N)` 时间与 `O(N)` 持久存储；流式实现工作内存 `O(chunk)`。覆盖空库、损坏/截断、版本不兼容、备份期间写入、索引重建、重复 restore 和发布阶段崩溃。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/1091f5c2-4b7c-4b13-9db8-7caada56c79f)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

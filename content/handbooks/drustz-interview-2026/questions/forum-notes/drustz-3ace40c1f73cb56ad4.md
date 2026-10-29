---
id: drustz-3ace40c1f73cb56ad4
section: forum-notes
order: 260
level: A
title: OpenAI 面试题库 · 一亩三分地会员版（完整） · Shard Rebalancing
quick: 作者文档章节 · OpenAI 面试题库 · 一亩三分地会员版（完整） · Shard Rebalancing
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - 面经整理与回答建议
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md
    type: primary
---
## Shard Rebalancing

### Shard Rebalancing

You are implementing a shard management system for a distributed key-value store.

Each shard is represented as a string in the format `"id:start:end"`, where the shard covers the inclusive key range `[start, end]`.

Given an integer `limit` and an array `shards`, rebalance the shards so that:

- No key is covered by more than `limit` shards.
- Processing happens after sorting the original shards by `start` ascending, then `end` ascending.
- If a shard would cover a key that already has `limit` active shards, shift that shard's `start` to the earliest key where coverage becomes strictly less than `limit`.
- If shifting makes `start > end`, delete that shard.
- After all shifts and deletions, coverage must stay continuous from the original minimum `start` to the original maximum `end`. If a gap appears, extend the most recently kept shard to fill it.
Return the rebalanced shards in the same `"id:start:end"` format. You may return them in any order.

Identifiers are distinct and do not contain colons.

---

来源：[DrustZ / Mingrui Zhang · online_resource/1p3a-openai.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/online_resource/1p3a-openai.md)。作者整理资料；许可和第三方来源范围见阅读指南。

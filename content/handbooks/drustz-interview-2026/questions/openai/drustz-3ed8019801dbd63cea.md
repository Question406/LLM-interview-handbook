---
id: drustz-3ed8019801dbd63cea
section: openai
order: 136
level: A
title: KV Store Implementation
quick: original-structured-preparation-guide · KV Store Implementation
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
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
      https://www.1point3acres.com/interview/problems/811ba67f-faca-4f75-a670-7ced29702f54
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# KV Store Implementation：版本化查询与并发扩展

> 内容定位：当前标题过于宽泛；本地 2026 面经明确另有 versioned KV 变体。以下把它整理成高频进阶练习，但不声称这些时间语义就是该会员 UUID 的 canonical 题面。

## 练习版接口

实现 `put(key, value, timestamp)`、`delete(key, timestamp)`、`get(key, timestamp)`，其中 get 返回不晚于查询时刻的最新有效值；再提供 `snapshot()`/`load()` 保存整个版本历史。

```text
put("model", "v1", 10)
put("model", "v3", 30)
put("model", "v2", 20)
get("model", 25)       => "v2"
delete("model", 40)
get("model", 50)       => None
```



必须先确认 timestamp 是否保证递增、同 key 同 timestamp 是覆盖还是拒绝，以及查询未来时刻是否允许。

## 数据结构与并发

为每个 key 保存按 `(timestamp, sequence)` 排序的版本数组，值可以是普通字符串或 tombstone。递增写时直接 append；乱序写用二分找到插入点。同 timestamp 若采用 last-write-wins，就用全局单调 sequence 打破平局。get 对时间数组执行 `upper_bound(query_time)`，向左一项即答案，若为 tombstone 则返回缺失。

并发实现可用顶层 map 锁保护 key 的创建，再用 per-key 读写锁保护版本数组；多 key snapshot 需要全局 generation/barrier，不能逐 key 复制而得到跨时刻混合视图。持久化按 key、版本数和每条 `(timestamp, sequence, tombstone, length-prefixed value)` 编码，并保存 next-sequence。

## 复杂度与边界

某 key 有 `V` 个版本时，get 为 `O(log V)`；递增 put 摊还 `O(1)`，乱序插入为 `O(V)`，可改平衡树得到 `O(log V)`；全量快照为 `O(B)`。边界包括同 timestamp 多写、删除后重建、空字符串与 tombstone 区分、极小/极大时间、并发 get/put、snapshot 中途失败、load 后 sequence 冲突，以及历史无限增长时的 retention/compaction 策略。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/811ba67f-faca-4f75-a670-7ced29702f54)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

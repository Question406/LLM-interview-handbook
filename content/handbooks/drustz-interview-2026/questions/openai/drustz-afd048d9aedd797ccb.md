---
id: drustz-afd048d9aedd797ccb
section: openai
order: 89
level: A
title: Implement an in-memory TTL cache (optionally LRU)
quick: >-
  original-structured-preparation-guide · Implement an in-memory TTL cache
  (optionally LRU)
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
      https://www.1point3acres.com/interview/problems/478c798b-df30-44a1-8f7e-2dfba6cd2710
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# In-Memory TTL Cache（可选 LRU）

> 旧正文混入了 versioned KV 和社交图，不是 TTL cache 的对应答案。下面给出独立的 TTL cache 设计。

## API 与语义

```text
set(key, value, ttl_ms, now_ms)
get(key, now_ms) -> value or not-found
delete(key)
```



每条记录保存 `(value, expires_at, version)`。hash map 提供按 key 查询；最小堆保存 `(expires_at, version, key)`，用于按时间清理。更新同一 key 时把 version 加一，堆中的旧节点无需立即删除，弹出时若版本不一致就丢弃。

```python
def get(key, now):
    entry = data.get(key)
    if entry is None:
        return None
    if entry.expires_at <= now:
        del data[key]
        return None
    return entry.value
```



每次公开操作前可以调用 `purge(now)`：不断弹出堆顶已经过期的节点，并且只删除仍与 map 中 version 相同的记录。

## 加 LRU

如果还要求容量上限和 LRU，另用双向链表或 `OrderedDict` 维护最近访问顺序。淘汰前先清过期项；没有过期项时再删除最久未使用的有效项。TTL 和 LRU 是两个独立维度，不要把过期时间当成访问顺序。

## 复杂度

hash 查询平均 `O(1)`；带 heap 的 set 和过期清理摊销 `O(log n)`；LRU 顺序更新为 `O(1)`。lazy heap 可能暂时保存旧版本节点，空间与更新次数有关，可在比例过高时重建。

## 边界

`ttl <= 0`、窗口端点采用 `expires_at <= now`、时钟回拨、并发 get/set、更新后的旧 heap 节点、后台清理线程退出，以及 value 本身为 `None`。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/478c798b-df30-44a1-8f7e-2dfba6cd2710)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

---
id: drustz-fa413a0bdc3baaa1df
section: anthropic
order: 83
level: A
title: Implement a Function 'get_when' in an In-Memory Database
quick: >-
  original-structured-preparation-guide · Implement a Function 'get_when' in an
  In-Memory Database
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
      https://www.1point3acres.com/interview/problems/b6750541-51ba-4dfa-93b2-568a0c81515b
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Event Store 的 `get_when`：找最早满足条件的事件

> 证据边界：当前 UUID 的公开 description 明确了事件、predicate、返回值和规模；下文不借用同名 TTL 历史查询，也不声称复制会员内容。

## 完整题面与接口

实现一个顺序内存事件库。`insert(event)` 接收 `{"timestamp": int, "data": any}`，时间戳唯一且按严格递增顺序插入；`get_when(predicate) -> int` 返回第一个令 `predicate(event)` 为真的事件时间戳，若不存在返回 `-1`，最多保存 `10^5` 条事件。

例如插入 `(1,"A")、(2,"B")、(3,"B")`，调用 `get_when(lambda e: e.data == "B")` 返回 2；查询 `data == "C"` 返回 -1。本题问的是**最早满足任意谓词的事件**，不是另一个数据库题里的“字段在过去何时取某值”。

## 解法与为何不能二分

用数组按插入顺序保存事件；插入时检查新 timestamp 大于末项，然后 append。查询从头扫描，第一次命中立即返回。谓词可以读取任意 data，真假序列不保证单调，因此仅凭时间有序不能二分；只有题目额外给出可索引字段或单调条件时，才可维护 `field_value -> sorted timestamps` 并二分。

插入均摊 `O(1)`，任意谓词查询最坏 `O(n)`，空间 `O(n)`；字段索引是可选扩展而非基础答案。测试空库、首项/末项命中、多个命中取最早、无命中、乱序或重复 timestamp、predicate 抛异常、插入后外部修改 event 的别名问题；若需隔离，应复制事件或定义其不可变。

接口还应约定 predicate 是纯函数：若它依赖外部可变状态，同一查询可能得到不同答案，数据库无法缓存。若大量查询共享固定条件，可额外提供结构化查询如 `get_when(field,value)` 并建倒排索引；这属于新合同，不能偷偷用来替代公开要求的任意函数。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/b6750541-51ba-4dfa-93b2-568a0c81515b)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

---
id: drustz-55c1eacebc411e5802
section: openai
order: 158
level: A
title: Design a simple database class with insert and query methods
quick: >-
  original-structured-preparation-guide · Design a simple database class with
  insert and query methods
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
      https://www.1point3acres.com/interview/problems/862e9246-1a5e-49f7-b30e-c9fe39aef1b5
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Simple Database Class：insert 与 query

## 证据边界

当前标题只要求一个带 `insert`、`query` 的简单数据库类；原始面经确认会按 name、age、id 等字段过滤。建表 schema、多列排序和动态类型推断属于相关高级版本，并非这个标题已确认的要求。下面使用 schema-less 行存储，给出完整可运行练习接口。

## 可读题面与接口

数据库按集合名保存字典行。`insert(collection, row)` 追加一份行副本并返回自增 `row_id`。`query(collection, filters=None)` 返回同时满足所有等值条件的行；结果按插入顺序排列，并返回副本。未知集合查询返回空列表还是报错需要统一，这里选择空列表。

```python
db = Database()
db.insert("users", {"name": "Ana", "age": 30, "city": "NY"})
db.insert("users", {"name": "Bob", "age": 30, "city": "SF"})
db.query("users", {"age": 30, "city": "NY"})
# [{"_id": 1, "name": "Ana", "age": 30, "city": "NY"}]
```



## 解法与关键数据结构

维护 `rows: dict[str, list[dict]]` 和每个集合的 `next_id`。插入时拒绝调用方伪造 `_id`，复制字典后写入系统 ID。查询逐行执行 `all(row.get(k, MISSING) == v for ...)`；必须用独立的 `MISSING` 哨兵，不能把缺字段和字段值 `None` 混为一谈。若之后支持范围比较，可把 filter 变成 `(field, operator, value)`，但基础接口保持简单。

## 复杂度与边界测试

设集合有 `N` 行、过滤字段 `F` 个，插入平均 `O(C)`，查询 `O(NF)`，返回空间 `O(KC)`。测试首次插入、多个集合 ID 是否独立、空 filters 返回全部、未知集合、缺字段、显式 `None`、重复行、调用方修改原 row、调用方修改查询结果、非法 `_id` 和不同类型但表面相等的值。若频繁按某字段等值查，可增加 `index[field][value] -> set[row_id]`，代价是插入更慢。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/862e9246-1a5e-49f7-b30e-c9fe39aef1b5)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

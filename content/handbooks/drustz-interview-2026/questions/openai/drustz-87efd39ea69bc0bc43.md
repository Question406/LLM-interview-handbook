---
id: drustz-87efd39ea69bc0bc43
section: openai
order: 175
level: A
title: In-Memory Database with Multi-Condition Query and Ordering
quick: >-
  original-structured-preparation-guide · In-Memory Database with
  Multi-Condition Query and Ordering
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
      https://www.1point3acres.com/interview/problems/1992efed-1d3c-4a76-bc45-362b9083c249
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# In-Memory Database：多条件查询与多列排序

## 证据边界

标题明确要求 multi-condition query 和 ordering；公开相关版本还明确多条件按 AND、支持一或多列排序，并提醒数值字符串不能按字典序比较。本地资料的另一实现用 predicate lambda。下面采用结构化条件与排序项，便于验证类型；OR、JOIN、DELETE 和 SQL 字符串 parser 不属于已确认范围。

## 可读题面与接口

表有固定列、列类型和自增 ID。`select` 接受投影列、`Condition(column, op, value)` 列表，以及 `Order(column, ascending)` 列表。所有条件同时成立才保留；按第一个排序列为主键、后续列依次打破平局；完全相同则保持行 ID 顺序。

```python
db.create_table("u", {"name": str, "age": int, "score": int})
db.insert("u", {"name": "B", "age": 10, "score": 8})
db.insert("u", {"name": "A", "age": 2, "score": 8})
db.select(
    "u",
    ["name", "age"],
    [Condition("score", ">=", 8)],
    [Order("score", False), Order("age", True)],
)
# [{"name":"A","age":2}, {"name":"B","age":10}]
```



## 解法与关键数据结构

`Table` 保存 `schema`、行列表和列名到位置的映射。插入时把值规范化为列类型；过滤时通过运算符白名单逐项比较。多列且升降方向不同，可从最后一项到第一项连续调用稳定排序；再以 row ID 作为最终稳定 tie-break。若存储的是字符串 `"10"` 和 `"2"`，必须先按 `int` 列转换，否则排序会错误。

## 复杂度与边界测试

`N` 行、`P` 条件、命中 `K` 行、`S` 个排序键时，扫描 `O(NP)`，稳定多次排序 `O(SK log K)`，空间 `O(K)`。测试零条件/零排序、条件列不在投影中、升降混合、重复键、数值字符串、类型转换失败、`None`、未知操作符、未知列和空结果。优化等值查询可对列建哈希索引，范围查询可用有序索引；复合索引需按常见过滤前缀设计。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/1992efed-1d3c-4a76-bc45-362b9083c249)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

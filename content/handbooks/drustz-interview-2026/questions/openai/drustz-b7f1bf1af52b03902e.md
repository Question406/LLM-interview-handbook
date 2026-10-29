---
id: drustz-b7f1bf1af52b03902e
section: openai
order: 184
level: A
title: In-Memory Key-Value Database CRUD Implementation
quick: >-
  original-structured-preparation-guide · In-Memory Key-Value Database CRUD
  Implementation
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
      https://www.1point3acres.com/interview/problems/4c7b892d-2d33-4bb2-8855-2dc6a30fa1d1
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# In-Memory Key-Value Database：CRUD

> 旧正文来自更复杂的 SQL 数据库题，不能当成这条 UUID 的精确答案。下面从标题能确认的 CRUD 核心开始，并把可选扩展单独列出。

## 基础 API

```text
set(key, value)       创建或覆盖
get(key)              返回 value 或 not-found
delete(key)           删除并返回是否存在
contains(key)         判断存在性
```



用 hash map 保存数据即可：

```python
class KeyValueDB:
    def __init__(self):
        self._data = {}

    def set(self, key, value):
        self._data[key] = value

    def get(self, key):
        if key not in self._data:
            raise KeyError(key)
        return self._data[key]

    def delete(self, key):
        return self._data.pop(key, None) is not None

    def contains(self, key):
        return key in self._data
```



如果 `None` 是合法 value，`delete` 不能用上面的返回值判断，应该先检查 `key in _data`。

## 复杂度

hash map 的 CRUD 平均为 `O(1)`，最坏受哈希冲突影响；空间为 `O(n)`。

## 可能的 follow-up

范围查询需要有序索引；TTL 需要过期时间与清理策略；事务需要 undo log 或多版本；并发访问需要锁或分片。不要在题目没要求时一次性把这些全做进去。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/4c7b892d-2d33-4bb2-8855-2dc6a30fa1d1)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

---
id: drustz-8fbb6c3427b63ddfa2
section: anthropic
order: 77
level: A
title: Python Class and Data Structures
quick: original-structured-preparation-guide · Python Class and Data Structures
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
      https://www.1point3acres.com/interview/problems/1c35c2c1-9209-49c2-8ad6-aca71db1ffdb
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Python 类与数据结构

## 题目要做什么

设计一个 Python 类，用集合保存不重复的元素，并提供五个方法：

1. `add_item(item)`：加入元素，重复加入不产生副本；
2. `remove_item(item)`：存在则删除，不存在则不操作；
3. `sort_items()`：返回所有元素的升序列表；
4. `hash_items()`：返回 `{元素: hash(元素)}`；
5. `binary_search(item)`：在排序结果中二分查找，找到返回下标，否则返回 `-1`。

## 数据结构选择

用 `set` 作为唯一真实数据源，再缓存最近一次排序结果。集合发生实际变化时让缓存失效；排序或二分查找时再按需重建。

```python
from bisect import bisect_left


class ItemStore:
    def __init__(self):
        self._items = set()
        self._sorted_cache = None

    def add_item(self, item) -> None:
        before = len(self._items)
        self._items.add(item)
        if len(self._items) != before:
            self._sorted_cache = None

    def remove_item(self, item) -> None:
        if item in self._items:
            self._items.remove(item)
            self._sorted_cache = None

    def _sorted(self):
        if self._sorted_cache is None:
            self._sorted_cache = sorted(self._items)
        return self._sorted_cache

    def sort_items(self):
        return list(self._sorted())

    def hash_items(self):
        return {item: hash(item) for item in self._items}

    def binary_search(self, item) -> int:
        values = self._sorted()
        index = bisect_left(values, item)
        return index if index < len(values) and values[index] == item else -1
```



## 复杂度

- 添加、删除：平均 `O(1)`；
- 首次构建排序缓存：`O(n log n)`；
- 缓存有效时二分：`O(log n)`；
- 返回排序列表副本和构造哈希映射：`O(n)`；
- 总空间：`O(n)`。

## 边界

元素必须可哈希并且能相互比较。混合 `int` 和 `str` 可能无法排序；字符串 `hash()` 跨 Python 进程不保证一致；并发修改时还需要锁或不可变快照。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/1c35c2c1-9209-49c2-8ad6-aca71db1ffdb)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

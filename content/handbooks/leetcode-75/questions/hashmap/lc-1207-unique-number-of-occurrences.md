---
id: lc-1207-unique-number-of-occurrences
section: hashmap
order: 2
level: A
title: LC 1207 · 独一无二的出现次数
quick: >-
  先用哈希数出每个值的出现次数，再把这些次数放进集合：集合大小等于不同值的个数，说明次数两两不同。时间 $O(n)$，额外空间
  $O(n)$。
tags:
  - Array
  - Hash
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1207. Unique Number of Occurrences
    url: https://leetcode.com/problems/unique-number-of-occurrences/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

给整数数组 `arr`，如果每个不同的值出现的次数都互不相同，返回 `true`，否则 `false`。$1 \le n \le 1000$，值在 $[-1000, 1000]$。

## 思路

两层哈希。第一层 `Counter` 得到「值 $\to$ 次数」；第二层问这些次数有没有重复，把 `counts.values()` 丢进 `set`，长度没变就说明没有两个值共用同一个次数。

也可以把次数排序后看相邻是否相等，多一个 $\log$。

## 参考代码

```python
from collections import Counter
from typing import List


def uniqueOccurrences(arr: List[int]) -> bool:
    counts = Counter(arr)
    return len(set(counts.values())) == len(counts)


if __name__ == "__main__":
    assert uniqueOccurrences([1, 2, 2, 1, 1, 3]) is True
    assert uniqueOccurrences([1, 2]) is False
    assert uniqueOccurrences([-3, 0, 1, -3, 1, 1, 1, -3, 10, 0]) is True
    assert uniqueOccurrences([5]) is True
    assert uniqueOccurrences([7, 7, 8, 8]) is False
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(n)$。

## 边界

- 只有一个不同值：一定是 `true`。
- 所有值各出现一次且不止一个值：次数都是 $1$，`false`。
- 负数作为键没问题；换成数组计数时要做下标偏移。

## 追问

- **最少删几个元素，让出现次数两两不同（LC 1647 思路）？** 次数从大到小排序，贪心往下压：每个次数不能超过上一个次数减一，也不能小于 $0$，差值就是要删的数量。排序后时间 $O(k \log k)$，$k$ 是不同值个数。

```python
from collections import Counter

def minDeletions(arr):
    freqs = sorted(Counter(arr).values(), reverse=True)
    deleted, prev = 0, None
    for f in freqs:
        keep = f if prev is None else max(0, min(f, prev - 1))
        deleted += f - keep
        prev = keep
    return deleted
```

- **不用 `Counter`？** 值域只有 $2001$ 个，开数组 `cnt[x + 1000] += 1` 计数；次数最大是 $n$，再开一个长度 $n+1$ 的布尔数组查重，全程不碰哈希。

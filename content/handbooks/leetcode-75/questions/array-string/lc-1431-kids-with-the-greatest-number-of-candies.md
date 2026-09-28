---
id: lc-1431-kids-with-the-greatest-number-of-candies
section: array-string
order: 3
level: A
title: LC 1431 · 拥有最多糖果的孩子
quick: >-
  先求当前最大值 `mx`，再逐个判断 `candies[i] + extraCandies >= mx`。其他孩子不动，所以只需和原最大值比。时间
  $O(n)$，额外空间 $O(1)$（不含答案）。
tags:
  - Array
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1431. Kids With the Greatest Number of Candies
    url: https://leetcode.com/problems/kids-with-the-greatest-number-of-candies/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

`candies[i]` 是第 $i$ 个孩子的糖果数，另有 `extraCandies` 颗额外糖果。对每个孩子判断：把额外糖果全给他后，他的糖果数是否不少于所有孩子（并列也算最多）。返回布尔数组。$2 \le n \le 100$。

## 思路

给第 $i$ 个孩子加糖时，其他人的数量不变，所以要比的对象只有原数组的最大值 `mx`。先扫一遍求 `mx`，再扫一遍判 `candies[i] + extra >= mx`。

逐个孩子都重新求一次「加完后的最大值」是 $O(n^2)$，没有必要。条件用 `>=`，并列算最多。

## 参考代码

```python
from typing import List


def kidsWithCandies(candies: List[int], extraCandies: int) -> List[bool]:
    mx = max(candies)
    return [c + extraCandies >= mx for c in candies]


if __name__ == "__main__":
    assert kidsWithCandies([2, 3, 5, 1, 3], 3) == [True, True, True, False, True]
    assert kidsWithCandies([4, 2, 1, 1, 2], 1) == [True, False, False, False, False]
    assert kidsWithCandies([12, 1, 12], 10) == [True, False, True]
    assert kidsWithCandies([1, 1], 0) == [True, True]
    print("ok")
```

## 复杂度

时间 $O(n)$，两遍扫描。除答案外额外空间 $O(1)$。

## 边界

- `extraCandies` 为 $0$：只有原本就等于最大值的孩子为真。
- 多个孩子并列最大：他们都为真，因为比较是 `>=`。
- 所有人糖果相同：全部为真。

## 追问

- **同一个数组要回答很多个不同的 `extra`，每次只要「有几个孩子能成为最多」？** 先排序，再对每个 `extra` 二分找第一个 `c >= mx - extra` 的位置，个数是 $n$ 减该位置。预处理 $O(n\log n)$，单次查询 $O(\log n)$。

```python
from bisect import bisect_left


def countKids(candies, extras):
    a = sorted(candies)
    mx = a[-1]
    return [len(a) - bisect_left(a, mx - e) for e in extras]
```

---
id: lc-128-longest-consecutive-sequence
section: hashmap
order: 9
level: S
title: LC 128 · 最长连续序列
quick: >-
  先入集合。只从序列起点出发：若 $x-1$ 不在集合，再向右数 $x,x+1,\ldots$。每个数只被数一次，时间
  $O(n)$。
tags:
  - Hash
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 128. 最长连续序列
    url: https://leetcode.cn/problems/longest-consecutive-sequence/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

在未排序数组里找最长连续整数序列的长度。数字可以不相邻，值连续即可。要求 $O(n)$。

## 思路

排序后再扫是 $O(n\log n)$。$O(n)$ 靠哈希集合：先把所有数丢进 `set`。枚举 $x$ 时，只有 $x-1$ 不在集合才是一段的左端点，再 `while x+len in set` 向右延伸。非起点的数跳过，从而每个数进内层循环至多一次。

`[100,4,200,1,3,2]` 的最长段是 $1,2,3,4$，长度 $4$。重复数字集合会去重，不影响长度。

## 参考代码

```python
from typing import List


def longestConsecutive(nums: List[int]) -> int:
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:
            y = x
            while y in s:
                y += 1
            best = max(best, y - x)
    return best


if __name__ == "__main__":
    assert longestConsecutive([100, 4, 200, 1, 3, 2]) == 4
    assert longestConsecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9
    assert longestConsecutive([]) == 0
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(n)$。外层跳过非起点，内层每个元素最多访问一次。

## 边界

- 空数组长度为 $0$；$[1]$ 长度为 $1$。
- 全相同：集合去重后只剩一个起点，长度为 $1$。
- 含负数与 $0$ 不影响：连续性看值，不看下标。

## 追问

- **要输出具体序列而不是长度？** 扫描时除了 `best` 长度，再记下该段起点 `best_start`。只在 $x-1$ 不在集合时才向右延伸，和求长度同一套 $O(n)$。答案用 `range(best_start, best_start + best_len)` 展开即可。若有多段同样长，题面没要求就返回任意一段。重复数字已被 `set` 吃掉，展开时不会出现重复值。

```python
def longestConsecutiveSeq(nums):
    s = set(nums)
    best_start = best_len = 0
    for x in s:
        if x - 1 not in s:
            y = x
            while y in s:
                y += 1
            if y - x > best_len:
                best_start, best_len = x, y - x
    return list(range(best_start, best_start + best_len))
```

- **并查集怎么做？** 每个数先自成连通块，若 $x-1$ 或 $x+1$ 已出现就把相邻值 `union`，根上维护块大小，答案取最大 `size`。时间仍摊还 $O(n)$，但要写 `find`/`union`，常数和代码量都更大。易错点是重复数字不要二次 `union`，否则 size 会翻倍。面试优先讲哈希集合从左端点延伸；并查集当「换一种连通块建模」的加分项。

```python
def longestConsecutiveUF(nums):
    parent, size = {}, {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        parent[rb] = ra
        size[ra] += size[rb]

    for x in nums:
        if x in parent:
            continue
        parent[x] = x
        size[x] = 1
        if x - 1 in parent:
            union(x, x - 1)
        if x + 1 in parent:
            union(x, x + 1)
    return max(size.values(), default=0)
```

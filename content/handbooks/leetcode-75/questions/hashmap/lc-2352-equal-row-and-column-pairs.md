---
id: lc-2352-equal-row-and-column-pairs
section: hashmap
order: 4
level: A
title: LC 2352 · 相等行列对
quick: >-
  把每一行转成 tuple 放进 `Counter` 计数，再把每一列拼成 tuple 去表里查，次数累加就是答案。时间 $O(n^2)$，额外空间
  $O(n^2)$。
tags:
  - Array
  - Hash
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 2352. Equal Row and Column Pairs
    url: https://leetcode.com/problems/equal-row-and-column-pairs/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

给 $n \times n$ 整数矩阵 `grid`，统计满足「第 $r$ 行与第 $c$ 列按顺序逐个元素相等」的 $(r, c)$ 对数。$1 \le n \le 200$。

## 思路

暴力对每对 $(r, c)$ 逐元素比较是 $O(n^3)$。把一整行当成一个键：行转 `tuple`（列表不可哈希）后计数，相同的行会累积次数。然后每一列也转 `tuple` 去查，查到几次就贡献几对。Python 里 `zip(*grid)` 直接给出所有列。

重复行要按次数计：两行相同、一列与它们相等，就是两对，所以用 `Counter` 而不是 `set`。

## 参考代码

```python
from collections import Counter
from typing import List


def equalPairs(grid: List[List[int]]) -> int:
    rows = Counter(tuple(row) for row in grid)
    return sum(rows[col] for col in zip(*grid))


if __name__ == "__main__":
    assert equalPairs([[3, 2, 1], [1, 7, 6], [2, 7, 7]]) == 1
    assert equalPairs([[3, 1, 2, 2], [1, 4, 4, 5], [2, 4, 2, 2], [2, 4, 2, 2]]) == 3
    assert equalPairs([[1]]) == 1
    assert equalPairs([[1, 1], [1, 1]]) == 4
    assert equalPairs([[1, 2], [3, 4]]) == 0
    print("ok")
```

## 复杂度

时间 $O(n^2)$：建键和哈希每行、每列各 $O(n)$。额外空间 $O(n^2)$，存了 $n$ 个长度为 $n$ 的 tuple。

## 边界

- 重复行、重复列：计数相乘式累加，全 $1$ 的 $2 \times 2$ 矩阵答案是 $4$。
- $n = 1$：唯一的行和列相同，答案 $1$。
- 对称矩阵：每行都等于对应的列，答案至少 $n$。

## 追问

- **不想整行做哈希键？** 把行插进 Trie，每个节点是一个元素值，行末节点记次数；每一列沿 Trie 走一遍，走到底就加上次数。复杂度同样 $O(n^2)$，但相同前缀的行共享节点。Trie 的写法见 `lc-208-implement-trie-prefix-tree`。

```python
def equalPairsTrie(grid):
    root = {}
    for row in grid:
        node = root
        for v in row:
            node = node.setdefault(v, {})
        node["#"] = node.get("#", 0) + 1
    n, ans = len(grid), 0
    for c in range(n):
        node = root
        for r in range(n):
            node = node.get(grid[r][c])
            if node is None:
                break
        else:
            ans += node.get("#", 0)
    return ans
```

- **用滚动哈希把一行压成一个整数？** 可以省空间到 $O(n)$，但有碰撞风险，要么用双模数，要么命中后再逐元素复核一遍。

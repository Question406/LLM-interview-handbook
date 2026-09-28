---
id: lc-77-combinations
section: backtracking
order: 2
level: A
title: LC 77 · 组合
quick: >-
  从 $1..n$ 选 $k$ 个数。回溯按升序选，下一层从 $i+1$
  起，避免重复组合。剩余名额不够时可剪枝。
tags:
  - Backtracking
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 77. 组合
    url: https://leetcode.cn/problems/combinations/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

给定 $n$ 与 $k$，返回 $[1,n]$ 中所有长度为 $k$ 的组合。组合与顺序无关，$[1,2]$ 与 $[2,1]$ 算同一个。

## 思路

回溯维护起点 `start`：本层枚举 $i\in[start,n]$，选 $i$ 后下一层从 $i+1$ 开始，天然升序、不重复。路径长度到 $k$ 就收。

剪枝：还要 $need$ 个数，则 $i$ 最大只能到 $n-need+1$，后面凑不齐。不要用全排列再排序去重。和 46 对比：组合下标只往前，排列用 `used`。

## 参考代码

```python
from typing import List


def combine(n: int, k: int) -> List[List[int]]:
    ans = []
    path = []

    def dfs(start: int) -> None:
        if len(path) == k:
            ans.append(path[:])
            return
        need = k - len(path)
        for i in range(start, n - need + 2):
            path.append(i)
            dfs(i + 1)
            path.pop()

    dfs(1)
    return ans


if __name__ == "__main__":
    assert combine(4, 2) == [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
    assert combine(1, 1) == [[1]]
    print("ok")
```

## 复杂度

时间 $O(\binom{n}{k}\cdot k)$，空间 $O(k)$ 加输出。

## 边界

- $k=1$：答案是 `[1]..[n]` 各一。
- $k=n$：只有 `[1,2,...,n]` 一条。
- $n=k=1$：`[[1]]`。剪枝上界 `n-need+1` 在这些情况下不会把区间剪空。

## 追问

- **变成组合总和？** 选的是数组里的值，带剩余量 `remain`，每个数可再用则下一层仍从 $i$ 起，不可再用则 $i+1$。即 LC 39，独立卡 `lc-39-combination-sum`。本题没有 `target`，剪枝只看「剩余名额够不够」。

- **允许重复选 / 输入有重复值？** 两件不同的事。
  1. 同一元素可用无限次（组合可重复）：下一层起点仍是 $i$，不是 $i+1$，等价 LC 39 去掉目标和、改成长度 $k$。
  2. 输入数组本身有重复值、组合要去重：先排序，同层 `i>start` 且 `nums[i]==nums[i-1]` 则跳，下一层仍 $i+1$（每个下标最多一次）。

```python
def combineRepeat(n, k):
    """1..n，同一数字可重复，组合长度 k。"""
    ans, path = [], []

    def dfs(start):
        if len(path) == k:
            ans.append(path[:])
            return
        for i in range(start, n + 1):
            path.append(i)
            dfs(i)
            path.pop()

    dfs(1)
    return ans


def combineDup(nums, k):
    """nums 含重复值，组合去重。"""
    nums.sort()
    ans, path = [], []

    def dfs(start):
        if len(path) == k:
            ans.append(path[:])
            return
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue
            path.append(nums[i])
            dfs(i + 1)
            path.pop()

    dfs(0)
    return ans
```

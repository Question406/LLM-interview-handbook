---
id: lc-216-combination-sum-iii
section: backtracking
order: 2
level: A
title: LC 216 · 组合总和 III
quick: >-
  从 $1$ 到 $9$ 里选 $k$ 个不同数，和为 $n$。回溯时下一层只从更大的数开始，天然去重；剩余和变负或数字不够就剪枝。搜索空间最多
  $\binom{9}{k}$，时间 $O(\binom{9}{k}\cdot k)$，额外空间 $O(k)$。
tags:
  - Backtracking
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 216. Combination Sum III
    url: https://leetcode.com/problems/combination-sum-iii/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

找出所有由 $k$ 个数组成、和为 $n$ 的组合：只能用 $1$ 到 $9$，每个数最多用一次。返回组合列表，组合之间顺序任意，同一组合不能重复出现。约束 $2\le k\le 9$，$1\le n\le 60$。

## 思路

回溯 `dfs(start, remain)`：从 `start` 到 $9$ 枚举下一个数 $x$，放进路径后递归 `dfs(x + 1, remain - x)`。下一层只从更大的数开始，所以每个组合只会以升序出现一次，不需要另外去重。路径长度到 $k$ 时检查 `remain == 0` 再收。

剪枝有两条：数是升序枚举的，$x \gt remain$ 以后更大的数也放不下，直接 `break`；剩下能选的数不够凑满 $k$ 个也可以提前停。暴力做法是枚举 $2^9=512$ 个子集再筛，规模这么小其实也能过，但回溯的写法能直接套到 LC 39 / 40 这类候选集更大的题上。

## 参考代码

```python
from typing import List


def combinationSum3(k: int, n: int) -> List[List[int]]:
    ans: List[List[int]] = []
    path: List[int] = []

    def dfs(start: int, remain: int) -> None:
        if len(path) == k:
            if remain == 0:
                ans.append(path[:])
            return
        for x in range(start, 10):
            if x > remain:
                break
            if 9 - x + 1 < k - len(path):
                break
            path.append(x)
            dfs(x + 1, remain - x)
            path.pop()

    dfs(1, n)
    return ans


if __name__ == "__main__":
    assert sorted(combinationSum3(3, 7)) == [[1, 2, 4]]
    assert sorted(combinationSum3(3, 9)) == [[1, 2, 6], [1, 3, 5], [2, 3, 4]]
    assert combinationSum3(4, 1) == []
    assert combinationSum3(9, 45) == [[1, 2, 3, 4, 5, 6, 7, 8, 9]]
    assert combinationSum3(2, 18) == []
    print("ok")
```

## 复杂度

最多枚举 $\binom{9}{k}$ 个组合，每个收集时拷贝 $O(k)$，时间 $O(\binom{9}{k}\cdot k)$，上界是常数级。额外空间 $O(k)$ 递归栈与路径，输出另计。

## 边界

- $n$ 太小凑不出 $k$ 个不同数（如 $k=4, n=1$）：返回 `[]`。
- $n$ 太大（超过 $9+8+\dots$ 的最大可能和）：同样返回 `[]`，剪枝会让搜索很快结束。
- $k=9$：只能全选，和必须是 $45$。

## 追问

- **不用回溯，用位掩码怎么做？** 枚举 $0$ 到 $2^9-1$ 的每个 mask，第 $i$ 位为 $1$ 表示选了 $i+1$。`popcount == k` 且和为 $n$ 就收。时间 $O(2^9\cdot 9)$，写起来更短，但不好推广到更大的候选集。

```python
def combinationSum3Mask(k, n):
    ans = []
    for mask in range(1 << 9):
        if bin(mask).count("1") != k:
            continue
        nums = [i + 1 for i in range(9) if mask >> i & 1]
        if sum(nums) == n:
            ans.append(nums)
    return ans
```

- **候选数可重复使用（LC 39）？** 递归时下一层从 $x$ 本身开始而不是 $x+1$，终止条件改成 `remain == 0`，其余骨架不变。

---
id: lc-39-combination-sum
section: backtracking
order: 4
level: A
title: LC 39 · 组合总和
quick: >-
  可重复选，下标不回退。回溯：选 `candidates[i]` 后下一层仍从 $i$
  开始；按序枚举避免同一组合不同排列。
tags:
  - Backtracking
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 39. 组合总和
    url: https://leetcode.cn/problems/combination-sum/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

无重复正整数 `candidates` 与目标和 `target`。每个数可选用无限次，求所有和为 `target` 的组合。顺序不同的同一组只算一次。

## 思路

回溯剩余量 `remain` 与起点 `start`。本层从 `start` 往后选，选中 `x` 后递归 `remain-x`，起点仍是当前下标 $i$（可再用 $x$），不能回到更小下标（避免 $[2,2,3]$ 与 $[3,2,2]$ 重复）。`remain==0` 收答案；先排序则 $x>\texttt{remain}$ 可直接 break。

对比 77：组合下标 $i+1$；本题可重复故是 $i$。每个数最多一次见 LC 40。

## 参考代码

```python
from typing import List


def combinationSum(candidates: List[int], target: int) -> List[List[int]]:
    candidates.sort()
    ans = []
    path = []

    def dfs(start: int, remain: int) -> None:
        if remain == 0:
            ans.append(path[:])
            return
        for i in range(start, len(candidates)):
            x = candidates[i]
            if x > remain:
                break
            path.append(x)
            dfs(i, remain - x)
            path.pop()

    dfs(0, target)
    return ans


if __name__ == "__main__":
    assert combinationSum([2, 3, 6, 7], 7) == [[2, 2, 3], [7]]
    assert combinationSum([2, 3, 5], 8) == [[2, 2, 2, 2], [2, 3, 3], [3, 5]]
    assert combinationSum([2], 1) == []
    print("ok")
```

## 复杂度

设目标 $T$、最小候选 $m$，深度约 $T/m$。时间指数级，约 $O(n^{T/m})$。空间 $O(T/m)$ 加输出。

## 边界

- 凑不出：`dfs` 全部 `break` / 走完，`ans` 为空。
- 单元素等于 `target`：直接收 `[x]`；大于 `target`：排序后该元素及后面都跳过。
- 最小候选已大于 `target`：第一层立刻 `break`，返回 `[]`。
- 对比组合题：只选下标、没有目标和，见 LC 77，独立卡 `lc-77-combinations`。

## 追问

- **每个数至多一次（LC 40 Combination Sum II）？** 候选可以有重复值，同一组合不能因为重复值的不同下标被收两次。先排序。递归改成 `dfs(i+1, remain-x)`（下标前进，不能再用当前元素）。同层跳过：`i > start` 且 `candidates[i] == candidates[i-1]` 则 `continue`，前一个相同值没选，当前再选只会复制同一条路径。时间仍指数级。

```python
def combinationSum2(candidates, target):
    candidates.sort()
    ans, path = [], []

    def dfs(start, remain):
        if remain == 0:
            ans.append(path[:])
            return
        for i in range(start, len(candidates)):
            x = candidates[i]
            if x > remain:
                break
            if i > start and x == candidates[i - 1]:
                continue
            path.append(x)
            dfs(i + 1, remain - x)
            path.pop()

    dfs(0, target)
    return ans
```

- **只要方案数、不要列出组合？** 完全背包。`dp[x]` 表示凑出 $x$ 的组合数。`dp[0]=1`。外层循环物品、内层容量从小到大，这样每个组合只计一次（顺序无关）。内外层对调变成排列数（LC 377）。最少枚数则是零钱兑换，见 LC 322，独立卡 `lc-322-coin-change`。

```python
def combinationSumCount(candidates, target):
    dp = [0] * (target + 1)
    dp[0] = 1
    for c in candidates:
        for x in range(c, target + 1):
            dp[x] += dp[x - c]
    return dp[target]
```

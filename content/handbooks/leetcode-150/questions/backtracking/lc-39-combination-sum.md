---
id: lc-39-combination-sum
section: backtracking
order: 4
level: A
title: LC 39 · 组合总和
quick: >-
  回溯时带着剩余目标和与起始下标。选了 `candidates[i]` 后下一层仍从 $i$
  开始，所以同一个数能重复用；不回到更小的下标，就不会把不同排列重复算成组合。先排序，超过剩余量就 break。
tags:
  - Backtracking
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 39. 组合总和
    url: 'https://leetcode.cn/problems/combination-sum/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定互不相同的正整数数组 `candidates` 和目标整数 `target`，返回所有元素之和等于 target 的组合。每个候选数可以被重复选择任意多次；同一组数仅因排列顺序不同，不算不同组合。答案中不能出现重复组合。

### 输入与输出

实现 `combinationSum(candidates, target) -> List[List[int]]`。返回所有合法组合，组合之间的顺序可以任意；没有组合时返回空列表。

### 约束

- `1 <= len(candidates) <= 30`，候选值互不相同。
- `2 <= candidates[i] <= 40`。
- `1 <= target <= 40`。

### 示例

```text
输入：candidates = [2,3,6,7], target = 7
输出：[[2,2,3],[7]]
```

[LeetCode 原题](https://leetcode.com/problems/combination-sum/description/)

## 解题思路与参考答案

## 题意

无重复正整数 `candidates` 与目标和 `target`。每个数可选用无限次，求所有和为 `target` 的组合。顺序不同的同一组只算一次。

## 思路

我会回溯，状态是剩余量 `remain` 和起点 `start`。本层从 `start` 往后选，选中 `x` 就递归 `remain-x`，起点仍是当前下标 $i$，因为 $x$ 还能再用；但不能回到更小的下标，否则 $[2,2,3]$ 和 $[3,2,2]$ 会重复出现。`remain==0` 就收答案。先排序的话，$x>\texttt{remain}$ 可以直接 break，后面更大的都不用试了。

拿 `[2,3,6,7]`、`target=7` 走一遍。从 2 开始，连选三个 2 剩 1，下一个 2 已经大于 1，break；退一步改选 3，正好凑成 `[2,2,3]`。其他以 2 或 3 开头的分支都凑不出来，6 剩 1 也不行，最后 7 自己就是一条。答案是 `[[2,2,3],[7]]`。

和 LC 77 对比，组合题下一层从 $i+1$ 开始；本题可以重复，所以还是 $i$。每个数最多用一次是 LC 40。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

如果题目允许答案以任意顺序返回，先排序或转成集合再比较；只有题目保证没有重复结果时才适合直接用集合，否则还要检查重复次数。

```python
assert combinationSum([2, 3, 6, 7], 7) == [[2, 2, 3], [7]]
assert combinationSum([2, 3, 5], 8) == [[2, 2, 2, 2], [2, 3, 3], [3, 5]]
assert combinationSum([2], 1) == []
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

设目标 $T$、最小候选 $m$，递归深度约 $T/m$。时间是指数级，约 $O(n^{T/m})$；空间 $O(T/m)$ 加输出。

## Edge Cases

凑不出来时，`dfs` 全部 `break` 或走完，`ans` 为空。单个元素等于 `target` 时直接收 `[x]`；大于 `target` 的元素，排序后它和后面的都会跳过。最小候选已经大于 `target`，第一层立刻 `break`，返回 `[]`。只选下标、没有目标和的组合题是 LC 77，独立卡 `lc-77-combinations`。

## 追问

**每个数最多用一次（LC 40 Combination Sum II）呢？**
先排序，递归改成 `dfs(i+1, remain-x)`，下标前进，不能再用当前元素。这题候选可以有重复值，同一个组合不能因为重复值的下标不同被收两次，所以还要同层跳过：`i > start` 且 `candidates[i] == candidates[i-1]` 就 `continue`。同一层里前一个相同的值没选，当前再选只会复制同一条路径。时间仍是指数级。

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

**只要方案数、不用列出组合呢？**
这就是完全背包。`dp[x]` 表示凑出 $x$ 的组合数，`dp[0]=1`。外层循环物品、内层容量从小到大，每个组合只计一次，和顺序无关；内外层对调就变成排列数（LC 377）。要最少枚数的话是零钱兑换 LC 322，独立卡 `lc-322-coin-change`。

```python
def combinationSumCount(candidates, target):
    dp = [0] * (target + 1)
    dp[0] = 1
    for c in candidates:
        for x in range(c, target + 1):
            dp[x] += dp[x - c]
    return dp[target]
```

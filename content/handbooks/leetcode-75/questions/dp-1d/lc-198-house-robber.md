---
id: lc-198-house-robber
section: dp-1d
order: 3
level: S
title: LC 198 · 打家劫舍
quick: >-
  不能抢相邻房屋。$dp[i]=\max(dp[i-1],\,dp[i-2]+nums[i])$：不抢第 $i$ 家就继承上一格，抢就接隔一格。滚两个变量，时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - DP
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 198. House Robber
    url: https://leetcode.com/problems/house-robber/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

一排房屋，`nums[i]` 是第 $i$ 家的金额（非负），相邻两家不能同时抢。求能抢到的最大金额。$1\le n\le 100$。

## 思路

$dp[i]$ 表示只考虑前 $i$ 家（下标 $0..i-1$）能抢到的最大值。对第 $i-1$ 家只有两种选择：不抢则继承 $dp[i-1]$；抢则上一家必须空着，得 $dp[i-2]+nums[i-1]$。

$dp[i]=\max(dp[i-1],\ dp[i-2]+nums[i-1])$，$dp[0]=0$，$dp[1]=nums[0]$。

每格只看前两格，用 `prev2`、`prev1` 滚过去即可。贪心「隔一家抢一家」是错的，例如 `[2,1,1,2]` 最优是抢首尾，间隔为 $3$。

## 参考代码

```python
from typing import List


def rob(nums: List[int]) -> int:
    prev2 = prev1 = 0
    for x in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + x)
    return prev1


if __name__ == "__main__":
    assert rob([1, 2, 3, 1]) == 4
    assert rob([2, 7, 9, 3, 1]) == 12
    assert rob([5]) == 5
    assert rob([2, 1]) == 2
    assert rob([2, 1, 1, 2]) == 4
    assert rob([0, 0, 0]) == 0
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- 只有 $1$ 间：答案就是该金额。
- 两间：取较大，$\max(nums[0], nums[1])$。
- 最优解间隔超过 $2$（如 `[2,1,1,2]`）：DP 会自动选「连续跳过两家」，奇偶分组贪心会错。

## 追问

- **环形（LC 213）？** 首尾相邻，不能同时抢。拆成两次线性：`nums[:-1]`（不抢最后一家）与 `nums[1:]`（不抢第一家），取较大。$n=1$ 单独返回。时间仍 $O(n)$。

```python
def robII(nums):
    def rob_line(a):
        prev2 = prev1 = 0
        for x in a:
            prev2, prev1 = prev1, max(prev1, prev2 + x)
        return prev1

    if len(nums) == 1:
        return nums[0]
    return max(rob_line(nums[:-1]), rob_line(nums[1:]))
```

- **树上相邻（LC 337）？** 每个结点返回 `(不抢该点, 抢该点)`。不抢 = 左右儿子各取 $\max$ 之和；抢 = 该点值 + 左不抢 + 右不抢。后序一遍，时间 $O(n)$。

```python
def robIII(root):
    def dfs(node):
        if not node:
            return (0, 0)
        ls, lt = dfs(node.left)
        rs, rt = dfs(node.right)
        return (max(ls, lt) + max(rs, rt), node.val + ls + rs)

    return max(dfs(root))
```

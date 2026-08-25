---
id: lc-198-house-robber
section: dp-1d
order: 2
level: S
title: LC 198 · 打家劫舍
quick: >-
  不能抢相邻房屋。$dp[i]=\max(dp[i-1],\,dp[i-2]+nums[i])$。滚两个变量：不偷到上一间 vs
  偷当前。时间 $O(n)$。
tags:
  - DP
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 198. 打家劫舍
    url: https://leetcode.cn/problems/house-robber/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

一排房屋金额 `nums`，不能抢相邻两家。求能抢到的最大金额。

## 思路

到第 $i$ 家：不抢则继承 $dp[i-1]$；抢则 $dp[i-2]+nums[i]$。取较大。

用 `prev2`、`prev1` 滚过去即可。白板我先讲「相邻互斥」，再写转移。环形版是 LC 213：首尾不能同时抢，拆成 `nums[0:-1]` 与 `nums[1:]` 两次。

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
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- 只有 $1$ 间：答案就是该金额，循环一次 `prev1` 变成它。
- 两间：取较大，$\max(nums[0], nums[1])$。
- 金额含 $0$：转移仍是 $\max(\text{不偷},\,\text{偷})$，$0$ 相当于没贡献。

## 追问

- **环形（LC 213）？** 首尾相邻，不能同时偷。拆成两次线性：`nums[0..n-2]`（可以偷第一家、不偷最后）与 `nums[1..n-1]`（不偷第一家）。$n=1$ 单独返回。时间仍 $O(n)$。

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

- **树上相邻（LC 337）？** 每个结点返回 `(不偷该点, 偷该点)`。不偷 = 左右儿子各自取 $\max(\text{偷},\text{不偷})$ 之和；偷 = 该点值 + 左不偷 + 右不偷。根取两者较大。后序一遍，时间 $O(n)$。

```python
def robIII(root):
    def dfs(node):
        if not node:
            return (0, 0)
        ls, lt = dfs(node.left)
        rs, rt = dfs(node.right)
        skip = max(ls, lt) + max(rs, rt)
        take = node.val + ls + rs
        return (skip, take)
    return max(dfs(root))
```

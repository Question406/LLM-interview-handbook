---
id: lc-198-house-robber
section: dp-1d
order: 2
level: S
title: LC 198 · 打家劫舍
quick: "一维 DP：到第 $i$ 间房，不抢就继承 $dp[i-1]$，抢就是 $dp[i-2]+nums[i]$，即 $dp[i]=\\max(dp[i-1],\\,dp[i-2]+nums[i])$。转移只依赖前两项，滚成两个变量，时间 $O(n)$、空间 $O(1)$。"
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

## 题目描述

一排房屋从左到右排列，`nums[i]` 表示第 i 间房里可取得的金额。你可以选择任意一些房屋，但不能同时选择两间相邻房屋。求在不违反相邻限制的前提下，能够取得的最大总金额。

### 输入与输出

实现 `rob(nums) -> int`。返回最大金额，不要求返回选择的房屋下标；允许一间也不选。房屋首尾不相邻，本题不是环形街道。

### 约束

- `1 <= len(nums) <= 100`。
- `0 <= nums[i] <= 400`。

### 示例

```text
输入：nums = [1,2,3,1]
输出：4
```

[LeetCode 原题](https://leetcode.com/problems/house-robber/description/)

## 解题思路与参考答案

## 题意

一排房屋的金额是 `nums`，不能抢相邻的两家，求能抢到的最大金额。

## 思路

这是一维 DP。每间房只有抢和不抢两种选择，而且只受前一间约束。到第 $i$ 家时，不抢就继承 $dp[i-1]$；抢的话前一家一定没抢，拿 $dp[i-2]+nums[i]$，两者取较大。

拿 `[2, 7, 9, 3, 1]` 走一遍：前两间最好是 $7$；到 $9$ 时，抢它得 $2+9=11$，比 $7$ 大；到 $3$ 时，$7+3=10$ 不如 $11$；到 $1$ 时，$11+1=12$，答案是 $12$。

转移只看前两项，所以用 `prev2`、`prev1` 两个变量，每处理一间房更新一次就够了。环形版是 LC 213，首尾不能同时抢，拆成 `nums[0:-1]` 和 `nums[1:]` 各跑一次，放在追问里。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert rob([1, 2, 3, 1]) == 4
assert rob([2, 7, 9, 3, 1]) == 12
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

只有 $1$ 间时答案就是它的金额，循环一次 `prev1` 就变成它。两间时取较大的，即 $\max(nums[0], nums[1])$。金额里有 $0$ 也不影响，转移仍是 $\max(\text{不偷},\,\text{偷})$，$0$ 相当于没贡献。

## 追问

**房子围成一圈（LC 213）呢？**
首尾相邻，不能同时偷，就拆成两次线性：`nums[0..n-2]`（可以偷第一家、不偷最后一家）和 `nums[1..n-1]`（不偷第一家），取较大。$n=1$ 单独返回，时间仍是 $O(n)$。

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

**相邻关系换到树上（LC 337）呢？**
每个结点返回 `(不偷该点, 偷该点)` 两个值。不偷时，左右儿子各自取 $\max(\text{偷},\text{不偷})$ 再相加；偷时，是该点值加左儿子不偷、右儿子不偷。根取两者较大，后序遍历一遍，时间 $O(n)$。

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

---
id: lc-300-longest-increasing-subsequence
section: dp-1d
order: 5
level: S
title: LC 300 · 最长递增子序列
quick: "先讲清 $O(n^2)$ DP：$dp[i]$ 是以 $i$ 结尾的 LIS 长度，枚举左侧更小的 $j$ 转移。要 $O(n\\log n)$ 就维护 `tails`，即各长度递增子序列的最小结尾，每个新数二分找第一个 $\\ge$ 它的位置替换，`tails` 的长度就是答案。"
tags:
  - DP
  - Binary Search
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 300. 最长递增子序列
    url: https://leetcode.cn/problems/longest-increasing-subsequence/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定一个整数数组，返回其中最长严格递增子序列的长度。子序列可以删去原数组中的一些元素，但剩余元素必须保持原有相对顺序，不要求在原数组中连续。“严格递增”不允许相邻所选值相等。

### 输入与输出

实现 `lengthOfLIS(nums: List[int]) -> int`。只返回最长长度，不需要返回所选下标或子序列本身。

### 约束

- `1 <= len(nums) <= 2500`，元素范围为 `[-10^4,10^4]`。

### 示例

```text
输入：nums = [10,9,2,5,3,7,101,18]
输出：4
```

例如 `[2,3,7,101]` 是长度为 4 的合法子序列；它不必是数组中的连续片段。

## 解题思路与参考答案

## 题意

给整数数组 `nums`，返回最长严格递增子序列的长度。子序列可以删元素，但不能改相对顺序。

## 思路

我会先用一句话讲 $O(n^2)$ 的 DP，再写 $O(n\log n)$ 的 `tails` 加二分。$dp[i]$ 是以 `nums[i]` 结尾的 LIS 长度，枚举 $j\lt i$ 且 `nums[j] < nums[i]`，取 $\max dp[j]+1$，答案是 $\max dp$，这一版是 $O(n^2)$。

要更快就换个状态：`tails[k]` 表示长度为 $k+1$ 的递增子序列里，最小的结尾值。扫到 $x$ 时，二分找第一个 $\ge x$ 的位置替换（严格递增所以用 $\ge$），找不到就追加。结尾越小，越容易接上后面的数，所以替换不会损失能达到的长度。拿 `[10, 9, 2, 5, 3, 7, 101, 18]` 走一遍：`10` 进来，`9` 替换它，`2` 再替换；`5` 追加成 `[2, 5]`，`3` 替换 `5` 得到 `[2, 3]`；`7`、`101` 依次追加，`18` 替换 `101`，最后是 `[2, 3, 7, 18]`，长度 $4$。

`tails` 始终递增，它的长度就是答案；但里面的值来自不同的候选序列，不保证能拼成原数组里一条真实的子序列。下面写 $O(n\log n)$，$O(n^2)$ 的代码放在追问里。

## 参考代码

```python
from typing import List


def lengthOfLIS(nums: List[int]) -> int:
    tails = []
    for x in nums:
        lo, hi = 0, len(tails)
        while lo < hi:
            mid = (lo + hi) // 2
            if tails[mid] < x:
                lo = mid + 1
            else:
                hi = mid
        if lo == len(tails):
            tails.append(x)
        else:
            tails[lo] = x
    return len(tails)


if __name__ == "__main__":
    assert lengthOfLIS([10, 9, 2, 5, 3, 7, 101, 18]) == 4
    assert lengthOfLIS([0, 1, 0, 3, 2, 3]) == 4
    assert lengthOfLIS([7, 7, 7, 7, 7, 7, 7]) == 1
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert lengthOfLIS([10, 9, 2, 5, 3, 7, 101, 18]) == 4
assert lengthOfLIS([0, 1, 0, 3, 2, 3]) == 4
assert lengthOfLIS([7, 7, 7, 7, 7, 7, 7]) == 1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

`tails` 版时间 $O(n\log n)$、空间 $O(n)$；朴素 DP 时间 $O(n^2)$、空间 $O(n)$。

## 边界

全递减时每个新数都替换 `tails[0]`，长度 $1$。全递增时每次都追加，长度 $n$。有重复时因为要严格递增，相等的数走「第一个 $\ge x$ 的位置替换」，不会让长度变长。

## 追问

**$O(n^2)$ 写法是什么样？**
就是思路里那套转移：$dp$ 初值都是 $1$，双重循环里遇到 `nums[j] < nums[i]` 就取 $\max dp[j]+1$，最后返回 $\max dp$。面试时先把这套转移讲清楚，再优化成 `tails`。

```python
def lengthOfLIS_n2(nums):
    n = len(nums)
    dp = [1] * n
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
```

**要打印出一条 LIS 呢？**
在 $O(n^2)$ 版里同步记 `prev[i]`，也就是 $i$ 从哪个 $j$ 转移来，然后从 `dp` 最大的下标倒推再反转。`tails` 本身不是某条真实子序列；如果坚持 $O(n\log n)$，就再开 `idx`/`prev`：二分更新时记下是谁占了这个长度，并指向上一个长度的下标。

```python
def reconstructLIS(nums):
    n = len(nums)
    dp = [1] * n
    prev = [-1] * n
    best = 0
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i] and dp[j] + 1 > dp[i]:
                dp[i] = dp[j] + 1
                prev[i] = j
        if dp[i] > dp[best]:
            best = i
    seq = []
    while best != -1:
        seq.append(nums[best])
        best = prev[best]
    seq.reverse()
    return seq
```

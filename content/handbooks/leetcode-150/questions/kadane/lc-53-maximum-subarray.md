---
id: lc-53-maximum-subarray
section: kadane
order: 1
level: S
title: LC 53 · 最大子数组和
quick: >-
  用 Kadane：`dp = max(x, dp + x)`，当前数要么单开一段，要么接在上一段后面，同时维护全局最大。时间 $O(n)$，额外空间 $O(1)$。
tags:
  - DP
  - Kadane
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 53. 最大子数组和
    url: https://leetcode.cn/problems/maximum-subarray/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定非空整数数组，选择一段至少包含一个元素的连续子数组，使元素和最大，并返回这个最大和。子数组必须保持原数组中的连续位置，不能跳过中间元素，也不能把空子数组作为候选。

### 输入与输出

实现 `maxSubArray(nums) -> int`。返回和而不是区间下标；数组可以全部为负数。

### 约束与约定

- `1 <= len(nums) <= 100000`。
- `-10000 <= nums[i] <= 10000`。

### 示例

```text
输入：nums = [-2,1,-3,4,-1,2,1,-5,4]
输出：6
```

示例中连续子数组 [4,-1,2,1] 的和为 6，是最大值。

[官方原题与完整题面](https://leetcode.com/problems/maximum-subarray/description/)。

## 解题思路与参考答案

## 题意

整数数组 `nums` 非空，找一段连续子数组，使它的和最大，返回这个和。

## 思路

我会用 Kadane，也就是一维 DP。`dp` 表示以当前元素结尾的最大和：前面那段的和是正的就接上，否则从自己重新开始。全局答案取所有 `dp` 里的最大值。

拿 `[-2,1,-3,4,-1,2,1,-5,4]` 走一遍：到 1 时前面是 $-2$，丢掉，从 1 开始；到 $-3$ 时 `cur` 变成 $-2$；到 4 时前面是负的，从 4 重开；接着 $-1$、2、1 一路接上，`cur` 依次是 3、5、6，`best` 记到 6；后面的 $-5$ 和 4 都没让它超过 6。答案是 6。

分治也能做：跨中点的最大和等于左边的最大后缀加右边的最大前缀，再和左右两半递归的结果比，时间 $O(n\log n)$，白板上当备选。

## 参考代码

```python
from typing import List


def maxSubArray(nums: List[int]) -> int:
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best


if __name__ == "__main__":
    assert maxSubArray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
    assert maxSubArray([1]) == 1
    assert maxSubArray([5, 4, -1, 7, 8]) == 23
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert maxSubArray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
assert maxSubArray([1]) == 1
assert maxSubArray([5, 4, -1, 7, 8]) == 23
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

全是负数时 `cur` 每次都从自己重开，`best` 是最大的那个负数。这题不允许空子数组（和为 $0$），所以不能返回 $0$。只有一个元素时循环不进，返回它自己。全是正数时整段加起来就是答案。

## 追问

**还要返回下标呢？**
`cur` 从 `x` 重开时记下起点 `s`，`cur` 刷新 `best` 时记下 `[s, i]`，最后返回和与闭区间。`cur + x == x` 时别随便改起点，否则全是 $0$ 的数组会把区间拆碎。

```python
def maxSubArrayRange(nums):
    best = cur = nums[0]
    start = end = s = 0
    for i in range(1, len(nums)):
        if cur + nums[i] < nums[i]:
            cur = nums[i]
            s = i
        else:
            cur += nums[i]
        if cur > best:
            best, start, end = cur, s, i
    return best, start, end
```

**环形数组（LC 918）呢？**
线性 Kadane 只覆盖不跨界的段。跨界的最大和等于总和减去最小子数组和，相当于把中间「最负」的一段丢掉，所以最大、最小各跑一遍。全是负数时最小子数组就是整个数组，`total - min` 会变成 $0$（空段），这题和 LC 918 都不允许，所以用「普通最大 $\lt 0$」特判，直接返回普通最大。单独一张卡 `lc-918-maximum-sum-circular-subarray`。

```python
def maxSubarraySumCircular(nums):
    total = max_end = min_end = 0
    max_sum = min_sum = nums[0]
    for x in nums:
        total += x
        max_end = max(x, max_end + x)
        min_end = min(x, min_end + x)
        max_sum = max(max_sum, max_end)
        min_sum = min(min_sum, min_end)
    if max_sum < 0:
        return max_sum
    return max(max_sum, total - min_sum)
```

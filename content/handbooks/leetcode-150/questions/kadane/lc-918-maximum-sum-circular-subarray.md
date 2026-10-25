---
id: lc-918-maximum-sum-circular-subarray
section: kadane
order: 2
level: A
title: LC 918 · 环形子数组的最大和
quick: "答案取两种情况的较大者：不跨接缝就是普通 Kadane，跨接缝等于 `total` 减去最小子数组和。全负时最小子数组是整个数组，`total - min` 会变成空段的 $0$，这时直接返回普通最大。一遍扫描，时间 $O(n)$。"
tags:
  - Kadane
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 918. 环形子数组的最大和
    url: https://leetcode.cn/problems/maximum-sum-circular-subarray/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定非空整数数组 `nums`，把它看成首尾相接的环。选择一段非空、沿原有顺序连续的子数组，使元素和最大。所选区间可以跨过数组末尾接回开头，但每个原数组位置最多使用一次，不能绕环多圈。

### 输入与输出

实现 `maxSubarraySumCircular(nums) -> int`，返回最大元素和。不能选择空区间，因此全为负数时也必须选择至少一个元素；不需要返回区间端点。

### 约束

- `1 <= len(nums) <= 3 * 10^4`。
- `-3 * 10^4 <= nums[i] <= 3 * 10^4`。

### 示例

```text
输入：nums = [1,-2,3,-2]
输出：3
```

[LeetCode 原题](https://leetcode.com/problems/maximum-sum-circular-subarray/description/)

## 解题思路与参考答案

## 题意

数组首尾相邻成环，要找一段非空的连续子数组，可以跨过接缝，让它的和最大。

## 思路

我会在一次循环里同时跑最大和最小两套 Kadane。答案要么不跨接缝，那就是普通的最大子数组和；要么跨接缝，这时留下的是两头，丢掉的是中间一段，丢掉的那段越小越好，所以跨界的最大和等于总和减去最小子数组和。

拿 `[5, -3, 5]` 走一遍，普通 Kadane 得到整段的 $7$；总和是 $7$，最小子数组是中间的 $-3$，`total - min = 10`，比 $7$ 大，答案就是首尾两个 $5$ 接起来的 $10$。

全负要特判。`[-3, -2, -3]` 的最小子数组就是整个数组，`total - min` 是 $0$，对应一个空段，这题不允许空段。所以我用「普通最大 $< 0$」来判断，成立就直接返回普通最大，这里是 $-2$。

有人会想把数组拆成两段再拼，这样边界容易漏，两套 Kadane 更稳。

## 参考代码

```python
from typing import List


def maxSubarraySumCircular(nums: List[int]) -> int:
    total = 0
    max_end = min_end = 0
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


if __name__ == "__main__":
    assert maxSubarraySumCircular([1, -2, 3, -2]) == 3
    assert maxSubarraySumCircular([5, -3, 5]) == 10
    assert maxSubarraySumCircular([-3, -2, -3]) == -2
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert maxSubarraySumCircular([1, -2, 3, -2]) == 3
assert maxSubarraySumCircular([5, -3, 5]) == 10
assert maxSubarraySumCircular([-3, -2, -3]) == -2
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

一遍循环里同时维护最大、最小的结尾和，时间 $O(n)$，额外空间 $O(1)$。

## 边界

- 全负的时候普通最大 $\lt 0$，直接返回最大的那个负数。这时用 `total - min` 会得到 $0$，是错的。
- 全正的时候最小子数组是最小的单个正数，`total - min` $\lt$ `total`，答案就是普通 Kadane 的结果，也就是 `total`。
- 答案只有一个环绕段时，比如 `[5, -3, 5]`，丢掉中间的 $-3$，`total - min = 10`。

## 追问

**数组不成环（LC 53）怎么写？**
只跑最大结尾和就行，`cur = max(x, cur + x)`，同时维护 `best`。别再算 `total - min`，那样会把「丢掉中间」的跨界段也算进来。这题比线性版多出来的，就是最小子数组和与全负特判。独立卡见 `lc-53-maximum-subarray`。

```python
def maxSubArray(nums):
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best
```

**长度限制为至多 $k$ 呢？**
Kadane 管不了长度，要改成前缀和加单调队列。最大子段和等于 $\max_{1 \le j-i \le k}(pre[j]-pre[i])$，对每个右端 $j$，要找窗口 $[j-k, j)$ 里最小的 `pre[i]`。单调队列存下标，队头过期就弹出，队尾的前缀不比当前小也弹出，这样队头就是窗口里最小的前缀，时间 $O(n)$。如果既是环形又限长，就把数组拼成两倍，再限制窗口不越过 $n$。

```python
from collections import deque

def maxSubarraySumLenAtMostK(nums, k):
    pre, dq, ans = [0], deque([0]), float("-inf")
    for x in nums:
        pre.append(pre[-1] + x)
    for j in range(1, len(pre)):
        while dq and j - dq[0] > k:
            dq.popleft()
        ans = max(ans, pre[j] - pre[dq[0]])
        while dq and pre[dq[-1]] >= pre[j]:
            dq.pop()
        dq.append(j)
    return ans
```

---
id: lc-643-maximum-average-subarray-i
section: sliding-window
order: 1
level: S
title: LC 643 · 子数组最大平均数 I
quick: >-
  长度固定时平均值最大就是和最大，所以用定长滑窗，先算前 $k$ 个的和，之后每右移一步加进一个、减出一个，维护最大和，最后除以 $k$。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Array
  - Sliding Window
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 643. Maximum Average Subarray I
    url: 'https://leetcode.com/problems/maximum-average-subarray-i/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定整数数组 nums 和整数 k，考虑其中所有长度恰好为 k 的连续子数组，返回这些子数组平均值中的最大值。不能跳过中间元素，也不能改变窗口长度来获得更高平均值。

### 输入与输出

实现 `findMaxAverage(nums: List[int], k: int) -> float`。返回平均值而非元素之和；结果允许绝对误差或相对误差不超过 `10^-5`。

### 约束

- `1 <= k <= len(nums) <= 10^5`。
- 每个元素在 `[-10^4,10^4]`，允许负数。

### 示例

```text
输入：nums = [1,12,-5,-6,50,3], k = 4
输出：12.75000
```

示例最优连续片段为 `[12,-5,-6,50]`，其和为 51，平均值为 51/4=12.75。

## 解题思路与参考答案

## 题意

给整数数组 `nums`（长度 $n$）和整数 $k$，找长度恰好为 $k$ 的连续子数组，返回它的最大平均值。误差小于 $10^{-5}$ 即可。$1 \le k \le n \le 10^5$，元素在 $[-10^4, 10^4]$。

## 思路

长度固定，平均值最大等价于和最大，所以我用定长滑动窗口，全程只比较窗口和，最后除一次 $k$，也少了浮点误差。窗口右移一格时，新和 = 旧和 + `nums[i]` - `nums[i-k]`，一步 $O(1)$。暴力对每个起点重新求和是 $O(nk)$，$k$ 接近 $n$ 时退化成 $O(n^2)$。

拿 `[1, 12, -5, -6, 50, 3]`、$k=4$ 走一遍。第一个窗口和是 $1+12-5-6=2$；右移一格加 50 减 1，得 51；再右移加 3 减 12，得 42。最大和 51，除以 4 得 12.75。

## 参考代码

```python
from typing import List


def findMaxAverage(nums: List[int], k: int) -> float:
    s = sum(nums[:k])
    best = s
    for i in range(k, len(nums)):
        s += nums[i] - nums[i - k]
        best = max(best, s)
    return best / k


if __name__ == "__main__":
    assert abs(findMaxAverage([1, 12, -5, -6, 50, 3], 4) - 12.75) < 1e-5
    assert findMaxAverage([5], 1) == 5.0
    assert findMaxAverage([-1, -2, -3], 2) == -1.5
    assert findMaxAverage([0, 4, 0, 3, 2], 1) == 4.0
    assert findMaxAverage([3, 3, 3], 3) == 3.0
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert abs(findMaxAverage([1, 12, -5, -6, 50, 3], 4) - 12.75) < 1e-5
assert findMaxAverage([5], 1) == 5.0
assert findMaxAverage([-1, -2, -3], 2) == -1.5
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## Edge Cases

`best` 初值要用第一个窗口的和，数组可能全负，初值写 $0$ 会错。

$k = n$ 时只有一个窗口，循环不执行，直接返回总和除以 $n$。

$k = 1$ 时退化为求最大元素。

## 追问

**长度至少为 $k$ 的最大平均值（LC 644）呢？**
窗口不再定长，滑窗就失效了。我会二分答案 `mid`，把每个数减去 `mid`，问是否存在长度 $\ge k$ 的子数组和 $\ge 0$，用前缀和 `pre[j] - min(pre[0..j-k])` 一遍判定。答案单调，二分到精度 $10^{-5}$，时间 $O(n \log \frac{R}{\epsilon})$。

```python
def findMaxAverageAtLeastK(nums, k):
    lo, hi = min(nums), max(nums)
    while hi - lo > 1e-6:
        mid = (lo + hi) / 2
        pre, prev_min, ok = 0.0, 0.0, False
        pre_k = 0.0
        for i, x in enumerate(nums):
            pre += x - mid
            if i >= k:
                pre_k += nums[i - k] - mid
                prev_min = min(prev_min, pre_k)
            if i >= k - 1 and pre - prev_min >= 0:
                ok = True
                break
        if ok:
            lo = mid
        else:
            hi = mid
    return lo
```

**要所有窗口的平均值呢？**
同一个滑窗，每步把 `s / k` 追加进结果就行，时间仍是 $O(n)$。

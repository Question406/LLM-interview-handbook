---
id: lc-334-increasing-triplet-subsequence
section: array-string
order: 8
level: S
title: LC 334 · 递增的三元子序列
quick: >-
  贪心维护两个变量：`first` 是目前最小的数，`second` 是「前面有更小数」的数里最小的那个。之后只要遇到比 `second`
  更大的数，递增三元组就存在。时间 $O(n)$，额外空间 $O(1)$。
tags:
  - Array
  - Greedy
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 334. Increasing Triplet Subsequence
    url: 'https://leetcode.com/problems/increasing-triplet-subsequence/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定一个整数数组，判断其中是否存在三个下标 i、j、k，满足 `i < j < k`，并且对应的值也严格递增：`nums[i] < nums[j] < nums[k]`。三个位置不要求相邻，重复的相等值不能代替严格递增关系。

### 输入与输出

实现 `increasingTriplet(nums: List[int]) -> bool`。存在这样的三个位置就返回 `True`，否则返回 `False`；不要求返回具体三元组。

### 约束

- `1 <= len(nums) <= 5 * 10^5`，元素在 32 位有符号整数范围内。
- 进阶要求 O(n) 时间和 O(1) 额外空间。

### 示例

```text
输入：nums = [1,2,3,4,5]
输出：true
```

## 解题思路与参考答案

## 题意

判断数组中是否存在下标 $i \lt j \lt k$ 使 $nums[i] \lt nums[j] \lt nums[k]$。要求严格递增。长度到 $5\cdot 10^5$，进阶要求时间 $O(n)$、额外空间 $O(1)$。

## 思路

我会用贪心，只维护两个变量，这样正好满足进阶要求的 $O(n)$ 时间、$O(1)$ 空间。`first` 是目前见过的最小值，`second` 是「前面有个更小数」的数里最小的那个。扫到 `x` 时，`x <= first` 就更新 `first`；否则 `x <= second` 就更新 `second`；再否则 `x > second`，三元组成立。用 `<=` 更新是为了处理相等值，保证严格递增。

拿 `[2, 1, 5, 0, 4, 6]` 走一遍：2 成为 `first`，1 把 `first` 换小，5 成为 `second`，0 又把 `first` 换成 0，4 比 0 大、不超过 5，`second` 换成 4，最后 6 大于 4，返回真。

面试官很可能追问一句：`first` 更新到 `second` 后面去了，答案还对吗？对。`second` 被赋值时，它前面一定有一个比它小的数；之后 `first` 换小只影响以后的二元组，已有的 `second` 仍带着那个旧的更小前驱。所以 `x > second` 时一定有合法三元组。

另一种做法是预处理前缀最小值和后缀最大值，找中间某个 $j$ 满足 $\text{premin}[j] \lt nums[j] \lt \text{sufmax}[j]$，时间也是 $O(n)$，但空间要 $O(n)$。

## 参考代码

```python
from typing import List


def increasingTriplet(nums: List[int]) -> bool:
    first = second = float("inf")
    for x in nums:
        if x <= first:
            first = x
        elif x <= second:
            second = x
        else:
            return True
    return False


if __name__ == "__main__":
    assert increasingTriplet([1, 2, 3, 4, 5]) is True
    assert increasingTriplet([5, 4, 3, 2, 1]) is False
    assert increasingTriplet([2, 1, 5, 0, 4, 6]) is True
    assert increasingTriplet([20, 100, 10, 12, 5, 13]) is True
    assert increasingTriplet([1, 1, 1, 1]) is False
    assert increasingTriplet([1, 2]) is False
    assert increasingTriplet([1, 1, 2, 2, 3]) is True
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert increasingTriplet([1, 2, 3, 4, 5]) is True
assert increasingTriplet([5, 4, 3, 2, 1]) is False
assert increasingTriplet([2, 1, 5, 0, 4, 6]) is True
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## Edge Cases

- 长度小于 $3$ 时直接不成立，循环走完也会返回假。
- 大量相等值靠 `<=` 更新处理，相等的数不会被当成递增。
- `first` 在 `second` 之后被刷小，比如 `[2, 5, 1, 6]`，`6 > second=5` 仍然正确返回真，对应 `2, 5, 6`。

## 追问

**要返回三个下标怎么办？**
`second` 更新时，同时记下当时 `first` 的下标，作为这对二元组的前驱。命中时返回「记下的前驱、`second` 下标、当前下标」。最新的 `first` 用不了，它可能在 `second` 后面。

```python
def increasingTripletIdx(nums):
    first = second = None
    pair_first = None
    for k, x in enumerate(nums):
        if first is None or x <= nums[first]:
            first = k
        elif second is None or x <= nums[second]:
            second = k
            pair_first = first
        else:
            return [pair_first, second, k]
    return []
```

**推广到长度为 $k$ 的递增子序列呢？**
用 LIS 的贪心数组。`tails[t]` 是长度 $t+1$ 的递增子序列的最小结尾，每个数用 `bisect_left` 替换或追加，长度到 $k$ 就返回真。时间 $O(n\log k)$，额外空间 $O(k)$。本题就是 $k=3$ 时把这个数组展开成两个变量。

```python
from bisect import bisect_left


def increasingK(nums, k):
    tails = []
    for x in nums:
        i = bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
            if len(tails) >= k:
                return True
        else:
            tails[i] = x
    return False
```

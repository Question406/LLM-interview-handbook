---
id: lc-238-product-of-array-except-self
section: array-string
order: 7
level: S
title: LC 238 · 除自身以外数组的乘积
quick: >-
  不能用除法，就用左侧积乘右侧积：第一遍从左往右把每个位置左边的积写进答案，第二遍从右往左用一个变量乘上右边的积。时间 $O(n)$，除答案数组外额外空间 $O(1)$。
tags:
  - Array
  - Prefix Sum
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 238. Product of Array Except Self
    url: https://leetcode.com/problems/product-of-array-except-self/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题目描述

给定整数数组 `nums`，构造同长度的数组 `answer`。其中 `answer[i]` 等于原数组中除下标 i 外的全部元素之积；只排除这一个位置，不是排除所有与 `nums[i]` 相等的值。零和负数都是合法元素。

### 输入与输出

实现 `productExceptSelf(nums) -> List[int]`，返回结果数组。要求运行时间为 O(n)，并且不能使用除法；输入数组不要求被修改。

### 约束

- `2 <= len(nums) <= 10^5`。
- `-30 <= nums[i] <= 30`。
- 题目保证各输出值在32位有符号整数范围内。

### 示例

```text
输入：nums = [1,2,3,4]
输出：[24,12,8,6]
```

[LeetCode 原题](https://leetcode.com/problems/product-of-array-except-self/description/)

## 解题思路与参考答案

## 题意

返回数组 `answer`，`answer[i]` 等于 `nums` 除 `nums[i]` 外所有元素的乘积。不能用除法，时间须 $O(n)$。题目保证任意前缀积、后缀积都在 $32$ 位整数范围内。

## 思路

我会用前后缀积来做：`answer[i]` 就是左边所有数的积乘右边所有数的积，两遍扫描就能凑出来，也顺带避开了除法。开口先跟面试官说一声不用除法，因为数组里有 $0$ 的话，除总积会除零。

拿 `[1, 2, 3, 4]` 走一遍。第一遍从左往右，`answer[i]` 先写成 `nums[0]*...*nums[i-1]`，`i=0` 时左边没有数，记 $1$，得到 `[1, 1, 2, 6]`。第二遍从右往左，用 `right` 记右侧积，先乘进 `answer[i]`，再 `right *= nums[i]`：下标 3 乘 1 得 6，下标 2 乘 4 得 8，下标 1 乘 12 得 12，下标 0 乘 24 得 24，结果是 `[24, 12, 8, 6]`。

有 $0$ 时前缀积照样正确，不用特判：只有一个 $0$ 的话，只有那个位置非零；两个及以上，全是 $0$。

## 参考代码

```python
from typing import List


def productExceptSelf(nums: List[int]) -> List[int]:
    n = len(nums)
    ans = [1] * n
    for i in range(1, n):
        ans[i] = ans[i - 1] * nums[i - 1]
    right = 1
    for i in range(n - 1, -1, -1):
        ans[i] *= right
        right *= nums[i]
    return ans


if __name__ == "__main__":
    assert productExceptSelf([1, 2, 3, 4]) == [24, 12, 8, 6]
    assert productExceptSelf([-1, 1, 0, -3, 3]) == [0, 0, 9, 0, 0]
    assert productExceptSelf([0, 0, 2]) == [0, 0, 0]
    assert productExceptSelf([3, 5]) == [5, 3]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert productExceptSelf([1, 2, 3, 4]) == [24, 12, 8, 6]
assert productExceptSelf([-1, 1, 0, -3, 3]) == [0, 0, 9, 0, 0]
assert productExceptSelf([0, 0, 2]) == [0, 0, 0]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

两遍扫描，时间 $O(n)$。除答案数组外只多了 `right` 一个变量，额外空间 $O(1)$。

## 边界

- 恰好一个 $0$ 时，只有 $0$ 那个位置是其余元素的积，其他位置都是 $0$。
- 两个及以上 $0$ 时，答案全是 $0$。
- 含负数时，符号自然体现在积里，算法不用特判。
- 长度为 $2$ 时，答案就是两个数互换。

## 追问

**如果允许用除法呢？**
先数 $0$ 的个数再分情况。两个及以上 $0$，全部返回 $0$；恰好一个 $0$，只有那个下标填非零元素之积，其余是 $0$；没有 $0$，先算总积再逐个整除。时间 $O(n)$，额外空间 $O(1)$（不含答案）。本题禁用除法，一是有 $0$ 会除零，二是面试想考前缀积。真这么写的时候，整除前确认能整除，有的语言还要留意溢出。

```python
def productExceptSelf_div(nums):
    n = len(nums)
    zeros = sum(x == 0 for x in nums)
    if zeros >= 2:
        return [0] * n
    prod = 1
    for x in nums:
        if x != 0:
            prod *= x
    if zeros == 1:
        return [prod if x == 0 else 0 for x in nums]
    return [prod // x for x in nums]
```

**中间积会溢出吗？**
看语言。LeetCode 保证答案能放进 $32$ 位整数，Python 整数任意精度，直接乘就行。C++/Java 用 `long` 存中间积，最后再转回 `int`；或者仍用左右前缀，每次乘都在题目保证的范围内。别为了防溢出改成取 `log` 再 `exp`，浮点误差可能让答案不准。先问清数据范围再选类型。

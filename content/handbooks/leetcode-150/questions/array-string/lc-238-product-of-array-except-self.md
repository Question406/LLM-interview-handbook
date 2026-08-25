---
id: lc-238-product-of-array-except-self
section: array-string
order: 13
level: S
title: LC 238 · 除自身以外数组的乘积
quick: >-
  不能用除法。我先从左往右把左侧前缀积写入答案，再从右往左乘上右侧积。时间 $O(n)$，额外空间 $O(1)$（不含答案数组）。
tags:
  - Array
  - Prefix
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 238. 除自身以外数组的乘积
    url: https://leetcode.cn/problems/product-of-array-except-self/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

返回数组 `answer`，`answer[i]` 等于 `nums` 除 `nums[i]` 外所有元素的乘积。不能用除法，时间须 $O(n)$。

## 思路

`answer[i] = 左侧积 × 右侧积`。第一遍从左扫，`answer[i]` 先写成 `nums[0]*...*nums[i-1]`（`i=0` 为 $1$）。第二遍从右扫，维护右侧积 `right`，乘进 `answer[i]` 后再 `right *= nums[i]`。

有 $0$ 时除法会炸，前缀积照样正确：一个 $0$ 则只有该位置非零；两个及以上全零。白板我会先声明「不用除法」。

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
    print("ok")
```

## 复杂度

时间 $O(n)$。除答案数组外额外空间 $O(1)$。

## 边界

- 恰好一个 $0$：只有 $0$ 那个位置是其余积，其他全 $0$。
- 两个及以上 $0$：答案全 $0$。
- 含负数：符号会反映在积里，算法不用特判。
- 长度为 $2$：答案就是彼此互换。

## 追问

- **允许用除法？** 先数 $0$ 的个数。$\ge 2$ 个 $0$，全返回 $0$。恰好一个 $0$，只有该下标填「非零元素之积」，其余为 $0$。没有 $0$，先算总积再逐个整除。时间 $O(n)$，额外空间 $O(1)$（不含答案）。本题禁用除法，是因为有 $0$ 会除零，以及面试想考前缀积。整除前确认能整除；语言里注意溢出。

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

- **中间积会溢出？** LeetCode 保证答案能放进 $32$ 位整数，Python 整数任意精度，直接乘即可。C++/Java 要用 `long` 存中间积，最后再转回 `int`；或者仍用左右前缀、每次乘都在题保证的范围内。不要为了防溢出改用 `log` 再 `exp`，精度会炸。白板我会先问清数据范围再选类型。

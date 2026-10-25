---
id: lc-238-product-of-array-except-self
section: array-string
order: 13
level: S
title: LC 238 · 除自身以外数组的乘积
quick: "不用除法，用左右前缀积：先从左往右把左侧积写进答案，再从右往左乘上右侧积，`answer[i]` 就是两者的乘积，有 $0$ 也不用特判。时间 $O(n)$，额外空间 $O(1)$（不含答案数组）。"
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

## 题目描述

给定整数数组 `nums`，构造同长度数组 `answer`。对于每个位置 i，`answer[i]` 是原数组中除了位置 i 以外的所有元素的乘积。即使两个位置存放相同的数，也只排除当前位置这一个元素；输入可以包含零和负数。

### 输入与输出

实现 `productExceptSelf(nums) -> List[int]`，返回整个结果数组。要求总时间为 O(n)，不能使用除法；不要求修改输入。

### 约束

- `2 <= len(nums) <= 10^5`。
- `-30 <= nums[i] <= 30`。
- 题目保证每个输出值可由32位有符号整数表示。

### 示例

```text
输入：nums = [1,2,3,4]
输出：[24,12,8,6]
```

[LeetCode 原题](https://leetcode.com/problems/product-of-array-except-self/description/)

## 解题思路与参考答案

## 题意

返回数组 `answer`，`answer[i]` 等于 `nums` 除 `nums[i]` 外所有元素的乘积。不能用除法，时间须 $O(n)$。

## 思路

我会用前缀积，因为 `answer[i] = 左侧积 × 右侧积`，完全不用除法，开口先声明这一点。第一遍从左扫，`answer[i]` 先写成 `nums[0]*...*nums[i-1]`（`i=0` 时为 $1$）；第二遍从右扫，维护右侧积 `right`，乘进 `answer[i]` 之后再 `right *= nums[i]`。

拿 `[1, 2, 3, 4]` 走一遍：第一遍得到左侧积 `[1, 1, 2, 6]`；第二遍从右往左，`right` 依次是 $1$、$4$、$12$、$24$，乘进去得到 `[24, 12, 8, 6]`。

有 $0$ 时没法直接用总积相除，前缀积照样正确：只有一个 $0$ 时，只有那个位置非零；两个及以上就全是零。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert productExceptSelf([1, 2, 3, 4]) == [24, 12, 8, 6]
assert productExceptSelf([-1, 1, 0, -3, 3]) == [0, 0, 9, 0, 0]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$。除答案数组外额外空间 $O(1)$。

## 边界

恰好一个 $0$ 时，只有 $0$ 所在位置是其余元素的积，其他全是 $0$。两个及以上 $0$，答案全 $0$。含负数时符号自然反映在积里，算法不用特判。长度为 $2$ 时答案就是两个数互换。

## 追问

**允许用除法呢？**
先数 $0$ 的个数。$\ge 2$ 个 $0$ 就全返回 $0$；恰好一个 $0$，只有那个下标填非零元素之积，其余是 $0$；没有 $0$ 就先算总积再逐个整除。时间 $O(n)$，额外空间 $O(1)$（不含答案）。本题禁用除法，一是有 $0$ 会除零，二是面试想考前缀积。整除前确认能整除，用定长整数的语言还要留意溢出。

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
先问清数据范围再选类型。LeetCode 保证答案能放进 $32$ 位整数，Python 整数任意精度，直接乘就行。C++/Java 要用 `long` 存中间积，最后再转回 `int`；或者仍用左右前缀，每次乘都在题目保证的范围内。别为了防溢出改用 `log` 再 `exp`，会产生精度误差。

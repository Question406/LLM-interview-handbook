---
id: lc-136-single-number
section: bit
order: 4
level: S
title: LC 136 · 只出现一次的数字
quick: >-
  其余都出现两次。全部 XOR：$a\oplus a=0$、$a\oplus 0=a$，成对抵消，剩下那个。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Bit
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 136. 只出现一次的数字
    url: https://leetcode.cn/problems/single-number/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

数组里除一个元素外，其余都恰好出现两次。找出只出现一次的那个。线性时间、常数额外空间。

## 思路

异或满足交换律、结合律，$x\oplus x=0$，$x\oplus 0=x$。所有数 XOR 一遍，成对的变 $0$，只剩单身那个。

哈希计数要 $O(n)$ 空间。排序后看邻居，$O(n\log n)$。面试里 XOR 是首选。

## 参考代码

```python
from typing import List


def singleNumber(nums: List[int]) -> int:
    x = 0
    for v in nums:
        x ^= v
    return x


if __name__ == "__main__":
    assert singleNumber([2, 2, 1]) == 1
    assert singleNumber([4, 1, 2, 1, 2]) == 4
    assert singleNumber([1]) == 1
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- $n=1$：数组只有单身那个，XOR 初值 $0$ 异或它就是它。
- 单身在开头 / 结尾：XOR 可交换、可结合，位置不影响结果。
- 含负数：补码下 XOR 同样成立，不必先转无符号。

## 追问

- **两个单身、其余两次（LC 260）？** 全体 XOR 得 `diff = a^b`。`diff` 至少有一位是 $1$，取最低的 `mask = diff & -diff`。按该位把数组分成两组：该位为 $1$ 的一组、为 $0$ 的一组。每组里除一个单身外都成对，组内再 XOR 各得一个单身。时间 $O(n)$，额外空间 $O(1)$。

```python
def singleNumberTwo(nums):
    diff = 0
    for x in nums:
        diff ^= x
    mask = diff & -diff
    a = b = 0
    for x in nums:
        if x & mask:
            a ^= x
        else:
            b ^= x
    return [a, b]
```

- **其余出现三次（LC 137）？** 普通 XOR 只能消偶数次。每位上统计 $1$ 的个数模 $3$，余数就是单身那一位；或用 `ones`/`twos` 状态机：`ones = (ones ^ x) & ~twos`，`twos = (twos ^ x) & ~ones`，同一比特出现三次后两者归零，答案是 `ones`。时间 $O(n)$，额外空间 $O(1)$。独立卡见 `lc-137-single-number-ii`。

```python
def singleNumberThree(nums):
    ones = twos = 0
    for x in nums:
        ones = (ones ^ x) & ~twos
        twos = (twos ^ x) & ~ones
    return ones
```

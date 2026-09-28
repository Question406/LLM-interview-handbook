---
id: lc-136-single-number
section: bit
order: 2
level: S
title: LC 136 · 只出现一次的数字
quick: >-
  其余都出现两次。全部 XOR：$a\oplus a=0$、$a\oplus 0=a$，成对抵消，剩下的就是答案。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Bit
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 136. Single Number
    url: https://leetcode.com/problems/single-number/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

非空整数数组里，除一个元素外其余都恰好出现两次。找出只出现一次的那个。要求线性时间、常数额外空间。

## 思路

异或满足交换律、结合律，$x\oplus x=0$，$x\oplus 0=x$。所有数 XOR 一遍，成对的变 $0$，只剩单身那个，和出现顺序无关。

哈希计数要 $O(n)$ 空间；排序后看邻居要 $O(n\log n)$；「$2\times$ 去重和 $-$ 总和」要额外集合，大数时还要担心溢出。面试里 XOR 是首选。

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
    assert singleNumber([-3, 5, 5]) == -3
    assert singleNumber([0, 7, 7]) == 0
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- $n=1$：XOR 初值 $0$ 异或它就是它。
- 单身在开头 / 结尾：XOR 可交换，位置不影响结果。
- 含负数或 $0$：补码下 XOR 同样成立；答案是 $0$ 时也能正确返回。

## 追问

- **两个单身、其余两次（LC 260）？** 全体 XOR 得 `diff = a ^ b`，`diff` 至少有一位是 $1$，取最低的 `mask = diff & -diff`。按这一位把数组分两组，每组里只有一个单身，组内再 XOR。时间 $O(n)$，额外空间 $O(1)$。

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

- **其余出现三次（LC 137）？** XOR 只能消偶数次。按位统计 $1$ 的个数模 $3$，余数就是单身在该位的值；或用 `ones` / `twos` 状态机，同一比特出现三次后两者归零，答案是 `ones`。

```python
def singleNumberThree(nums):
    ones = twos = 0
    for x in nums:
        ones = (ones ^ x) & ~twos
        twos = (twos ^ x) & ~ones
    return ones
```

---
id: lc-137-single-number-ii
section: bit
order: 5
level: A
title: LC 137 · 只出现一次的数字 II
quick: >-
  其余都出现三次。每位上 $1$ 的个数模 $3$，或用 `ones`/`twos` 记出现 $1$ 次、$2$ 次的比特。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Bit
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 137. 只出现一次的数字 II
    url: https://leetcode.cn/problems/single-number-ii/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

除一个元素外，其余都恰好出现三次。找出只出现一次的那个。线性时间、常数额外空间。

## 思路

每位独立：出现三次的比特贡献是 $3$ 的倍数，模 $3$ 剩下的就是单身那一位。Python 整数无限长，符号位不用单独处理。

状态机更短：`ones` 是「模 $3$ 余 $1$」的比特，`twos` 是「余 $2$」。转移 `ones = (ones ^ x) & ~twos`，`twos = (twos ^ x) & ~ones`。三次同一比特后两者都回到 $0$。

普通 XOR 只能消两次，这里不能直接用。

## 参考代码

```python
from typing import List


def singleNumber(nums: List[int]) -> int:
    ones = twos = 0
    for x in nums:
        ones = (ones ^ x) & ~twos
        twos = (twos ^ x) & ~ones
    return ones


if __name__ == "__main__":
    assert singleNumber([2, 2, 3, 2]) == 3
    assert singleNumber([0, 1, 0, 1, 0, 1, 99]) == 99
    assert singleNumber([-2, -2, 1, -2]) == 1
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。按位统计则是 $O(32n)$。

## 边界

- 单身是 $0$：`ones` 最终为 $0$，合法。
- 单身是负数：Python 整数无限长，状态机对补码比特同样有效。
- 单身在开头：扫描顺序无关，三次出现的数会把状态清回 $0$。

## 追问

- **出现 $k$ 次、单身出现一次？** 每位独立计数：对第 $b$ 位把所有数该位之和模 $k$，余数就是单身该位。$k=3$ 时就是本题。也可用 $k-1$ 个状态变量模拟模 $k$ 计数器。时间 $O(32n)$。Python 要把第 $31$ 位还原成符号。

```python
def singleNumberK(nums, k):
    ans = 0
    for b in range(32):
        s = sum((x >> b) & 1 for x in nums) % k
        if s:
            ans |= 1 << b
    if ans >= 1 << 31:
        ans -= 1 << 32
    return ans
```

- **两个单身、其余两次（LC 260）？** 先全体 XOR 得 `diff = a^b`，用最低不同位 `mask = diff & -diff` 把数组拆成两组，各组再 XOR。时间 $O(n)$，额外空间 $O(1)$。不能套本题的模 $3$ 状态机：出现两次的比特模 $3$ 余 $2$，两个单身会混在一起。

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

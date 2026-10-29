---
id: lc-136-single-number
section: bit
order: 2
level: S
title: LC 136 · 只出现一次的数字
quick: >-
  全部 XOR 一遍：$a\oplus a=0$、$a\oplus 0=a$，出现两次的数成对抵消，剩下的就是只出现一次的那个。时间 $O(n)$，额外空间
  $O(1)$。
tags:
  - Bit
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 136. Single Number
    url: 'https://leetcode.com/problems/single-number/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定非空整数数组 `nums`，其中恰好有一个数只出现一次，其他每个不同的数都恰好出现两次。找出那个只出现一次的数。负数和0也可能出现，要求依据出现次数而不是数值大小判断。

### 输入与输出

实现 `singleNumber(nums) -> int`，返回该数的值，不是下标。要求时间为 O(n)，额外空间为 O(1)。

### 约束

- `1 <= len(nums) <= 3 * 10^4`。
- `-3 * 10^4 <= nums[i] <= 3 * 10^4`。
- 输入保证满足“一个数一次、其他数两次”的出现次数条件。

### 示例

```text
输入：nums = [2,2,1]
输出：1
```

[LeetCode 原题](https://leetcode.com/problems/single-number/description/)

## 解题思路与参考答案

## 题意

非空整数数组里，除一个元素外其余都恰好出现两次。找出只出现一次的那个。要求线性时间、常数额外空间。

## 思路

我会把所有数异或起来，成对的数会互相抵消，线性时间、常数空间都满足。异或满足交换律、结合律，$x\oplus x=0$，$x\oplus 0=x$，所以和出现顺序无关，成对的变 $0$，只剩出现一次的数。

拿 `[4, 1, 2, 1, 2]` 看，重新排一下就是 $4\oplus(1\oplus 1)\oplus(2\oplus 2)=4\oplus 0\oplus 0=4$。

其他做法都差一点。哈希计数要 $O(n)$ 空间；排序后看邻居要 $O(n\log n)$；「$2\times$ 去重和 $-$ 总和」要额外集合，大数时还要担心溢出。面试里首选 XOR。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert singleNumber([2, 2, 1]) == 1
assert singleNumber([4, 1, 2, 1, 2]) == 4
assert singleNumber([1]) == 1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## Edge Cases

- $n=1$ 时，初值 $0$ 异或它就是它。
- 只出现一次的数在开头还是结尾都一样，XOR 可交换，位置不影响结果。
- 含负数或 $0$ 时，补码下 XOR 同样成立；答案是 $0$ 也能正确返回。

## 追问

**两个数各出现一次、其余各出现两次（LC 260）呢？**
先全体 XOR 得到 `diff = a ^ b`，`diff` 至少有一位是 $1$，取最低的那位 `mask = diff & -diff`。按这一位把数组分成两组，每组里只有一个只出现一次的数，组内再 XOR。时间 $O(n)$，额外空间 $O(1)$。

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

**其余出现三次（LC 137）呢？**
XOR 只能消掉偶数次，得换办法。按位统计 $1$ 的个数模 $3$，余数就是答案在该位的值；或者用 `ones` / `twos` 状态机，同一比特出现三次后两者归零，答案是 `ones`。

```python
def singleNumberThree(nums):
    ones = twos = 0
    for x in nums:
        ones = (ones ^ x) & ~twos
        twos = (twos ^ x) & ~ones
    return ones
```

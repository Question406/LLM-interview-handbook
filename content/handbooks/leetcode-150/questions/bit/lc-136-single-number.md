---
id: lc-136-single-number
section: bit
order: 4
level: S
title: LC 136 · 只出现一次的数字
quick: "把所有数异或一遍：$a\\oplus a=0$、$a\\oplus 0=a$，成对出现的数互相抵消，剩下的就是只出现一次的那个。时间 $O(n)$，额外空间 $O(1)$。"
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

## 题目描述

给定非空整数数组 nums。其中恰有一个元素出现一次，其余每种元素都恰好出现两次。找出并返回只出现一次的那个值。

### 接口与输出

实现 `singleNumber(nums: List[int]) -> int`。要求线性时间和常数额外空间；返回元素的值，不是下标。

### 合法输入与约束

`1 <= len(nums) <= 30000`，`-30000 <= nums[i] <= 30000`。输入保证满足“一种元素出现一次，其余各出现两次”的条件。

### 示例

```text
输入：nums = [2,2,1]
输出：1
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/single-number/description/)。

## 解题思路与参考答案

## 题意

数组里除了一个元素，其余都恰好出现两次，找出只出现一次的那个。要求线性时间、常数额外空间。

## 思路

我会直接用异或，因为它满足交换律和结合律，而且 $x\oplus x=0$、$x\oplus 0=x$。所有数异或一遍，成对的变成 $0$，只剩单身那个。

比如 `[4, 1, 2, 1, 2]`，顺序无所谓，可以看成 $4\oplus(1\oplus 1)\oplus(2\oplus 2)=4\oplus 0\oplus 0=4$。

其他做法也可以顺带说一句：哈希计数要 $O(n)$ 空间，排序后看邻居是 $O(n\log n)$。面试里首选异或。

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

## 边界

$n=1$ 时数组里只有单身那个，异或初值 $0$ 和它异或就是它。单身在开头还是结尾都不影响，异或可交换、可结合。含负数也没问题，补码下异或同样成立，不用先转无符号。

## 追问

**有两个单身、其余都出现两次（LC 260）怎么办？**
先全体异或得到 `diff = a^b`。`diff` 至少有一位是 $1$，取最低的那位 `mask = diff & -diff`，按这一位把数组分成两组：该位为 $1$ 的一组，为 $0$ 的一组。每组里除了一个单身都成对，组内再各自异或，就分别得到两个单身。时间 $O(n)$，额外空间 $O(1)$。

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
普通异或只能消掉偶数次。可以在每一位上统计 $1$ 的个数模 $3$，余数就是单身那一位；也可以用 `ones`/`twos` 状态机：`ones = (ones ^ x) & ~twos`，`twos = (twos ^ x) & ~ones`，同一比特出现三次后两者归零，答案是 `ones`。时间 $O(n)$，额外空间 $O(1)$。独立卡见 `lc-137-single-number-ii`。

```python
def singleNumberThree(nums):
    ones = twos = 0
    for x in nums:
        ones = (ones ^ x) & ~twos
        twos = (twos ^ x) & ~ones
    return ones
```

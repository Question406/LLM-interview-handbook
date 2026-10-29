---
id: lc-137-single-number-ii
section: bit
order: 5
level: A
title: LC 137 · 只出现一次的数字 II
quick: >-
  其余数都出现三次，所以每一位上 $1$ 的个数模 $3$ 就是单身在那一位的值；更短的写法是用 `ones`/`twos` 记出现 $1$ 次、$2$
  次的比特，出现三次自动清零。时间 $O(n)$，额外空间 $O(1)$。
tags:
  - Bit
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 137. 只出现一次的数字 II
    url: 'https://leetcode.cn/problems/single-number-ii/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定非空整数数组，恰好一个数出现一次，其他每个数都恰好出现三次。找出并返回只出现一次的数，重复元素的相对位置没有任何保证。

### 输入与输出

实现 `singleNumber(nums) -> int`。输入可包含负数，返回这个唯一的单次出现值。

### 约束与约定

- `1 <= len(nums) <= 30000`。
- 所有数均在 32 位有符号整数范围内。
- 要求线性时间、常数额外空间。

### 示例

```text
输入：nums = [2,2,3,2]
输出：3
```

示例中的 2 出现三次，只有 3 出现一次。

[官方原题与完整题面](https://leetcode.com/problems/single-number-ii/description/)。

## 解题思路与参考答案

## 题意

除了一个元素，其余都恰好出现三次，找出只出现一次的那个。要求线性时间、常数额外空间。

## 思路

普通异或只能消掉偶数次，这里用不了，我会改成按位计数。每个二进制位独立看：重复的数都出现三次，它们对这一位的贡献是 $3$ 的倍数，计数模 $3$ 后剩下的就是单身在这一位的值。Python 整数无限长，符号位不用单独处理。

比如 `[2, 2, 3, 2]`：$2$ 是 `10`，$3$ 是 `11`。最低位上只有 $3$ 贡献了一个 $1$，模 $3$ 余 $1$；第二位上四个数都是 $1$，一共 $4$ 个，模 $3$ 余 $1$。两位都是 $1$，答案 `11`，也就是 $3$。

代码里用的是更短的状态机。`ones` 记录「出现次数模 $3$ 余 $1$」的比特，`twos` 记录「余 $2$」的比特，转移是 `ones = (ones ^ x) & ~twos`，`twos = (twos ^ x) & ~ones`。同一个比特出现三次之后，两者都回到 $0$。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert singleNumber([2, 2, 3, 2]) == 3
assert singleNumber([0, 1, 0, 1, 0, 1, 99]) == 99
assert singleNumber([-2, -2, 1, -2]) == 1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。按位统计的写法是 $O(32n)$。

## Edge Cases

单身是 $0$ 时，`ones` 最终为 $0$，结果正确。单身是负数时，Python 整数无限长，状态机对补码比特同样有效。单身在开头也没关系，扫描顺序无关，出现三次的数会把状态清回 $0$。

## 追问

**推广到其余出现 $k$ 次、单身出现一次呢？**
还是每位独立计数：对第 $b$ 位，把所有数这一位的值加起来模 $k$，余数就是单身这一位，$k=3$ 时就是本题。也可以用 $k-1$ 个状态变量模拟一个模 $k$ 计数器。时间 $O(32n)$。Python 里要把第 $31$ 位还原成符号。

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

**两个单身、其余出现两次（LC 260）能套这个状态机吗？**
不能。出现两次的比特模 $3$ 余 $2$，两个单身会混在一起。这题要先全体异或得到 `diff = a^b`，用最低的不同位 `mask = diff & -diff` 把数组拆成两组，各组再异或。时间 $O(n)$，额外空间 $O(1)$。

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

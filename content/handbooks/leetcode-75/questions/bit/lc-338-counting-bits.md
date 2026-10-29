---
id: lc-338-counting-bits
section: bit
order: 1
level: A
title: LC 338 · 比特位计数
quick: >-
  用 DP 递推：$ans[i]=ans[i\gg 1]+(i\,\&\,1)$，右移一位的数已经算过，再补上最低位。也可以用
  $ans[i]=ans[i\,\&\,(i-1)]+1$，去掉最低位的 $1$。时间 $O(n)$，额外空间 $O(1)$（不计输出）。
tags:
  - Bit
  - DP
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 338. Counting Bits
    url: 'https://leetcode.com/problems/counting-bits/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定非负整数 n，依次统计从 0 到 n 的每个整数在二进制表示中含有多少个 1，并把这些计数组成数组。

### 输入与输出

实现 `countBits(n: int) -> List[int]`。返回长度 n+1 的数组 ans，其中 ans[i] 是整数 i 的 1 位数量，顺序必须与整数从小到大对应。

### 约束

- `0 <= n <= 10^5`。
- 进阶要求 O(n) 时间，并且不直接对每个数调用语言内置的位计数函数。

### 示例

```text
输入：n = 2
输出：[0,1,1]
```

0、1、2 的二进制分别为 0、1、10，对应计数为 `[0,1,1]`。

## 解题思路与参考答案

## 题意

给整数 $n$（$0\le n\le 10^5$），返回长度 $n+1$ 的数组 `ans`，`ans[i]` 是 $i$ 的二进制表示里 $1$ 的个数。进阶要求线性时间、不用内置 popcount。

## 思路

我会用 DP 递推，每个数都能从一个更小、已经算过的数一步转移过来。把 $i$ 右移一位得到 $i\gg 1$，它比 $i$ 小，答案已经在表里；两者的 $1$ 个数只差被移掉的最低位。所以 $ans[i]=ans[i\gg 1]+(i\,\&\,1)$，从 $1$ 递推到 $n$。

拿 $n=5$ 走一遍：$ans[1]=ans[0]+1=1$，$ans[2]=ans[1]+0=1$，$ans[3]=ans[1]+1=2$，$ans[4]=ans[2]+0=1$，$ans[5]=ans[2]+1=2$，得到 `[0, 1, 1, 2, 1, 2]`。

另一种转移是 $i\,\&\,(i-1)$，它把 $i$ 最低位的 $1$ 清掉，结果也比 $i$ 小，所以 $ans[i]=ans[i\,\&\,(i-1)]+1$。两种都是 $O(1)$ 转移。逐个数去数位是 $O(n\log n)$，能过，但不满足进阶要求。

## 参考代码

```python
from typing import List


def countBits(n: int) -> List[int]:
    ans = [0] * (n + 1)
    for i in range(1, n + 1):
        ans[i] = ans[i >> 1] + (i & 1)
    return ans


if __name__ == "__main__":
    assert countBits(2) == [0, 1, 1]
    assert countBits(5) == [0, 1, 1, 2, 1, 2]
    assert countBits(0) == [0]
    assert countBits(1) == [0, 1]
    res = countBits(1000)
    assert all(res[i] == bin(i).count("1") for i in range(1001))
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert countBits(2) == [0, 1, 1]
assert countBits(5) == [0, 1, 1, 2, 1, 2]
assert countBits(0) == [0]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$，输出数组 $O(n)$ 不计。

## Edge Cases

- $n=0$ 时返回 `[0]`，循环不进。
- $2$ 的幂只有一个 $1$，由 $ans[i\gg 1]$ 一路继承到 $ans[1]=1$。
- $2^k-1$ 全是 $1$，答案是 $k$，可以用来自检。

## 追问

**只求单个数的 $1$ 个数（LC 191）呢？**
反复 `x &= x - 1`，每次清掉最低位的 $1$，循环次数就是答案，比逐位右移快。

```python
def hammingWeight(x):
    cnt = 0
    while x:
        x &= x - 1
        cnt += 1
    return cnt
```

**按最高位分段怎么递推？**
维护不超过 $i$ 的最大 $2$ 的幂 `high`，$ans[i]=ans[i-high]+1$。$i$ 是 $2$ 的幂时更新 `high`，判断用 $i\,\&\,(i-1)=0$。

```python
def countBitsHigh(n):
    ans = [0] * (n + 1)
    high = 0
    for i in range(1, n + 1):
        if i & (i - 1) == 0:
            high = i
        ans[i] = ans[i - high] + 1
    return ans
```

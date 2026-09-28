---
id: lc-338-counting-bits
section: bit
order: 1
level: A
title: LC 338 · 比特位计数
quick: >-
  $ans[i]=ans[i\gg 1]+(i\,\&\,1)$：右移一位的数已经算过，再补上最低位。也可用 $ans[i]=ans[i\,\&\,(i-1)]+1$ 去掉最低位的 $1$。时间
  $O(n)$，额外空间 $O(1)$（不计输出）。
tags:
  - Bit
  - DP
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 338. Counting Bits
    url: https://leetcode.com/problems/counting-bits/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

给整数 $n$（$0\le n\le 10^5$），返回长度 $n+1$ 的数组 `ans`，`ans[i]` 是 $i$ 的二进制表示里 $1$ 的个数。进阶要求线性时间、不用内置 popcount。

## 思路

把 $i$ 右移一位得到 $i\gg 1$，它比 $i$ 小，答案已经在表里；两者的 $1$ 个数只差被移掉的最低位。所以 $ans[i]=ans[i\gg 1]+(i\,\&\,1)$，从 $1$ 递推到 $n$。

另一种转移是 $i\,\&\,(i-1)$：它把 $i$ 最低位的 $1$ 清掉，结果也比 $i$ 小，$ans[i]=ans[i\,\&\,(i-1)]+1$。两种都是 $O(1)$ 转移。逐个数去数位是 $O(n\log n)$，能过但不满足进阶要求。

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

## 复杂度

时间 $O(n)$，额外空间 $O(1)$，输出数组 $O(n)$ 不计。

## 边界

- $n=0$：返回 `[0]`，循环不进。
- $2$ 的幂：只有一个 $1$，由 $ans[i\gg 1]$ 一路继承到 $ans[1]=1$。
- $2^k-1$：全 $1$，答案 $k$，可用来自检。

## 追问

- **只求单个数的 $1$ 个数（LC 191）？** 反复 `x &= x - 1`，每次清掉最低位的 $1$，循环次数等于答案，比逐位右移快。

```python
def hammingWeight(x):
    cnt = 0
    while x:
        x &= x - 1
        cnt += 1
    return cnt
```

- **按最高位分段怎么递推？** 维护当前不超过 $i$ 的最大 $2$ 的幂 `high`，$ans[i]=ans[i-high]+1$。$i$ 是 $2$ 的幂时更新 `high`，判断用 $i\,\&\,(i-1)=0$。

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

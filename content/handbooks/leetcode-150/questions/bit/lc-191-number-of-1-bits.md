---
id: lc-191-number-of-1-bits
section: bit
order: 3
level: S
title: LC 191 · 位1的个数
quick: >-
  `n & (n - 1)` 清掉最低的 $1$，循环直到 $n=0$，次数即汉明重量。时间与 $1$ 的个数成正比。
tags:
  - Bit
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 191. 位1的个数
    url: https://leetcode.cn/problems/number-of-1-bits/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

返回无符号整数二进制表示中 $1$ 的个数（汉明重量）。

## 思路

`n & (n - 1)` 会把最低置位的 $1$ 清掉，其余位不变。循环到 $0$，循环次数等于 $1$ 的个数。

逐位右移也可以，固定 $32$ 次。白板我优先讲清这个位运算。Python 的 `n.bit_count()` 能过，但要会手写。

## 参考代码

```python
def hammingWeight(n: int) -> int:
    cnt = 0
    while n:
        n &= n - 1
        cnt += 1
    return cnt


if __name__ == "__main__":
    assert hammingWeight(11) == 3
    assert hammingWeight(128) == 1
    assert hammingWeight(0) == 0
    assert hammingWeight((1 << 32) - 1) == 32
    print("ok")
```

## 复杂度

时间 $O(k)$，$k$ 为 $1$ 的个数，最坏 $O(32)$。额外空间 $O(1)$。

## 边界

- $n=0$：循环不进，答案 $0$。
- 只有最高位是 $1$：`n & (n-1)` 一次就清掉，答案 $1$。
- 全 $1$（$2^{32}-1$）：循环 $32$ 次。

## 追问

- **汉明距离（LC 461）？** 两数 XOR 后，不同比特变成 $1$，再数 $1$ 的个数。时间与不同位数成正比。

```python
def hammingDistance(x, y):
    n, cnt = x ^ y, 0
    while n:
        n &= n - 1
        cnt += 1
    return cnt
```

- **区间 $[0,n]$ 内一共有多少个 $1$？** 不要对每个数调本题。第 $b$ 位以 $2^{b+1}$ 为周期，每周期前一半是 $0$、后一半是 $1$。对 $n+1$ 计完整周期再加余数。也可数位 DP。

```python
def countBitsRange(n):
    n += 1
    ans, b = 0, 1
    while b < n:
        cycle = b << 1
        ans += (n // cycle) * b + max(0, n % cycle - b)
        b <<= 1
    return ans
```

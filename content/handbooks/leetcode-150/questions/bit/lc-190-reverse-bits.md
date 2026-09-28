---
id: lc-190-reverse-bits
section: bit
order: 2
level: A
title: LC 190 · 颠倒二进制位
quick: >-
  固定 $32$ 位。循环 $32$ 次：`ans` 左移一位，接上 `n` 的最低位，再把
  `n` 右移。时间 $O(1)$。
tags:
  - Bit
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 190. 颠倒二进制位
    url: https://leetcode.cn/problems/reverse-bits/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

把 $32$ 位无符号整数的比特整体颠倒，返回颠倒后的值。高位不足要补零，低位的 $1$ 会变成高位。

## 思路

从低到高吐位、从高到低装填。每次 `ans = (ans << 1) | (n & 1)`，然后 `n >>= 1`，固定做 $32$ 轮。不要按「有效比特」提前停，否则高位的 $0$ 丢了。

分治交换（16、8、4、2、1 位成对换）也能 $O(1)$，常数更小，提一句即可。

## 参考代码

```python
def reverseBits(n: int) -> int:
    ans = 0
    for _ in range(32):
        ans = (ans << 1) | (n & 1)
        n >>= 1
    return ans


if __name__ == "__main__":
    assert reverseBits(0) == 0
    assert reverseBits(1) == 1 << 31
    assert reverseBits(43261596) == 964176192
    print("ok")
```

## 复杂度

时间 $O(1)$（$32$ 次），额外空间 $O(1)$。

## 边界

- $n=0$：固定 $32$ 轮后仍是 $0$。
- $n=1$：最低位翻到最高位，结果是 $2^{31}$。
- 最高位已是 $1$：会翻到最低位；不要按有符号数提前停，高位的 $0$ 也要占位。

## 追问

- **不定长比特？** 先约定宽度 $w$（或用 `n.bit_length()`），循环 $w$ 次而不是写死 $32$。宽度不足时左边补零，逻辑与本题相同。

```python
def reverseBitsVar(n, width=None):
    if width is None:
        width = max(n.bit_length(), 1)
    ans = 0
    for _ in range(width):
        ans = (ans << 1) | (n & 1)
        n >>= 1
    return ans
```

- **字节翻转？** 把 $32$ 位拆成 $4$ 个字节，字节顺序反过来，每个字节内部用 $256$ 项表翻转。适合反复调用，把 $32$ 次位移收成 $4$ 次查表。

```python
TABLE = [int(f"{i:08b}"[::-1], 2) for i in range(256)]

def reverseBitsBytes(n):
    b0 = TABLE[n & 255]
    b1 = TABLE[(n >> 8) & 255]
    b2 = TABLE[(n >> 16) & 255]
    b3 = TABLE[(n >> 24) & 255]
    return (b0 << 24) | (b1 << 16) | (b2 << 8) | b3
```

---
id: lc-1318-minimum-flips-to-make-a-or-b-equal-to-c
section: bit
order: 3
level: A
title: LC 1318 · 或运算的最小翻转次数
quick: >-
  各位独立。$c$ 该位为 $1$：$a,b$ 都是 $0$ 才要翻 $1$ 次；$c$ 该位为 $0$：$a,b$ 里有几个 $1$ 就翻几次。一行写法是
  $\mathrm{popcount}((a|b)\oplus c)+\mathrm{popcount}(a\,\&\,b\,\&\,\lnot c)$。时间 $O(\log C)$，额外空间 $O(1)$。
tags:
  - Bit
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1318. Minimum Flips to Make a OR b Equal to c
    url: https://leetcode.com/problems/minimum-flips-to-make-a-or-b-equal-to-c/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

三个正整数 $a$、$b$、$c$（都不超过 $10^9$）。一次翻转是把 $a$ 或 $b$ 二进制里的某一位 $0\leftrightarrow 1$。求最少翻转几次，使 $a\,|\,b=c$。

## 思路

按位或没有进位，每一位互不影响，所以逐位求最少翻转再相加就是全局最优。看第 $i$ 位，记 $x, y, z$ 为 $a, b, c$ 在这一位的值：

- $z=1$：只要 $x, y$ 有一个是 $1$ 就满足；两个都是 $0$ 时翻任意一个，代价 $1$。
- $z=0$：$x, y$ 都必须是 $0$，代价是 $x+y$。

扫到 $a, b, c$ 都变成 $0$ 为止，最多 $30$ 位。位运算合并写法：$(a|b)\oplus c$ 标出所有不符合的位，每位至少翻一次；其中 $c$ 为 $0$ 且 $a, b$ 都是 $1$ 的位要翻两次，用 $a\,\&\,b\,\&\,\lnot c$ 再补上。

## 参考代码

```python
def minFlips(a: int, b: int, c: int) -> int:
    flips = 0
    while a or b or c:
        x, y, z = a & 1, b & 1, c & 1
        if z:
            flips += 1 if x == 0 and y == 0 else 0
        else:
            flips += x + y
        a >>= 1
        b >>= 1
        c >>= 1
    return flips


if __name__ == "__main__":
    assert minFlips(2, 6, 5) == 3
    assert minFlips(4, 2, 7) == 1
    assert minFlips(1, 2, 3) == 0
    assert minFlips(1, 1, 1) == 0
    assert minFlips(7, 7, 0) == 6
    assert minFlips(8, 3, 5) == 3
    print("ok")
```

## 复杂度

时间 $O(\log C)$，$C=\max(a,b,c)$，最多约 $30$ 轮。额外空间 $O(1)$。

## 边界

- 已经满足 $a\,|\,b=c$：每位代价都是 $0$。
- $c$ 的某位是 $0$ 而 $a, b$ 该位都是 $1$：要翻两次，只算 $1$ 是常见错误。
- 三个数位数不同：循环条件用 `a or b or c`，保证较长的那个数的高位也被检查。

## 追问

- **不写循环，一行位运算？** 前一项数出所有不符合的位，后一项给「要翻两次」的位补一次。Python 里 `~c` 是负数，但和非负的 `a & b` 相与后结果非负，`bin().count` 没问题。

```python
def minFlipsOneLine(a, b, c):
    return bin((a | b) ^ c).count("1") + bin(a & b & ~c).count("1")
```

- **改成 $a\,\&\,b=c$？** 同样逐位：$z=1$ 时 $x, y$ 都要是 $1$，代价 $(1-x)+(1-y)$；$z=0$ 时只要有一个 $0$，两者都是 $1$ 才翻 $1$ 次。

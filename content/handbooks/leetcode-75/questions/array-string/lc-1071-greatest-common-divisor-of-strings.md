---
id: lc-1071-greatest-common-divisor-of-strings
section: array-string
order: 2
level: A
title: LC 1071 · 字符串的最大公因子
quick: >-
  先判 `str1 + str2 == str2 + str1`，不等则无公因子；相等时答案就是长度为 $\gcd(m,n)$ 的前缀。时间
  $O(m+n)$，额外空间 $O(m+n)$（拼接串）。
tags:
  - String
  - Math
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1071. Greatest Common Divisor of Strings
    url: https://leetcode.com/problems/greatest-common-divisor-of-strings/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

若 `s` 由 `t` 重复若干次（至少一次）拼成，称 `t` 整除 `s`。给 `str1`、`str2`，返回同时整除两者的最长字符串 `x`；不存在返回空串。长度在 $[1, 1000]$，只含大写字母。

## 思路

若存在公因子 `x`，两串都是 `x` 的重复，所以 `str1 + str2` 和 `str2 + str1` 都是 `x` 重复 $(m+n)/|x|$ 次，必然相等。反过来，两串拼接可交换时，它们一定是同一个基串的幂（字符串组合里的经典结论）。所以一次比较就能判有没有解。

有解时，任何公因子长度都要同时整除 $m$ 和 $n$，最长的就是 $\gcd(m,n)$，而且前缀 `str1[:g]` 确实能整除两串。

朴素做法是从 $\min(m,n)$ 往下枚举同时整除两者的长度，逐个检查前缀重复后是否等于原串，最坏 $O(\min(m,n)\cdot(m+n))$。我会先讲可交换判定，再补为什么是 gcd 长度。

## 参考代码

```python
from math import gcd


def gcdOfStrings(str1: str, str2: str) -> str:
    if str1 + str2 != str2 + str1:
        return ""
    return str1[: gcd(len(str1), len(str2))]


if __name__ == "__main__":
    assert gcdOfStrings("ABCABC", "ABC") == "ABC"
    assert gcdOfStrings("ABABAB", "ABAB") == "AB"
    assert gcdOfStrings("LEET", "CODE") == ""
    assert gcdOfStrings("A", "A") == "A"
    assert gcdOfStrings("AAAAAA", "AAAA") == "AA"
    assert gcdOfStrings("ABAB", "ABA") == ""
    print("ok")
```

## 复杂度

时间 $O(m+n)$：拼接和比较各一次，gcd 是 $O(\log\min(m,n))$。额外空间 $O(m+n)$，存两个拼接串。

## 边界

- 两串相同：答案就是它本身。
- 长度互质但字符全相同，如 `"AAA"`、`"AA"`：gcd 为 $1$，答案 `"A"`。
- 前缀相同但不是整倍，如 `"ABAB"`、`"ABA"`：拼接不等，返回空串。

## 追问

- **不记得可交换结论，怎么写保底解？** 从 $\gcd(m,n)$ 开始往下枚举同时整除 $m$、$n$ 的长度 $L$，检查 `str1[:L]` 重复 $m/L$ 次等于 `str1`、重复 $n/L$ 次等于 `str2`。实际只需检查 $L=\gcd(m,n)$ 这一个：若它不行，更短的因子长度也不行，因为更短的公因子重复后一定也能拼出 gcd 长度的公因子。

```python
from math import gcd


def gcdOfStrings_check(str1, str2):
    g = gcd(len(str1), len(str2))
    x = str1[:g]
    if x * (len(str1) // g) == str1 and x * (len(str2) // g) == str2:
        return x
    return ""
```

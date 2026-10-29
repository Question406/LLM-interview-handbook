---
id: lc-1071-greatest-common-divisor-of-strings
section: array-string
order: 2
level: A
title: LC 1071 · 字符串的最大公因子
quick: >-
  先判 `str1 + str2 == str2 + str1`，不相等就没有公因子；相等时答案就是长度为 $\gcd(m,n)$ 的前缀。拼接比较一次，时间
  $O(m+n)$，额外空间 $O(m+n)$ 存拼接串。
tags:
  - String
  - Math
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 1071. Greatest Common Divisor of Strings
    url: 'https://leetcode.com/problems/greatest-common-divisor-of-strings/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

对两个非空字符串 t 和 s，若把 t 完整重复若干次（至少一次）可以恰好拼成 s，就称 t 能整除 s。现给定 `str1`、`str2`，请找出能够同时整除这两个字符串、且长度最大的非空字符串。

### 输入与输出

实现 `gcdOfStrings(str1, str2) -> str`。返回这个最长字符串；不存在共同字符串因子时返回空字符串。这里比较的是完整字符串的重复结构，不是字符集合的交集。

### 约束

- `1 <= len(str1), len(str2) <= 1000`。
- 两个字符串只包含大写英文字母。

### 示例

```text
输入：str1 = "ABCABC", str2 = "ABC"
输出："ABC"
```

[LeetCode 原题](https://leetcode.com/problems/greatest-common-divisor-of-strings/description/)

## 解题思路与参考答案

## 题意

若 `s` 由 `t` 重复若干次（至少一次）拼成，称 `t` 整除 `s`。给 `str1`、`str2`，返回同时整除两者的最长字符串 `x`；不存在返回空串。长度在 $[1, 1000]$，只含大写字母。

## 思路

我会先用一个判定把无解的情况筛掉：`str1 + str2` 和 `str2 + str1` 相等才有公因子，有的话答案就是长度为 $\gcd(m,n)$ 的前缀。

拿 `"ABABAB"` 和 `"ABAB"` 走一遍。两种拼法都是 `"ABABABABAB"`，相等，所以有解；长度 6 和 4 的 gcd 是 2，答案是前缀 `"AB"`。换成 `"LEET"` 和 `"CODE"`，一种拼成 `"LEETCODE"`，另一种是 `"CODELEET"`，不相等，直接返回空串。

这个判定为什么成立？如果存在公因子 `x`，两串都是 `x` 的重复，那 `str1 + str2` 和 `str2 + str1` 都是 `x` 重复 $(m+n)/|x|$ 次，必然相等。反过来，两串拼接可交换时，它们一定是同一个基串的幂，这是字符串组合里的经典结论。所以比较一次就知道有没有解。

有解之后，任何公因子的长度都要同时整除 $m$ 和 $n$，最长只能是 $\gcd(m,n)$，而前缀 `str1[:g]` 确实能整除两串。

朴素做法是从 $\min(m,n)$ 往下枚举同时整除两者的长度，逐个检查前缀重复后是否等于原串，最坏 $O(\min(m,n)\cdot(m+n))$。面试时我会先讲可交换判定，再补为什么是 gcd 长度。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert gcdOfStrings("ABCABC", "ABC") == "ABC"
assert gcdOfStrings("ABABAB", "ABAB") == "AB"
assert gcdOfStrings("LEET", "CODE") == ""
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(m+n)$：拼接和比较各一次，gcd 是 $O(\log\min(m,n))$。额外空间 $O(m+n)$，存两个拼接串。

## Edge Cases

两串相同的时候，答案就是它本身。

长度互质但字符全相同也有解，比如 `"AAA"` 和 `"AA"`，gcd 是 $1$，答案是 `"A"`。

前缀看着一样但长度不成倍，比如 `"ABAB"` 和 `"ABA"`，拼接结果不相等，返回空串。

## 追问

**不记得可交换结论，怎么写保底解？**
直接检查长度为 $\gcd(m,n)$ 的前缀就够了。最直观的想法是从 $\gcd(m,n)$ 开始往下枚举同时整除 $m$、$n$ 的长度 $L$，检查 `str1[:L]` 重复 $m/L$ 次等于 `str1`、重复 $n/L$ 次等于 `str2`。实际只需要检查 $L=\gcd(m,n)$ 这一个：它不行的话，更短的因子长度也不行，因为更短的公因子重复后一定也能拼出 gcd 长度的公因子。

```python
from math import gcd


def gcdOfStrings_check(str1, str2):
    g = gcd(len(str1), len(str2))
    x = str1[:g]
    if x * (len(str1) // g) == str1 and x * (len(str2) // g) == str2:
        return x
    return ""
```

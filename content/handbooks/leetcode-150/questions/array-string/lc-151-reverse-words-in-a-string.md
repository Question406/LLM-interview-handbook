---
id: lc-151-reverse-words-in-a-string
section: array-string
order: 21
level: A
title: LC 151 · 反转字符串中的单词
quick: >-
  `split` 按空白拆出单词再反转拼接，多空格会自动压掉。结果去首尾空格、单词间只留一个空格。时间
  $O(n)$。
tags:
  - String
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 151. 反转字符串中的单词
    url: https://leetcode.cn/problems/reverse-words-in-a-string/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

反转字符串 `s` 里单词的顺序。单词是不含空格的字符序列。结果里单词之间恰好一个空格，首尾无空格。输入可能有前导、尾随和连续空格。

## 思路

`s.split()` 默认按任意空白切并丢掉空段，再 `reversed` 后 `" ".join`。这是 Python 里最干净的写法。

若要求 $O(1)$ 额外空间（字符数组）：先整体反转，再逐单词反转回来，最后压缩空格。白板一般先写 `split`，再口述原地三步。

## 参考代码

```python
def reverseWords(s: str) -> str:
    return " ".join(reversed(s.split()))


if __name__ == "__main__":
    assert reverseWords("the sky is blue") == "blue is sky the"
    assert reverseWords("  hello world  ") == "world hello"
    assert reverseWords("a good   example") == "example good a"
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(n)$（单词列表）。原地字符数组做法额外空间 $O(1)$。

## 边界

- 单个单词：去完首尾空格后原样返回。
- 全是空格夹一个词：`split` 后只剩该词。
- 多个连续空格：`split()` 会丢掉空段，`join` 后单词间只留一个空格。

## 追问

- **要求原地（字符数组 $O(1)$ 额外空间）？** 三步：先整体反转，单词顺序对了但每个词内部是反的；再逐单词反转回来；最后双指针压缩空格、去掉首尾。时间 $O(n)$，额外空间 $O(1)$。Python 字符串不可变，白板用 list 演示。这块容易栽：压缩空格时单词之间只写一个空格，以及 `reverse` 的区间是闭区间。

```python
def reverseWords_inplace(s):
    a = list(s)
    n = len(a)

    def reverse(lo, hi):
        while lo < hi:
            a[lo], a[hi] = a[hi], a[lo]
            lo += 1
            hi -= 1

    reverse(0, n - 1)
    i = 0
    while i < n:
        while i < n and a[i] == " ":
            i += 1
        j = i
        while j < n and a[j] != " ":
            j += 1
        reverse(i, j - 1)
        i = j
    w = 0
    i = 0
    while i < n:
        while i < n and a[i] == " ":
            i += 1
        if i == n:
            break
        if w:
            a[w] = " "
            w += 1
        while i < n and a[i] != " ":
            a[w] = a[i]
            w += 1
            i += 1
    return "".join(a[:w])
```

- **只反转每个单词内部、不改单词顺序（LC 557）？** 遇到单词就地反转，空格原样保留。双指针找每个词的 `[l, r)`，反转后再从 `r` 继续。时间 $O(n)$，额外空间 $O(n)$（字符串不可变时）或 $O(1)$（字符数组）。本题改顺序、压空格；557 改词内、保留空格。不在 150 手册里。

```python
def reverseWords_iii(s):
    a = list(s)
    n = len(a)
    i = 0
    while i < n:
        if a[i] == " ":
            i += 1
            continue
        j = i
        while j < n and a[j] != " ":
            j += 1
        l, r = i, j - 1
        while l < r:
            a[l], a[r] = a[r], a[l]
            l += 1
            r -= 1
        i = j
    return "".join(a)
```

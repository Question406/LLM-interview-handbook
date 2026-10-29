---
id: lc-151-reverse-words-in-a-string
section: array-string
order: 21
level: A
title: LC 151 · 反转字符串中的单词
quick: >-
  Python 里用 `split` 按空白拆出单词，反转后用一个空格拼回去，多余空格会自动压掉，结果首尾没有空格。时间
  $O(n)$。要求原地的话就整体反转、逐词反转、再压缩空格。
tags:
  - String
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 151. 反转字符串中的单词
    url: 'https://leetcode.cn/problems/reverse-words-in-a-string/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定一个包含若干单词的字符串，把单词的出现顺序完全反转，单词内部的字符顺序保持不变。单词是由非空格字符组成的连续片段。输入可以含首尾空格或多个连续空格；输出必须去掉首尾空格，并在相邻单词之间只保留一个空格。

### 输入与输出

实现 `reverseWords(s: str) -> str`，返回整理后的字符串。

### 约束

- `1 <= len(s) <= 10^4`。
- 输入只含大小写英文字母、数字和普通空格，且至少有一个单词。

### 示例

```text
输入：s = "the sky is blue"
输出："blue is sky the"
```

这里反转的是四个单词的顺序，不是把整个字符串逐字符倒置。

## 解题思路与参考答案

## 题意

反转字符串 `s` 里单词的顺序。单词是不含空格的字符序列。结果里单词之间恰好一个空格，首尾无空格。输入可能有前导、尾随和连续空格。

## 思路

Python 里最干净的写法是 `s.split()`：它默认按任意空白切，并丢掉空段，之后 `reversed` 再 `" ".join`。拿 `"a good   example"` 走一遍：`split()` 得到 `["a", "good", "example"]`，中间的连续空格已经没了，反转后拼成 `"example good a"`。

如果要求 $O(1)$ 额外空间（字符数组），就先整体反转，再逐单词反转回来，最后压缩空格。白板上我一般先写 `split`，再口述原地的三步。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert reverseWords("the sky is blue") == "blue is sky the"
assert reverseWords("  hello world  ") == "world hello"
assert reverseWords("a good   example") == "example good a"
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(n)$（单词列表）。原地字符数组做法额外空间 $O(1)$。

## Edge Cases

单个单词去掉首尾空格后原样返回。全是空格夹一个词时，`split` 后只剩这个词。多个连续空格会被 `split()` 当空段丢掉，`join` 后单词之间只留一个空格。

## 追问

**要求原地、字符数组 $O(1)$ 额外空间呢？**
分三步。先整体反转，单词顺序对了，但每个词内部是反的；再逐个单词反转回来；最后用双指针压缩空格、去掉首尾。时间 $O(n)$，额外空间 $O(1)$。Python 字符串不可变，白板上用 list 演示。压缩空格时单词之间只写一个空格，`reverse` 的区间是闭区间，这两处最容易写错。

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

**只反转每个单词内部、不改单词顺序呢（LC 557）？**
遇到单词就地反转，空格原样保留。用双指针找每个词的 `[l, r)`，反转后从 `r` 继续。时间 $O(n)$，额外空间在字符串不可变时是 $O(n)$，字符数组是 $O(1)$。本题改顺序、压空格，557 改词内、保留空格。这题不在 150 手册里。

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

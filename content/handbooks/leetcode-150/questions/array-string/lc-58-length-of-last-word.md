---
id: lc-58-length-of-last-word
section: array-string
order: 19
level: A
title: LC 58 · 最后一个单词的长度
quick: >-
  从右往左：先跳过尾部空格，再计数连续非空格。时间 $O(L)$，额外空间 $O(1)$。不要 `split` 也能写。
tags:
  - String
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 58. 最后一个单词的长度
    url: https://leetcode.cn/problems/length-of-last-word/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

字符串 `s` 由单词和空格组成，至少有一个单词。返回最后一个单词的长度。单词是不含空格的最大连续字符段。

## 思路

尾部可能有空格，所以从右扫：先跳过 `' '`，再数到下一个空格或开头。`s.split()` 再取 `[-1]` 也能过，但面试应展示 $O(1)$ 额外空间的指针写法。

## 参考代码

```python
def lengthOfLastWord(s: str) -> int:
    i = len(s) - 1
    while i >= 0 and s[i] == " ":
        i -= 1
    length = 0
    while i >= 0 and s[i] != " ":
        length += 1
        i -= 1
    return length


if __name__ == "__main__":
    assert lengthOfLastWord("Hello World") == 5
    assert lengthOfLastWord("   fly me   to   the moon  ") == 4
    assert lengthOfLastWord("luffy is still joyboy") == 8
    print("ok")
```

## 复杂度

时间 $O(L)$，最坏扫完整串。额外空间 $O(1)$。

## 边界

- 无尾空格：第一段 `while` 立刻停，直接数最后一个单词。
- 前导和尾随都有空格：先跳尾空格，再数，前导空格碰不到。
- 整个串一个单词：第二段 `while` 会数到下标 $0$。

## 追问

- **第一个单词的长度？** 把方向反过来：`i` 从 $0$ 出发，先跳过前导空格，再数连续非空格，碰到空格或结尾停下。时间 $O(L)$，额外空间 $O(1)$。`s.split()` 再取 `[0]` 也能过，但会开 $O(L)$ 额外空间，面试更想看指针。易错点是没跳前导空格就开数，以及空串 / 全空格——本题保证至少一个单词，若放宽要约定返回 $0$。不要 `strip` 后再 `split`，那是 $O(L)$ 空间的偷懒写法。

```python
def lengthOfFirstWord(s):
    i, n = 0, len(s)
    while i < n and s[i] == " ":
        i += 1
    length = 0
    while i < n and s[i] != " ":
        length += 1
        i += 1
    return length
```

- **空白不只有空格，还有 tab？** 先和面试官定义空白集合，例如 `{' ', '\t'}`，两段循环改成 `s[i] in blanks` / `s[i] not in blanks`。Python 也可用 `str.isspace()`，它还包含换行、不间断空格等，范围更宽，要说清楚。时间仍 $O(L)$，额外空间 $O(1)$。易错点是只改了一段循环：跳过尾部空白后，计数阶段仍只认 `' '`，会把 tab 当成单词字符。单词中间若允许 tab，定义就变成「空白分隔」，和本题「空格分隔」不是同一题。

```python
def lengthOfLastWord(s, blanks=" \t"):
    i = len(s) - 1
    while i >= 0 and s[i] in blanks:
        i -= 1
    length = 0
    while i >= 0 and s[i] not in blanks:
        length += 1
        i -= 1
    return length
```


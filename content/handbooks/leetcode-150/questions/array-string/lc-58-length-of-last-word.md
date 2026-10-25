---
id: lc-58-length-of-last-word
section: array-string
order: 19
level: A
title: LC 58 · 最后一个单词的长度
quick: "从右往左扫：先跳过尾部空格，再数连续的非空格字符，碰到空格或开头就停。时间 $O(L)$，额外空间 $O(1)$。不用 `split` 也能写。"
tags:
  - String
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 58. 最后一个单词的长度
    url: https://leetcode.cn/problems/length-of-last-word/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定由英文单词和空格组成的字符串，返回最后一个单词的字符数。单词是字符串中不含空格的最大连续字符段；末尾可能有空格，这些空格不属于最后一个单词。

### 输入与输出

实现 `lengthOfLastWord(s: str) -> int`，返回长度，不返回单词本身。

### 约束

- `1 <= len(s) <= 10^4`。
- 输入只含英文字母和普通空格，且保证至少有一个单词。

### 示例

```text
输入：s = "Hello World"
输出：5
```

最后一个单词是 `World`，含 5 个字符。

## 解题思路与参考答案

## 题意

字符串 `s` 由单词和空格组成，至少有一个单词。返回最后一个单词的长度。单词是不含空格的最大连续字符段。

## 思路

我会从右往左扫，因为尾部可能有空格，从右边开始最直接。先跳过 `' '`，再数到下一个空格或开头为止。拿 `"   fly me   to   the moon  "` 走一遍：先跳过末尾两个空格，停在 `n` 上，再往左数 `n`、`o`、`o`、`m`，碰到空格停下，长度是 $4$。

`s.split()` 再取 `[-1]` 也能过，指针写法能做到 $O(1)$ 额外空间。

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
    assert lengthOfLastWord("luffy is still joyboy") == 6
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert lengthOfLastWord("Hello World") == 5
assert lengthOfLastWord("   fly me   to   the moon  ") == 4
assert lengthOfLastWord("luffy is still joyboy") == 6
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(L)$，最坏扫完整串。额外空间 $O(1)$。

## 边界

没有尾空格时，第一段 `while` 立刻停，直接数最后一个单词。前导和尾随都有空格时，先跳尾空格再数，前导空格根本碰不到。整个串只有一个单词时，第二段 `while` 会一直数到下标 $0$。

## 追问

**要第一个单词的长度呢？**
把方向反过来就行。`i` 从 $0$ 出发，先跳过前导空格，再数连续非空格，碰到空格或结尾停下，时间 $O(L)$，额外空间 $O(1)$。`s.split()` 再取 `[0]` 也能过，但要开 $O(L)$ 额外空间，面试更想看指针写法；先 `strip` 再 `split` 同样要 $O(L)$ 额外空间。没跳前导空格就开始数、以及空串或全空格，是最容易漏的情况。本题保证至少一个单词，放宽的话要约定返回 $0$。

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

**空白不只有空格，还有 tab 呢？**
先和面试官把空白集合定下来，比如 `{' ', '\t'}`，然后两段循环都改成 `s[i] in blanks` / `s[i] not in blanks`。Python 也可以用 `str.isspace()`，但它还包含换行、不间断空格等，范围更宽，要说清楚。时间仍是 $O(L)$，额外空间 $O(1)$。两段循环都要改：只改了跳尾部那段的话，计数阶段还只认 `' '`，会把 tab 当成单词字符。如果单词中间也允许 tab，定义就变成「空白分隔」，和本题的「空格分隔」是两道题。

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

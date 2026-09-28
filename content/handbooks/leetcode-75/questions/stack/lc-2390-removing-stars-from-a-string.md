---
id: lc-2390-removing-stars-from-a-string
section: stack
order: 1
level: A
title: LC 2390 · 从字符串中移除星号
quick: >-
  用栈：普通字符入栈，遇到 `*` 就弹栈顶，栈顶正好是星号左边最近的还没被删的字符。最后把栈拼回字符串。时间 $O(n)$，额外空间
  $O(n)$。
tags:
  - String
  - Stack
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 2390. Removing Stars From a String
    url: https://leetcode.com/problems/removing-stars-from-a-string/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

字符串 `s` 由小写字母和 `*` 组成。每次操作选一个 `*`，删掉它和它左边最近的一个非星号字符。反复操作直到没有星号，返回结果。题目保证操作总能进行，结果唯一。$|s| \le 10^5$。

## 思路

「左边最近的未删字符」就是后进先出：从左往右扫，保留下来的字符按顺序压栈，遇到 `*` 时它要删的正好是栈顶。扫完栈里就是答案。

直接在字符串上找、删是每次 $O(n)$，整体 $O(n^2)$。Python 里用 `list` 当栈，最后 `"".join`，别在循环里拼字符串。

## 参考代码

```python
def removeStars(s: str) -> str:
    stack = []
    for c in s:
        if c == "*":
            stack.pop()
        else:
            stack.append(c)
    return "".join(stack)


if __name__ == "__main__":
    assert removeStars("leet**cod*e") == "lecoe"
    assert removeStars("erase*****") == ""
    assert removeStars("abc") == "abc"
    assert removeStars("a*b") == "b"
    assert removeStars("ab*c*") == "a"
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(n)$。

## 边界

- 没有星号：原样返回。
- 全部删光：返回空串。
- 题目保证每个 `*` 左边都有字符可删，`pop` 不会空栈；不保证时要先判空。

## 追问

- **要求原地、$O(1)$ 额外空间（可变字符数组）？** 用写指针 `w` 模拟栈顶：字母写到 `w` 并右移，星号让 `w` 左移。前 `w` 个就是结果。

```python
def removeStarsInPlace(chars):
    w = 0
    for c in chars:
        if c == "*":
            w -= 1
        else:
            chars[w] = c
            w += 1
    return "".join(chars[:w])
```

- **比较两个带退格的串是否相等（LC 844）？** 可以各跑一遍栈再比较。想要 $O(1)$ 空间就从右往左扫，用计数器记还要跳过几个字符，两边同步比较下一个有效字符。

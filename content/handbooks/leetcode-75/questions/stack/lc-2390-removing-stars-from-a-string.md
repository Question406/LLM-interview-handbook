---
id: lc-2390-removing-stars-from-a-string
section: stack
order: 1
level: A
title: LC 2390 · 从字符串中移除星号
quick: >-
  星号要删的「左边最近的未删字符」就是后进先出，所以用栈：普通字符入栈，遇到 `*` 就弹栈顶，最后把栈拼回字符串。时间 $O(n)$，额外空间
  $O(n)$。
tags:
  - String
  - Stack
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 2390. Removing Stars From a String
    url: 'https://leetcode.com/problems/removing-stars-from-a-string/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定由小写英文字母和星号 `*` 构成的字符串 s。每次选取一个星号，删除这个星号以及它左侧最近的一个非星号字符。重复操作直到没有星号，返回剩余字符串；其余字符的相对顺序不变。

### 接口与输出

实现 `removeStars(s: str) -> str`。输入保证每一步所需删除的左侧字符存在，并且最终结果唯一；结果可以是空字符串。

### 合法输入与约束

`1 <= len(s) <= 100000`。每个星号只删除一个非星号字符，不是删除它左侧的全部内容。

### 示例

```text
输入：s = "leet**cod*e"
输出："lecoe"
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/removing-stars-from-a-string/description/)。

## 解题思路与参考答案

## 题意

字符串 `s` 由小写字母和 `*` 组成。每次操作选一个 `*`，删掉它和它左边最近的一个非星号字符。反复操作直到没有星号，返回结果。题目保证操作总能进行，结果唯一。$|s| \le 10^5$。

## 思路

我会用栈，因为「左边最近的未删字符」就是后进先出。从左往右扫，保留下来的字符按顺序压栈，遇到 `*` 时它要删的正好是栈顶，扫完栈里就是答案。直接在字符串上找、删是每次 $O(n)$，整体 $O(n^2)$。

拿 `"leet**cod*e"` 走一遍。`l e e t` 入栈，两个星号弹掉 `t` 和 `e`，栈里剩 `l e`；`c o d` 入栈，星号弹掉 `d`；最后 `e` 入栈，拼起来是 `"lecoe"`。

Python 里用 `list` 当栈，最后 `"".join`，别在循环里拼字符串。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
assert removeStars("leet**cod*e") == "lecoe"
assert removeStars("erase*****") == ""
assert removeStars("abc") == "abc"
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(n)$。

## Edge Cases

没有星号时原样返回；全部删光时返回空串。

题目保证每个 `*` 左边都有字符可删，`pop` 不会碰到空栈；不保证的话要先判空。

## 追问

**要求原地、$O(1)$ 额外空间（可变字符数组）呢？**
用写指针 `w` 模拟栈顶，字母写到 `w` 并右移，星号让 `w` 左移。前 `w` 个就是结果。

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

**比较两个带退格的串是否相等（LC 844）呢？**
可以各跑一遍栈再比较。想要 $O(1)$ 空间就从右往左扫，用计数器记还要跳过几个字符，两边同步比较下一个有效字符。

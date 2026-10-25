---
id: lc-1768-merge-strings-alternately
section: array-string
order: 1
level: A
title: LC 1768 · 交替合并字符串
quick: "一个下标 `i` 从 $0$ 走到 $\\max(m,n)-1$，每步先看 `word1` 再看 `word2`，没越界就追加，较长串剩下的部分自然接在后面。时间 $O(m+n)$，额外空间 $O(m+n)$，就是结果串。"
tags:
  - String
  - Two Pointers
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1768. Merge Strings Alternately
    url: https://leetcode.com/problems/merge-strings-alternately/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题目描述

给定两个字符串，从第一个字符串开始，交替从两者的开头各取一个字符，按取出顺序组成新字符串。某个字符串先用完时，将另一个字符串剩余的全部字符按原顺序接到末尾。

### 输入与输出

实现 `mergeAlternately(word1, word2) -> str`。返回合并后的新字符串，两个输入串内部的字符顺序都不能改变。

### 约束与约定

- `1 <= len(word1),len(word2) <= 100`。
- 两个字符串都只含小写英文字母。

### 示例

```text
输入：word1 = "abc", word2 = "pqr"
输出："apbqcr"
```

示例依次取 a、p、b、q、c、r，得到 apbqcr。

[官方原题与完整题面](https://leetcode.com/problems/merge-strings-alternately/description/)。

## 解题思路与参考答案

## 题意

给两个字符串 `word1`、`word2`，从 `word1` 开始交替各取一个字符拼成新串。一个串先用完，另一个串剩下的字符原样接到末尾。长度都在 $[1, 100]$，只含小写字母。

## 思路

用一个下标 `i` 从 $0$ 扫到两串中较长的长度，每一步先看 `word1` 再看 `word2`，没越界就追加。这样短串用完以后，循环只会继续追加长串的字符，不用单独写「接尾巴」的分支。

拿 `"ab"` 和 `"pqrs"` 走一遍：`i = 0` 追加 `a`、`p`，`i = 1` 追加 `b`、`q`，到 `i = 2` 和 `i = 3` 时 `word1` 已经越界，只追加 `r`、`s`，结果是 `"apbqrs"`。

Python 里字符串不可变，我会先把字符收进 list，最后 `"".join`，避免反复 `+=` 产生多余拷贝。

## 参考代码

```python
def mergeAlternately(word1: str, word2: str) -> str:
    m, n = len(word1), len(word2)
    out = []
    for i in range(max(m, n)):
        if i < m:
            out.append(word1[i])
        if i < n:
            out.append(word2[i])
    return "".join(out)


if __name__ == "__main__":
    assert mergeAlternately("abc", "pqr") == "apbqcr"
    assert mergeAlternately("ab", "pqrs") == "apbqrs"
    assert mergeAlternately("abcd", "pq") == "apbqcd"
    assert mergeAlternately("a", "b") == "ab"
    assert mergeAlternately("a", "xyz") == "axyz"
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert mergeAlternately("abc", "pqr") == "apbqcr"
assert mergeAlternately("ab", "pqrs") == "apbqrs"
assert mergeAlternately("abcd", "pq") == "apbqcd"
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(m+n)$，额外空间 $O(m+n)$，就是结果本身。

## 边界

两串等长时严格交替，没有尾巴。

有一边只有一个字符时，第一轮取完，后面全是另一边剩下的字符。

顺序固定从 `word1` 开始，写反的话示例 `"ab"`、`"pqrs"` 会变成 `"paqbrs"`。

## 追问

**推广到 $k$ 个字符串轮流取呢？**
思路一样，按轮次下标 `i` 扫到最长长度，每轮按顺序遍历所有串，没越界就追加。时间是 $O(\sum |s_j| + k\cdot L)$，$L$ 是最长串的长度。如果各串长度差得很大，可以用队列只保留还没用完的串，每轮弹出、追加，没用完再放回去，时间降到 $O(\sum |s_j|)$。

```python
from collections import deque


def mergeK(words):
    q = deque((w, 0) for w in words if w)
    out = []
    while q:
        w, i = q.popleft()
        out.append(w[i])
        if i + 1 < len(w):
            q.append((w, i + 1))
    return "".join(out)
```

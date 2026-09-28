---
id: lc-1768-merge-strings-alternately
section: array-string
order: 1
level: A
title: LC 1768 · 交替合并字符串
quick: >-
  一个下标 `i` 从 $0$ 走到 $\max(m,n)-1$，两边各自没越界就依次追加。较长串的剩余部分自然接在后面。时间
  $O(m+n)$，额外空间 $O(m+n)$（结果串）。
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

## 题意

给两个字符串 `word1`、`word2`，从 `word1` 开始交替各取一个字符拼成新串。一个串先用完，另一个串剩下的字符原样接到末尾。长度都在 $[1, 100]$，只含小写字母。

## 思路

用同一个下标 `i` 扫到两串较长的长度：`i` 在 `word1` 范围内就追加 `word1[i]`，再看 `word2`。这样短串用完后，循环只会继续追加长串的字符，不用单独写「接尾巴」的分支。

Python 里字符串不可变，我会把字符先收进 list，最后 `"".join`，避免反复 `+=` 产生多余拷贝。

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

## 复杂度

时间 $O(m+n)$，额外空间 $O(m+n)$，就是结果本身。

## 边界

- 两串等长：严格交替，没有尾巴。
- 一边只有一个字符：取完第一轮后全是另一边的剩余。
- 顺序固定从 `word1` 开始，写反了示例 `"ab"`、`"pqrs"` 会变成 `"paqbrs"`。

## 追问

- **推广到 $k$ 个字符串轮流取？** 同样按轮次下标 `i` 扫到最长长度，每轮按顺序遍历所有串，没越界就追加。时间 $O(\sum |s_j| + k\cdot L)$，$L$ 是最长串长度；若各串长度差很大，可以用队列只保留还没用完的串，每轮弹出、追加、没用完再放回，时间降到 $O(\sum |s_j|)$。

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

---
id: lc-1657-determine-if-two-strings-are-close
section: hashmap
order: 3
level: S
title: LC 1657 · 确定两个字符串是否接近
quick: >-
  操作 1 让字符顺序无关，操作 2 让频次可以在已出现的字符之间任意重新分配。所以两串接近当且仅当：出现的字符集合相同，且频次排序后相同。时间
  $O(n)$，额外空间 $O(1)$（字符集 26）。
tags:
  - String
  - Hash
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1657. Determine if Two Strings Are Close
    url: https://leetcode.com/problems/determine-if-two-strings-are-close/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

两个小写字母串 `word1`、`word2`。可以对任一字符串反复做两种操作：

- 操作 1：交换任意两个字符的位置。
- 操作 2：选两个已经出现的字符 `a`、`b`，把所有 `a` 变成 `b`、所有 `b` 变成 `a`。

能把 `word1` 变成 `word2` 就返回 `true`。长度 $\le 10^5$。

## 思路

先看两种操作保住了什么。操作 1 不改任何字符的频次。操作 2 只是把两个字符的频次互换，字符集合不变，频次的多重集合也不变。所以两个条件是必要的：字符集合相同，频次排序后相同。

反过来也够用。字符集合相同时，操作 2 相当于在这些字符之间交换频次，任意一个排列都能由若干次交换得到，所以可以把频次分配调成和 `word2` 一致；频次一致后，操作 1 把顺序排好。长度不同的情况会被频次比较自动排除。

我会先说「找不变量」，再用 `Counter` 比较 `keys` 和排序后的 `values`，别去模拟操作。

## 参考代码

```python
from collections import Counter


def closeStrings(word1: str, word2: str) -> bool:
    if len(word1) != len(word2):
        return False
    c1, c2 = Counter(word1), Counter(word2)
    return c1.keys() == c2.keys() and sorted(c1.values()) == sorted(c2.values())


if __name__ == "__main__":
    assert closeStrings("abc", "bca") is True
    assert closeStrings("a", "aa") is False
    assert closeStrings("cabbba", "abbccc") is True
    assert closeStrings("uau", "ssx") is False
    assert closeStrings("aab", "bbb") is False
    assert closeStrings("aabbb", "aaabb") is True
    print("ok")
```

## 复杂度

时间 $O(n)$：计数线性，排序最多 $26$ 个频次是常数。额外空间 $O(1)$。

## 边界

- 长度不同：直接 `false`。
- 频次多重集合相同但字符集合不同，如 `"uau"` 与 `"ssx"`：操作 2 不能凭空造出没出现过的字符，`false`。
- 字符集合相同但频次多重集合不同，如 `"aabbb"` 与 `"abbbb"`：$\{2,3\}$ 对 $\{1,4\}$，`false`。

## 追问

- **只允许操作 1？** 就是变位词判断：`Counter(word1) == Counter(word2)`。
- **操作 2 允许把字符换成没出现过的字母？** 字符集合的限制没有了，只剩频次多重集合相同这一个条件。

```python
from collections import Counter

def closeStringsAnyLetter(word1, word2):
    return sorted(Counter(word1).values()) == sorted(Counter(word2).values())
```

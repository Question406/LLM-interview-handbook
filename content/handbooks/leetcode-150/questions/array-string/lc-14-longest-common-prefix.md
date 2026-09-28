---
id: lc-14-longest-common-prefix
section: array-string
order: 20
level: S
title: LC 14 · 最长公共前缀
quick: >-
  以第一串为 `prefix`，逐个字符串比较；不匹配就截短 `prefix`。空了就提前返回。时间 $O(S)$（$S$ 为字符总数）。
tags:
  - String
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 14. 最长公共前缀
    url: https://leetcode.cn/problems/longest-common-prefix/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

字符串数组 `strs`，返回它们的最长公共前缀。没有公共前缀就返回空串。

## 思路

横向：`prefix` 初始化为 `strs[0]`，对每个后续串不断截到双方公共前缀，`prefix` 空就可以停。纵向：按列比较所有串的第 $j$ 个字符，遇到不同或某串结束就返回 `s[0][:j]`。

分治、字典树也能做；白板横向或纵向就够。

## 参考代码

```python
from typing import List


def longestCommonPrefix(strs: List[str]) -> str:
    if not strs:
        return ""
    prefix = strs[0]
    for s in strs[1:]:
        while not s.startswith(prefix):
            prefix = prefix[:-1]
            if not prefix:
                return ""
    return prefix


if __name__ == "__main__":
    assert longestCommonPrefix(["flower", "flow", "flight"]) == "fl"
    assert longestCommonPrefix(["dog", "racecar", "car"]) == ""
    print("ok")
```

## 复杂度

时间 $O(S)$，$S$ 是所有字符个数。额外空间 $O(1)$（不计输出）。

## 边界

- 只有一个串：公共前缀就是它自己。
- 存在空串：公共前缀立刻变成空。
- 公共前缀恰好是某个完整串：比如 `["ab", "abc"]`，答案是 `ab`。

## 追问

- **规模很大、短串很少？** 公共前缀长度不超过最短串，我一般先扫一遍找最短串当初始 `prefix`，能少做很多 `startswith`。也可以按列比：第 $j$ 列只要有一个串长度不够或字符不同就停，最坏仍 $O(S)$，但一旦失配立刻结束，对「前缀很短」的数据更友好。时间仍 $O(S)$，$S$ 为字符总数。不要先按字典序排序再比首尾，排序是 $O(S\log n)$，常数更大，除非后续要多次查询。

- **动态插入新串？** 维护当前公共前缀 `prefix`。每来一个新串 `s`，把 `prefix` 截到 `s` 与它的公共前缀；一旦变成空就可以停，后面再插入也不会变长。删除更麻烦：删掉的若不是「卡前缀长度」的那条，前缀可能变长，需要重扫剩余串。白板插入用截断即可，时间与新串长度成正比。

```python
def common_prefix(a, b):
    i = 0
    m = min(len(a), len(b))
    while i < m and a[i] == b[i]:
        i += 1
    return a[:i]


def insert(prefix, s):
    return common_prefix(prefix, s) if prefix else ""
```

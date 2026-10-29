---
id: lc-14-longest-common-prefix
section: array-string
order: 20
level: S
title: LC 14 · 最长公共前缀
quick: >-
  以第一串为 `prefix`，逐个和后面的串比，不匹配就把 `prefix` 截短，空了就提前返回。时间 $O(S)$（$S$ 为字符总数），额外空间
  $O(1)$。
tags:
  - String
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 14. 最长公共前缀
    url: 'https://leetcode.cn/problems/longest-common-prefix/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定非空字符串列表 `strs`，找出所有字符串共同拥有的最长开头片段。前缀必须从每个字符串的第一个字符开始；某个字符串为空，或者所有字符串没有共同的首字符时，结果为空字符串。

### 输入与输出

实现 `longestCommonPrefix(strs) -> str`。返回公共前缀本身，而不是它的长度；比较区分不同字符。

### 约束

- `1 <= len(strs) <= 200`。
- 每个字符串长度在 0 到 200 之间。
- 非空字符串只包含小写英文字母。

### 示例

```text
输入：strs = ["flower","flow","flight"]
输出："fl"
```

[LeetCode 原题](https://leetcode.com/problems/longest-common-prefix/description/)

## 解题思路与参考答案

## 题意

字符串数组 `strs`，返回它们的最长公共前缀。没有公共前缀就返回空串。

## 思路

我用横向比较：`prefix` 先设成 `strs[0]`，再和后面每个串比，不断截到双方的公共前缀，`prefix` 一空就可以停。拿 `["flower", "flow", "flight"]` 走一遍：`flower` 和 `flow` 比完截成 `flow`，再和 `flight` 比截成 `fl`，答案就是 `fl`。

纵向也行：按列比所有串的第 $j$ 个字符，遇到不同或某个串结束，就返回 `s[0][:j]`。分治、字典树也能做，白板上横向或纵向就够了。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert longestCommonPrefix(["flower", "flow", "flight"]) == "fl"
assert longestCommonPrefix(["dog", "racecar", "car"]) == ""
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(S)$，$S$ 是所有字符个数。额外空间 $O(1)$（不计输出）。

## Edge Cases

只有一个串时，公共前缀就是它自己。存在空串时，公共前缀立刻变成空。公共前缀也可能恰好是某个完整串，比如 `["ab", "abc"]`，答案是 `ab`。

## 追问

**规模很大、短串很少怎么办？**
先扫一遍找最短串当初始 `prefix`。公共前缀长度不会超过最短串，这样能少做很多 `startswith`。也可以按列比，第 $j$ 列只要有一个串长度不够或字符不同就停，最坏仍是 $O(S)$（$S$ 为字符总数），但一失配就结束，对前缀很短的数据更友好。先按字典序排序再比首尾也能做，但排序是 $O(S\log n)$，常数更大，除非后面要多次查询，否则不划算。

**动态插入新串呢？**
维护当前公共前缀 `prefix`，每来一个新串 `s`，就把 `prefix` 截到它和 `s` 的公共前缀，时间和新串长度成正比。一旦变空就可以停，后面再插入也不会变长。删除更麻烦：删掉的如果不是卡住前缀长度的那条，前缀可能变长，得重扫剩下的串。白板上插入用截断就够了。

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

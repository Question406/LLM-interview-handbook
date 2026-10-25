---
id: lc-49-group-anagrams
section: hashmap
order: 5
level: S
title: LC 49 · 字母异位词分组
quick: >-
  我会给每个串做一个可哈希的签名，异位词的签名相同：26 维计数元组，或者排完序的串。签名相同的放进同一个桶，计数元组的时间大约 $O(nk)$。
tags:
  - Hash
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 49. 字母异位词分组
    url: https://leetcode.cn/problems/group-anagrams/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定字符串数组 strs，把所有互为字母异位词的字符串归入同一组。两个字符串互为异位词，当且仅当它们包含的每种字母及其出现次数都相同，允许字母排列顺序不同。

### 接口与输出

实现 `groupAnagrams(strs: List[str]) -> List[List[str]]`。每个输入字符串都应在输出中出现一次，重复字符串也要保留相应次数；组与组之间以及每组内部的顺序不限。

### 合法输入与约束

`1 <= len(strs) <= 10000`，每个字符串长度为 0 到 100，只含小写英文字母。空字符串合法，所有空字符串应处于同一组。

### 示例

```text
输入：strs = ["eat","tea","tan","ate","nat","bat"]
输出：[["bat"],["nat","tan"],["ate","eat","tea"]]
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/group-anagrams/description/)。

## 解题思路与参考答案

## 题意

给你一串单词，把互为字母异位词的分到同一组。组之间、组内顺序都随意。

## 思路

我会按签名做哈希分组。签名要满足异位词相同、非异位词不同。常用的有两种：一种是计数元组，扫一遍 $k$ 个字符得到长度 26 的次数数组，用 `tuple(cnt)` 当 key，总时间 $O(nk)$；另一种是排序串，用 `''.join(sorted(s))` 当 key，总时间 $O(nk\log k)$。参考代码用的是计数元组。

拿 `["eat","tea","tan","ate","nat","bat"]` 来说，`eat`、`tea`、`ate` 都是一个 a、一个 e、一个 t，计数相同，进同一组；`tan` 和 `nat` 一组；`bat` 自己一组。

别用质数乘积当签名，次数一大就溢出。

## 参考代码

```python
from collections import defaultdict
from typing import List


def groupAnagrams(strs: List[str]) -> List[List[str]]:
    groups = defaultdict(list)
    for s in strs:
        cnt = [0] * 26
        for ch in s:
            cnt[ord(ch) - 97] += 1
        groups[tuple(cnt)].append(s)
    return list(groups.values())


if __name__ == "__main__":
    def norm(gs):
        return sorted(sorted(g) for g in gs)

    assert norm(groupAnagrams(["eat", "tea", "tan", "ate", "nat", "bat"])) == norm(
        [["bat"], ["nat", "tan"], ["ate", "eat", "tea"]]
    )
    assert norm(groupAnagrams([""])) == [[""]]
    assert norm(groupAnagrams(["a"])) == [["a"]]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

如果题目允许答案以任意顺序返回，先排序或转成集合再比较；只有题目保证没有重复结果时才适合直接用集合，否则还要检查重复次数。

```python
def norm(gs):
        return sorted(sorted(g) for g in gs)
assert norm(groupAnagrams(["eat", "tea", "tan", "ate", "nat", "bat"])) == norm(
        [["bat"], ["nat", "tan"], ["ate", "eat", "tea"]]
    )
assert norm(groupAnagrams([""])) == [[""]]
assert norm(groupAnagrams(["a"])) == [["a"]]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(nk)$，额外空间 $O(nk)$。$n$ 是单词数，$k$ 是最长单词长度。用排序串当 key 就是 $O(nk\log k)$。

## 边界

空串自己成一组，单个字符也是一组。全部相同就只有一组，全部互不相同就每个词一组。

## 追问

**只判断两个串是不是异位词呢？**
那不用分组。我先比长度，再开 26 个桶对 $s$ 加、$t$ 减，全为零就是真。时间 $O(k)$，空间 $O(1)$。这就是 LC 242，单独一张卡 `lc-242-valid-anagram`。分组题的签名函数，就是把异位词判定做成了可哈希的 key；只判断两个串时直接比计数，用不着先分组再看桶大小。

```python
def isAnagram(s, t):
    if len(s) != len(t):
        return False
    cnt = [0] * 26
    for a, b in zip(s, t):
        cnt[ord(a) - 97] += 1
        cnt[ord(b) - 97] -= 1
    return all(c == 0 for c in cnt)
```

**字母表很大，开不了 26 个桶呢？**
用排序后的串当 key，也就是 `''.join(sorted(s))`。异位词排完序结果相同，非异位词几乎不会撞。时间 $O(nk\log k)$，空间还是 $O(nk)$。只有小写字母时计数元组更合适，$O(nk)$ 还不用排序。质数乘积、把计数拼成字符串也能当签名，但溢出和分隔符要自己处理，面试我优先用排序串或 26 元组。

```python
from collections import defaultdict

def groupAnagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        groups["".join(sorted(s))].append(s)
    return list(groups.values())
```

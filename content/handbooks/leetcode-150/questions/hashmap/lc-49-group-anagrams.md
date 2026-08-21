---
id: lc-49-group-anagrams
section: hashmap
order: 5
level: S
title: LC 49 · 字母异位词分组
quick: >-
  把每个串变成可哈希的签名：26 维计数元组，或排序后的串。同一签名丢进同一个桶。时间约
  $O(nk)$。
tags:
  - Hash
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 49. 字母异位词分组
    url: https://leetcode.cn/problems/group-anagrams/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

给定一串单词，把互为字母异位词的分到同一组。组间、组内顺序任意。

## 思路

哈希分组。签名必须对异位词相同、对非异位词不同：

- 计数元组：扫 $k$ 个字符得到长度 26 的次数，`tuple(cnt)` 做 key，总时间 $O(nk)$。
- 排序串：`''.join(sorted(s))` 做 key，总时间 $O(nk\log k)$。

`eat`/`tea`/`ate` 同组，`tan`/`nat` 同组，`bat` 单独。不要用质数乘积当签名：次数一大就溢出。

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

## 复杂度

时间 $O(nk)$，额外空间 $O(nk)$。$n$ 为单词数，$k$ 为最长单词长度。排序 key 则为 $O(nk\log k)$。

## 边界

- 空串单独成组；单字符也是一组。
- 全部相同则只有一组；全部互不相同则每词一组。

## 追问

- **只要判断两个串是不是异位词？** 不必分组。先比长度，再 26 桶对 $s$ 加、$t$ 减，全零即真。时间 $O(k)$，空间 $O(1)$。这就是 LC 242，独立卡见 `lc-242-valid-anagram`。分组题的签名函数其实就是「把异位词判定变成可哈希的 key」；两两判断时直接比计数，不要先分组再看桶大小。

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

- **字母表很大、不能开 26 桶？** 用排序后的串当 key：`''.join(sorted(s))`。异位词排序结果相同，非异位词几乎不会撞。时间 $O(nk\log k)$，空间仍 $O(nk)$。小写 26 反而更稳：计数元组 $O(nk)$、无排序、也不怕 Unicode 规范化问题。质数乘积、把计数拼成字符串都可以当签名，但溢出和分隔符要自己处理，面试优先排序串或 26 元组。

```python
from collections import defaultdict

def groupAnagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        groups["".join(sorted(s))].append(s)
    return list(groups.values())
```

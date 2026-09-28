---
id: lc-49-group-anagrams
section: hashmap
order: 5
level: S
title: LC 49 · 字母异位词分组
quick: >-
  我会给每个串做一个可哈希的签名：26 维计数元组，或者排完序的串。同一签名丢进同一个桶。时间大约
  $O(nk)$。
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

## 题意

给你一串单词，互为字母异位词的分到同一组。组间、组内顺序随便。

## 思路

哈希分组。签名要对异位词相同、对非异位词不同。

- 计数元组：扫 $k$ 个字符得到长度 26 的次数，`tuple(cnt)` 当 key，总时间 $O(nk)$。
- 排序串：`''.join(sorted(s))` 当 key，总时间 $O(nk\log k)$。

`eat`/`tea`/`ate` 同组，`tan`/`nat` 同组，`bat` 单独。别用质数乘积当签名，次数一大就溢出。

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

时间 $O(nk)$，额外空间 $O(nk)$。$n$ 是单词数，$k$ 是最长单词长度。用排序 key 就是 $O(nk\log k)$。

## 边界

- 空串单独成组；单字符也是一组。
- 全部相同就一组；全部互不相同就每词一组。

## 追问

- **只要判断两个串是不是异位词？** 不用分组。我先比长度，再开 26 桶对 $s$ 加、$t$ 减，全零就是真。时间 $O(k)$，空间 $O(1)$。这就是 LC 242，独立卡见 `lc-242-valid-anagram`。分组题的签名函数，就是把异位词判定做成可哈希的 key；两两判断时直接比计数，别先分组再看桶大小。

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

- **字母表很大、不能开 26 桶？** 用排序后的串当 key：`''.join(sorted(s))`。异位词排序结果相同，非异位词几乎不会撞。时间 $O(nk\log k)$，空间还是 $O(nk)$。小写 26 用计数元组更合适：$O(nk)$、不用排序。质数乘积、把计数拼成字符串都能当签名，但溢出和分隔符要自己处理，面试我优先排序串或 26 元组。

```python
from collections import defaultdict

def groupAnagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        groups["".join(sorted(s))].append(s)
    return list(groups.values())
```

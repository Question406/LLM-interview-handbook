---
id: lc-242-valid-anagram
section: hashmap
order: 4
level: S
title: LC 242 · 有效的字母异位词
quick: >-
  长度不等直接否。26 桶对 $s$ 加、$t$ 减，全 $0$ 即异位词。时间 $O(n)$，或排序后比串
  $O(n\log n)$。
tags:
  - Hash
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 242. 有效的字母异位词
    url: https://leetcode.cn/problems/valid-anagram/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

判断 $t$ 是否为 $s$ 的字母异位词：字符种类与次数完全相同，顺序可以不同。默认小写。

## 思路

哈希计数：长度先剪枝，再一个 26 维数组对 $s$ 加一对 $t$ 减一，最后全零。排序后比较也行，少写几行但多 $\log n$。`aacc` 与 `ccac` 不是异位词，次数对不上。

白板我先问清字符集：只有小写用数组，否则用哈希表。

## 参考代码

```python
def isAnagram(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    cnt = [0] * 26
    for a, b in zip(s, t):
        cnt[ord(a) - 97] += 1
        cnt[ord(b) - 97] -= 1
    return all(c == 0 for c in cnt)


if __name__ == "__main__":
    assert isAnagram("anagram", "nagaram") is True
    assert isAnagram("rat", "car") is False
    assert isAnagram("a", "ab") is False
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。排序写法时间为 $O(n\log n)$。

## 边界

- 空串对空串为真；长度不等直接假。
- 只有一个字符不同或次数差一，26 桶扫完会留下非零。

## 追问

- **字符集是 Unicode / 任意字符？** 26 桶会越界。改用哈希表对 $s$ 加、$t$ 减，或直接 `Counter(s) == Counter(t)`。仍先比长度，不相等必假。时间 $O(n)$，空间 $O(|\Sigma|)$，$\Sigma$ 是实际出现过的字符。大小写敏感要先问清；若忽略大小写，两边先 `.lower()`。不要排序后比串再声称 $O(n)$，排序是 $O(n\log n)$。

```python
from collections import Counter

def isAnagram(s, t):
    return len(s) == len(t) and Counter(s) == Counter(t)
```

- **分组所有异位词（LC 49）？** 每个词做成可哈希签名，签名相同的丢进同一个桶。小写 26 用计数元组 `tuple(cnt)`，总时间 $O(nk)$；字母表很大就用排序串 `''.join(sorted(s))`，时间 $O(nk\log k)$。`eat`/`tea`/`ate` 同组。不要用质数乘积当签名，次数一大就溢出。独立卡见 `lc-49-group-anagrams`。

```python
from collections import defaultdict

def groupAnagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        cnt = [0] * 26
        for ch in s:
            cnt[ord(ch) - 97] += 1
        groups[tuple(cnt)].append(s)
    return list(groups.values())
```

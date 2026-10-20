---
id: lc-383-ransom-note
section: hashmap
order: 1
level: A
title: LC 383 · 赎金信
quick: >-
  统计 `magazine` 各字母次数，再扫 `ransomNote` 逐个减。任一字母减到负数则不够。时间
  $O(m+n)$，额外空间 $O(1)$（26 桶）。
tags:
  - Hash
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 383. 赎金信
    url: https://leetcode.cn/problems/ransom-note/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

判断能否用 `magazine` 里的字母拼出 `ransomNote`。每个字母只能用一次，大小写均为小写。

## 思路

哈希计数：先把杂志里每个字符的出现次数记进 26 维桶（或 `Counter`）。再扫赎金信，每用一个字母就把对应计数减一；减到小于 $0$ 说明缺货。杂志更长时，先计数短串再去长串里扣，写法对称。

常见误区是：做成子序列。这是多重集合包含，字母顺序无关。

## 参考代码

```python
def canConstruct(ransomNote: str, magazine: str) -> bool:
    cnt = [0] * 26
    for ch in magazine:
        cnt[ord(ch) - 97] += 1
    for ch in ransomNote:
        i = ord(ch) - 97
        cnt[i] -= 1
        if cnt[i] < 0:
            return False
    return True


if __name__ == "__main__":
    assert canConstruct("a", "b") is False
    assert canConstruct("aa", "ab") is False
    assert canConstruct("aa", "aab") is True
    print("ok")
```

## 复杂度

时间 $O(m+n)$，额外空间 $O(1)$。$m$、$n$ 为两串长度；字母表固定 26。

## 边界

- `ransomNote` 为空：一个字母都不用，恒真。
- `magazine` 更短也可能种类看起来够，但某字母次数不够，减到负数就该停。

## 追问

- **Unicode / 任意字符怎么办？** 26 桶假设小写拉丁字母。改成 `Counter` 或普通哈希表：先扫杂志加次数，再扫赎金信减，减到 $\lt 0$ 返回假。时间仍 $O(m+n)$，空间 $O(|\Sigma|)$。大小写是否合并要先问清。不要把它做成子序列题：顺序无关，只看多重集合包含。

```python
from collections import Counter

def canConstruct(note, mag):
    cnt = Counter(mag)
    for ch in note:
        cnt[ch] -= 1
        if cnt[ch] < 0:
            return False
    return True
```

- **要输出一种具体取法？** 杂志侧按字符把下标推进队列；赎金信每要一个字母就弹出该字母最早（或任意）一个下标。某字母队列空则拼不出。返回的下标列表就是一种取法，时间 $O(m+n)$。若还要求下标递增且尽量靠左，弹出最早下标即可，因为队列本身按出现顺序入队。这是多重匹配，不是最短覆盖子串。

```python
from collections import defaultdict, deque

def constructIndices(note, mag):
    pos = defaultdict(deque)
    for i, ch in enumerate(mag):
        pos[ch].append(i)
    used = []
    for ch in note:
        if not pos[ch]:
            return None
        used.append(pos[ch].popleft())
    return used
```

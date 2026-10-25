---
id: lc-383-ransom-note
section: hashmap
order: 1
level: A
title: LC 383 · 赎金信
quick: >-
  先统计 `magazine` 每个字母的次数，再扫 `ransomNote` 逐个减一，任何字母减到负数就说明不够用。时间 $O(m+n)$，额外空间 $O(1)$（26 个桶）。
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

## 题目描述

给定目标文本 ransomNote 和可用字母串 magazine，判断能否用 magazine 提供的字母拼出整个 ransomNote。magazine 的每个字符位置最多使用一次，字母可以重新排列；同一个字母需要按出现次数消耗。

### 输入与输出

实现 `canConstruct(ransomNote: str, magazine: str) -> bool`，能够拼出返回 `True`，否则返回 `False`。不需要返回选用了 magazine 中哪些位置。

### 约束

- 两个字符串长度均为 1 到 `10^5`。
- 两个字符串都只包含小写英文字母。

### 示例

```text
输入：ransomNote = "a", magazine = "b"
输出：false
```

magazine 没有字母 a，因此无法构造目标 a。

## 解题思路与参考答案

## 题意

判断能不能用 `magazine` 里的字母拼出 `ransomNote`。每个字母只能用一次，全部是小写。

## 思路

我会用哈希计数。这题是多重集合包含，和字母顺序无关，常见误区是把它做成子序列。先把杂志里每个字符出现的次数记进 26 维桶（或者 `Counter`），再扫赎金信，每用一个字母就把对应计数减一，减到小于 $0$ 就说明缺货。

比如 `ransomNote = "aa"`、`magazine = "ab"`：杂志里 `a` 只有一个，第二个 `a` 一减就变成 $-1$，返回假；杂志换成 `"aab"` 就够用了。

杂志更长时，也可以先给短串计数再去长串里扣，写法是对称的。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert canConstruct("a", "b") is False
assert canConstruct("aa", "ab") is False
assert canConstruct("aa", "aab") is True
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(m+n)$，额外空间 $O(1)$。$m$、$n$ 是两个串的长度，字母表固定 26 个。

## 边界

`ransomNote` 为空时一个字母都不用，恒为真。`magazine` 更短时字母种类也可能看起来够，但某个字母次数不够，减到负数就该停。

## 追问

**字符是 Unicode 或任意字符呢？**
26 个桶假设的是小写拉丁字母，换成 `Counter` 或普通哈希表就行：先扫杂志加次数，再扫赎金信减，减到 $\lt 0$ 返回假。时间仍是 $O(m+n)$，空间 $O(|\Sigma|)$。大小写要不要合并先问清楚。顺序在这里无关，只看多重集合包含，别做成子序列。

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

**要输出一种具体取法呢？**
杂志这边按字符把下标推进各自的队列，赎金信每要一个字母，就弹出这个字母最早（或任意）的一个下标；某个字母的队列空了就拼不出。返回的下标列表就是一种取法，时间 $O(m+n)$。如果还要求下标递增且尽量靠左，弹出最早的下标就行，因为队列本身就是按出现顺序入队的。这是多重匹配，和最短覆盖子串是两类题。

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

---
id: lc-290-word-pattern
section: hashmap
order: 3
level: A
title: LC 290 · 单词规律
quick: >-
  `pattern` 与 `s.split()` 等长后做双向映射：字符 $\leftrightarrow$ 单词。一侧冲突或两边长度不等即假。时间
  $O(n)$。
tags:
  - Hash
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 290. 单词规律
    url: https://leetcode.cn/problems/word-pattern/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

`pattern` 里每个字符对应 `s` 按空格切开后的一个单词，且对应是双射。判断 `s` 是否符合该规律。

## 思路

先 `words = s.split()`。长度与 `pattern` 不等直接否。随后与 LC 205 同一套路：维护 `pattern -> word` 与 `word -> pattern`。`abba` 对 `dog cat cat dog` 真；对 `dog cat cat fish` 假；`jquery` 对 `jquery` 是一个单词对多个字符，也假。

不要用 `s.split(" ")` 依赖连续空格；题目保证单词由单个空格分隔。

## 参考代码

```python
def wordPattern(pattern: str, s: str) -> bool:
    words = s.split()
    if len(pattern) != len(words):
        return False
    p2w, w2p = {}, {}
    for p, w in zip(pattern, words):
        if p2w.get(p, w) != w or w2p.get(w, p) != p:
            return False
        p2w[p] = w
        w2p[w] = p
    return True


if __name__ == "__main__":
    assert wordPattern("abba", "dog cat cat dog") is True
    assert wordPattern("abba", "dog cat cat fish") is False
    assert wordPattern("aaaa", "dog cat cat dog") is False
    assert wordPattern("abba", "dog dog dog dog") is False
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(n)$。$n$ 为单词个数（或字符总长）。

## 边界

- 单字符对单个单词为真。
- `pattern` 比单词多或少直接假，先比长度再映射。

## 追问

- **同一单词被两个字符抢？** 这就是 `ab` / `dog dog`：`a\to dog` 写完后，`b` 也想映到 `dog`。只维护 $p\to w$ 会放过，必须同时查 $w\to p$。对称的反例是 `aa` / `dog cat`，两个位置的 `a` 不能映到不同单词。两边都用 `.get(key, default)` 写成「没有就按当前值，有就必须相等」，一次判断能挡住两类冲突。时间 $O(n)$。

- **正则编号版，怎么和 LC 205 统一？** 把序列里每个元素替换成「它第一次出现时的编号」，得到一条规范串。`pattern` 编一次，单词列表编一次，两条编号序列相等当且仅当存在双射。`abba` 与 `dog cat cat dog` 都是 `[0,1,1,0]`；`badc`/`baba` 一条是 `[0,1,2,3]`、一条是 `[0,1,0,1]`，不相等。这和字符版同构是同一套判定，独立卡见 `lc-205-isomorphic-strings`。编号写法不需要两张映射表，但要多一次扫描。

```python
def normalize(seq):
    first, code = {}, []
    for x in seq:
        first.setdefault(x, len(first))
        code.append(first[x])
    return code

def isIsomorphic(s, t):
    return len(s) == len(t) and normalize(s) == normalize(t)
```

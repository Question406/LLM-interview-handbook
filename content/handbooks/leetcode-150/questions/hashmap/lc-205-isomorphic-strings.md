---
id: lc-205-isomorphic-strings
section: hashmap
order: 2
level: A
title: LC 205 · 同构字符串
quick: >-
  建双向映射 $s\to t$ 与 $t\to s$。同一侧已有映射却对不上，或不同字符映射到同一个字符，就不是同构。时间
  $O(n)$。
tags:
  - Hash
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 205. 同构字符串
    url: https://leetcode.cn/problems/isomorphic-strings/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

判断 $s$、$t$ 是否同构：能把 $s$ 的字符一一替换成 $t$ 的字符，且替换规则是双射（不两对一、也不一对两）。

## 思路

只记 $s\to t$ 不够：`foo`/`bar` 里 `o` 不能同时映射到 `a` 和 `r`；`badc`/`baba` 里 `c` 和 `d` 会映射到同一个字符。必须同时维护 $s\to t$ 与 $t\to s$。扫到一对 `(a, b)`：若 `a` 已对应其他字符，或 `b` 已对应其他字符，就失败；否则写入两侧。

长度不同直接否。空串互相同构。

## 参考代码

```python
def isIsomorphic(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    s2t, t2s = {}, {}
    for a, b in zip(s, t):
        if s2t.get(a, b) != b or t2s.get(b, a) != a:
            return False
        s2t[a] = b
        t2s[b] = a
    return True


if __name__ == "__main__":
    assert isIsomorphic("egg", "add") is True
    assert isIsomorphic("foo", "bar") is False
    assert isIsomorphic("paper", "title") is True
    assert isIsomorphic("badc", "baba") is False
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(|\Sigma|)$。$n$ 为串长，字符集通常很小。

## 边界

- 单字符互相同构；空串也同构。
- `aaa`/`bbb` 真：多对一禁止，一对一允许多次使用同一条规则。
- `aba`/`baa` 假：`a` 不能同时映到 `b` 和 `a`。

## 追问

- **只要单射、不要双射？** 单射只禁止「一个原像两个像」，维护 $s\to t$ 即可：已有 `a` 的像却不是当前的 `b` 就失败。本题是同构，必须双射，还要禁止「两个原像抢同一个像」，所以 $t\to s$ 不能省。`badc`/`baba` 就是单射过、双射不过的典型反例：`c` 和 `d` 都想映到 `a`。开口先问清「能不能多对一」，再决定要不要第二张表。时间仍 $O(n)$，空间 $O(|\Sigma|)$。

- **同构到某个模式串（LC 290）？** 把 $t$ 换成按空格切开的单词数组，字符 $\leftrightarrow$ 单词仍是双射，代码几乎一样。先比 `len(pattern)` 和单词数，再同时写 `p2w` 与 `w2p`。`abba` 对 `dog cat cat dog` 真，对 `dog dog dog dog` 假，因为两个字符抢同一个单词。独立卡见 `lc-290-word-pattern`。另一种等价写法是把两侧都编成「首次出现的编号序列」再比较，同构当且仅当编号串相同。

```python
def wordPattern(pattern, s):
    words = s.split()
    if len(pattern) != len(words):
        return False
    p2w, w2p = {}, {}
    for p, w in zip(pattern, words):
        if p2w.get(p, w) != w or w2p.get(w, p) != p:
            return False
        p2w[p], w2p[w] = w, p
    return True
```

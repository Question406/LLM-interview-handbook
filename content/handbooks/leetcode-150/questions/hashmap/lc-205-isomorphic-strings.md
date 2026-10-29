---
id: lc-205-isomorphic-strings
section: hashmap
order: 2
level: A
title: LC 205 · 同构字符串
quick: >-
  同时维护 $s\to t$ 和 $t\to s$ 两张映射表。扫到一对字符时，任一侧已有映射却对不上，就说明出现了一对多或者多对一，不同构。时间
  $O(n)$。
tags:
  - Hash
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 205. 同构字符串
    url: 'https://leetcode.cn/problems/isomorphic-strings/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定两个等长字符串 s 和 t，判断能否用一套固定的字符替换规则把 s 变成 t。s 中同一个字符每次都必须替换成 t 中同一个字符；s 中两个不同字符不能映射到同一个字符。字符允许映射到自身，字符位置及顺序不能改变。

### 输入与输出

实现 `isIsomorphic(s: str, t: str) -> bool`。存在满足条件的一一对应关系时返回 `True`，否则返回 `False`。

### 约束

- `1 <= len(s) == len(t) <= 5 * 10^4`。
- 字符串可以包含任意有效 ASCII 字符，不限于小写字母。

### 示例

```text
输入：s = "egg", t = "add"
输出：true
```

示例中 e 对应 a，g 对应 d；第二个 g 仍对应 d，因此满足要求。

## 解题思路与参考答案

## 题意

判断 $s$、$t$ 是否同构：能把 $s$ 的字符一一替换成 $t$ 的字符，而且替换规则是双射，既不能两个字符换成同一个，也不能一个字符换成两个。

## 思路

我会同时维护 $s\to t$ 和 $t\to s$ 两张表，同构要求双射，只记一个方向会漏掉一类冲突。

两个例子一看就清楚。`foo`/`bar` 里 `o` 先对应 `a`，后来又要对应 `r`，这种一对多 $s\to t$ 那张表就能拦住。`badc`/`baba` 里单看 $s\to t$，每个字符都只对应一个字符，但 `b` 和 `d` 都被映射成了 `b`，这种多对一只有 $t\to s$ 那张表能发现。

扫到一对 `(a, b)` 时，如果 `a` 已经对应别的字符，或者 `b` 已经被别的字符占了，就失败；否则两边都写上。长度不同直接返回否，空串互相同构。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert isIsomorphic("egg", "add") is True
assert isIsomorphic("foo", "bar") is False
assert isIsomorphic("paper", "title") is True
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(|\Sigma|)$。$n$ 是串长，字符集通常很小。

## Edge Cases

单个字符互相同构，空串也同构。`aaa`/`bbb` 是真，禁止的是多对一，同一条一对一的规则可以反复用。`aba`/`baa` 是假，`a` 不能同时映到 `b` 和 `a`。

## 追问

**只要求单射、不要求双射呢？**
那只维护 $s\to t$ 就够了：`a` 已经有像，却不是当前的 `b`，就失败。单射只禁止「一个原像两个像」。本题是同构，要双射，还得禁止「两个原像抢同一个像」，所以 $t\to s$ 省不掉。`badc`/`baba` 就是单射能过、双射不过的典型反例，`b` 和 `d` 都想映到 `b`。开口先问清能不能多对一，再决定要不要第二张表。时间仍是 $O(n)$，空间 $O(|\Sigma|)$。

**同构到一个单词模式（LC 290）呢？**
把 $t$ 换成按空格切开的单词数组，字符 $\leftrightarrow$ 单词仍然是双射，代码几乎一样。先比 `len(pattern)` 和单词数，再同时写 `p2w` 和 `w2p`。`abba` 对 `dog cat cat dog` 是真，对 `dog dog dog dog` 是假，因为两个字符抢同一个单词。单独一张卡 `lc-290-word-pattern`。还有一种等价写法：把两边都编成「首次出现的编号序列」再比较，同构当且仅当两条编号串相同。

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

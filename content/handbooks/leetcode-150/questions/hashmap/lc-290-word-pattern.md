---
id: lc-290-word-pattern
section: hashmap
order: 3
level: A
title: LC 290 · 单词规律
quick: >-
  先 `s.split()`，单词数和 `pattern` 长度不等直接返回假。然后像 LC 205 一样做字符 $\leftrightarrow$ 单词的双向映射，任一侧冲突就是假，时间 $O(n)$。
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

## 题目描述

给定模式字符串 `pattern` 和由空格分隔的单词串 `s`，判断它们是否遵守同一种一一对应关系。pattern 中每个字符对应 s 中相同位置的一个完整单词；相同字符必须始终对应相同单词，不同字符不能对应同一个单词。字符数量与单词数量也必须相同。

### 输入与输出

实现 `wordPattern(pattern, s) -> bool`。满足双向一一对应返回 True，否则返回 False。单词以一个空格分隔，不把单词内部字符逐个与模式字符比较。

### 约束

- `1 <= len(pattern) <= 300`，pattern 只含小写英文字母。
- `1 <= len(s) <= 3000`，s 只含小写英文字母和空格。
- s 没有首尾空格，相邻单词之间恰有一个空格。

### 示例

```text
输入：pattern = "abba", s = "dog cat cat dog"
输出：true
```

[LeetCode 原题](https://leetcode.com/problems/word-pattern/description/)

## 解题思路与参考答案

## 题意

`pattern` 里每个字符对应 `s` 按空格切开后的一个单词，而且这种对应是双射。判断 `s` 是否符合这个规律。

## 思路

这题和 LC 205 是同一个套路，只是把 $t$ 的字符换成了单词。我先 `words = s.split()`，长度和 `pattern` 不等直接返回否，然后同时维护 `pattern -> word` 和 `word -> pattern` 两张表。

`abba` 对 `dog cat cat dog`：`a` 对 `dog`、`b` 对 `cat`，后面两个位置都对得上，是真。对 `dog cat cat fish`，最后一个 `a` 要对应 `fish`，和 `dog` 冲突，是假。`jquery` 对 `jquery` 也是假，`s` 只有一个单词，却要对应多个字符。

切分用默认的 `split()` 就行。`s.split(" ")` 遇到连续空格会拆出空串；题目保证单词之间是单个空格，默认 `split()` 足够。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert wordPattern("abba", "dog cat cat dog") is True
assert wordPattern("abba", "dog cat cat fish") is False
assert wordPattern("aaaa", "dog cat cat dog") is False
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(n)$。$n$ 是单词个数（或字符总长）。

## 边界

单个字符对单个单词是真。`pattern` 比单词多或者少都直接是假，所以先比长度再做映射。

## 追问

**两个字符对应同一个单词怎么办？**
这就是 `ab` / `dog dog`：写完 `a\to dog` 之后，`b` 也想映到 `dog`。只维护 $p\to w$ 会放过它，必须同时查 $w\to p$。对称的反例是 `aa` / `dog cat`，两个位置的 `a` 不能映到不同单词。两边都用 `.get(key, default)` 写成「没有就按当前值，有就必须相等」，一次判断就能挡住这两类冲突。时间 $O(n)$。

**用编号的写法，怎么和 LC 205 统一？**
把序列里每个元素换成「它第一次出现时的编号」，得到一条规范串。`pattern` 编一次，单词列表编一次，两条编号序列相等当且仅当存在双射。`abba` 和 `dog cat cat dog` 都编成 `[0,1,1,0]`；`badc`/`baba` 一条是 `[0,1,2,3]`、一条是 `[0,1,0,1]`，不相等。这和字符版同构是同一套判定，单独一张卡 `lc-205-isomorphic-strings`。编号写法不需要两张映射表，但要多扫一遍。

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

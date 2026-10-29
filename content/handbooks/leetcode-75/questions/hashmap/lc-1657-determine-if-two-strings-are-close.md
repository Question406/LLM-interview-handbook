---
id: lc-1657-determine-if-two-strings-are-close
section: hashmap
order: 3
level: S
title: LC 1657 · 确定两个字符串是否接近
quick: >-
  两串接近，当且仅当出现的字符集合相同、且频次排序后相同。操作 1 让顺序无关，操作 2 让频次能在已出现的字符之间任意重新分配。时间 $O(n)$，额外空间
  $O(1)$（字符集 26）。
tags:
  - String
  - Hash
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 1657. Determine if Two Strings Are Close
    url: 'https://leetcode.com/problems/determine-if-two-strings-are-close/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定两个字符串，你可以对任意一个字符串反复进行两种操作：交换任意两个位置上的字符；或者选择当前字符串中已经存在的两个不同字符，把其中一种的全部出现同时换成另一种，反之亦然。判断是否能够把两个字符串变成相同的字符串。

### 输入与输出

实现 `closeStrings(word1, word2) -> bool`。交换字符种类是整串同时交换，不是只替换某一个位置，也不能凭空引入从未出现过的新字符。满足转换条件返回 True，否则返回 False。

### 约束与约定

- `1 <= len(word1),len(word2) <= 100000`。
- 两个字符串只含小写英文字母，两种操作都不改变字符串长度。

### 示例

```text
输入：word1 = "abc", word2 = "bca"
输出：true
```

abc 与 bca 仅调整字符位置即可相同，因此是接近的字符串。

[官方原题与完整题面](https://leetcode.com/problems/determine-if-two-strings-are-close/description/)。

## 解题思路与参考答案

## 题意

两个小写字母串 `word1`、`word2`。可以对任一字符串反复做两种操作：

- 操作 1：交换任意两个字符的位置。
- 操作 2：选两个已经出现的字符 `a`、`b`，把所有 `a` 变成 `b`、所有 `b` 变成 `a`。

能把 `word1` 变成 `word2` 就返回 `true`。长度 $\le 10^5$。

## 思路

这题我会先找两种操作下不变的东西，再用 `Counter` 比较，不去模拟操作。操作 1 不改任何字符的频次。操作 2 只是把两个字符的频次对调，字符集合不变，频次的多重集合也不变。所以有两个必要条件：字符集合相同，频次排序后相同。

这两个条件也是充分的。字符集合相同时，操作 2 等于在这些字符之间交换频次，任何一种排列都能由若干次交换得到，所以能把频次分配调成和 `word2` 一样；频次一致之后，再用操作 1 把顺序排好。长度不同的情况，在比较频次时会自动被排除。

拿 `"cabbba"` 和 `"abbccc"` 看：前者是 `a` 2 次、`b` 3 次、`c` 1 次，后者是 `a` 1 次、`b` 2 次、`c` 3 次。字符集合都是 $\{a,b,c\}$，频次排序后都是 $[1,2,3]$，所以是 `true`。

代码就是用 `Counter` 比较 `keys` 和排序后的 `values`。

## 参考代码

```python
from collections import Counter


def closeStrings(word1: str, word2: str) -> bool:
    if len(word1) != len(word2):
        return False
    c1, c2 = Counter(word1), Counter(word2)
    return c1.keys() == c2.keys() and sorted(c1.values()) == sorted(c2.values())


if __name__ == "__main__":
    assert closeStrings("abc", "bca") is True
    assert closeStrings("a", "aa") is False
    assert closeStrings("cabbba", "abbccc") is True
    assert closeStrings("uau", "ssx") is False
    assert closeStrings("aab", "bbb") is False
    assert closeStrings("aabbb", "aaabb") is True
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

如果题目允许答案以任意顺序返回，先排序或转成集合再比较；只有题目保证没有重复结果时才适合直接用集合，否则还要检查重复次数。

```python
assert closeStrings("abc", "bca") is True
assert closeStrings("a", "aa") is False
assert closeStrings("cabbba", "abbccc") is True
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$：计数是线性的，排序最多 $26$ 个频次，是常数。额外空间 $O(1)$。

## Edge Cases

长度不同，直接 `false`。

频次多重集合相同、字符集合不同，比如 `"uau"` 和 `"ssx"`，操作 2 没法凭空造出没出现过的字符，`false`。

字符集合相同、频次多重集合不同，比如 `"aabbb"` 和 `"abbbb"`，$\{2,3\}$ 对 $\{1,4\}$，`false`。

## 追问

**只允许操作 1 呢？**
那就是变位词判断，`Counter(word1) == Counter(word2)`。

**操作 2 允许换成没出现过的字母呢？**
字符集合的限制就没了，只剩频次多重集合相同这一个条件。

```python
from collections import Counter


def closeStringsAnyLetter(word1, word2):
    return sorted(Counter(word1).values()) == sorted(Counter(word2).values())
```

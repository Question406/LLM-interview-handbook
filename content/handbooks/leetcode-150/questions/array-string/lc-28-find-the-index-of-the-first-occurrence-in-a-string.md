---
id: lc-28-find-the-index-of-the-first-occurrence-in-a-string
section: array-string
order: 23
level: A
title: LC 28 · 找出字符串中第一个匹配项的下标
quick: >-
  先写朴素匹配：枚举起点，逐字符和 `needle` 比，找不到返回 $-1$，最坏 $O(nm)$。再提一句 KMP，主串指针不回头，可以做到
  $O(n+m)$。
tags:
  - String
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 28. 找出字符串中第一个匹配项的下标
    url: >-
      https://leetcode.cn/problems/find-the-index-of-the-first-occurrence-in-a-string/
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定两个字符串 `haystack` 和 `needle`，查找 `needle` 是否完整、连续地出现在 `haystack` 中。若出现多次，取最靠左的一次；不能跳过字符进行匹配。

### 输入与输出

实现 `strStr(haystack, needle) -> int`。返回第一次匹配的起始下标，下标从 0 开始；不存在时返回 -1。

### 约束

- 两个字符串长度均在 1 到 `10^4` 之间。
- 字符串只包含小写英文字母。

### 示例

```text
输入：haystack = "sadbutsad", needle = "sad"
输出：0
```

[LeetCode 原题](https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/description/)

## 解题思路与参考答案

## 题意

在 `haystack` 中找出 `needle` 第一次出现的下标；不存在返回 $-1$。等价于 `str.index` / `strstr`。

## 思路

我会先写朴素匹配，它最短、最不容易错，然后口述 KMP。朴素做法是起点 $i$ 从 $0$ 到 $n-m$，比较 `haystack[i:i+m] == needle`。拿 `"sadbutsad"` 找 `"sad"`：起点 $0$ 一比就中，返回 $0$。`needle` 为空（$m=0$）时题面一般约定返回 $0$，不过本题 `needle` 非空。

KMP 先对 `needle` 建最长真前后缀表（`lps` / `next`），匹配失败时只回退模式串，主串不回头，所以是线性的。

## 参考代码

```python
def strStr(haystack: str, needle: str) -> int:
    n, m = len(haystack), len(needle)
    if m == 0:
        return 0
    for i in range(n - m + 1):
        if haystack[i : i + m] == needle:
            return i
    return -1


if __name__ == "__main__":
    assert strStr("sadbutsad", "sad") == 0
    assert strStr("leetcode", "leeto") == -1
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert strStr("sadbutsad", "sad") == 0
assert strStr("leetcode", "leeto") == -1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

朴素最坏 $O((n-m+1)m)$，平均情况更好。KMP 时间 $O(n+m)$，额外空间 $O(m)$。

## Edge Cases

`needle` 等于整段 `haystack` 时，起点 $0$ 一次比完就返回 $0$。只在末尾匹配时起点要扫到 $n-m$，写成 `range(n-m)` 会漏掉最后一次。完全没有公共子串时所有窗口都失败，返回 $-1$。

## 追问

**KMP 和 Rabin-Karp 怎么讲？**
KMP 的核心是主串不回头。朴素做法最坏每个起点都比 $m$ 个字符，时间 $O((n-m+1)m)$。KMP 先对 `needle` 建 `lps`，`lps[i]` 是 `needle[:i+1]` 的最长真前后缀长度；主串指针 `i` 只增不减，模式失配时 `j = lps[j-1]`，建表加匹配共 $O(n+m)$，额外空间 $O(m)$。最容易写错的是回退：要回到 `lps[j-1]`，写成 `j-1` 就错了；匹配成功后如果还要继续找，也得先回退。Rabin-Karp 用滚动哈希比较窗口，平均 $O(n+m)$，但哈希碰撞时必须再比一次字符串，最坏仍是 $O(nm)$。白板上先写对朴素，再口述 KMP 的「主串不回头」。

```python
def strStr_kmp(haystack, needle):
    n, m = len(haystack), len(needle)
    if m == 0:
        return 0
    lps = [0] * m
    length = 0
    i = 1
    while i < m:
        if needle[i] == needle[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length:
            length = lps[length - 1]
        else:
            i += 1
    i = j = 0
    while i < n:
        if haystack[i] == needle[j]:
            i += 1
            j += 1
            if j == m:
                return i - m
        elif j:
            j = lps[j - 1]
        else:
            i += 1
    return -1


def strStr_rk(haystack, needle):
    n, m = len(haystack), len(needle)
    if m == 0:
        return 0
    if n < m:
        return -1
    base, mod = 256, 10**9 + 7
    power = pow(base, m - 1, mod)
    h_hash = n_hash = 0
    for i in range(m):
        h_hash = (h_hash * base + ord(haystack[i])) % mod
        n_hash = (n_hash * base + ord(needle[i])) % mod
    for i in range(n - m + 1):
        if h_hash == n_hash and haystack[i : i + m] == needle:
            return i
        if i + m < n:
            h_hash = (h_hash - ord(haystack[i]) * power) % mod
            h_hash = (h_hash * base + ord(haystack[i + m])) % mod
            h_hash %= mod
    return -1
```

**要找所有出现位置呢？**
朴素做法每个起点都比完，命中就记下、再试下一个起点，重叠出现（`aaa` 里找 `aa`）不会漏，最坏仍 $O(nm)$。KMP 匹配成功后把 `j` 设成 `lps[j-1]`，别归零，主串 `i` 不动（已经加过了），这样重叠的匹配也能接上，时间 $O(n+m)$。成功后 `i += 1` 再从 $0$ 比会漏掉重叠。另外 `needle` 为空时出现位置是 $0\ldots n$ 共 $n+1$ 个，要先和面试官把定义说好。

```python
def find_all_kmp(haystack, needle):
    n, m = len(haystack), len(needle)
    if m == 0:
        return list(range(n + 1))
    lps = [0] * m
    length = 0
    i = 1
    while i < m:
        if needle[i] == needle[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length:
            length = lps[length - 1]
        else:
            i += 1
    ans = []
    i = j = 0
    while i < n:
        if haystack[i] == needle[j]:
            i += 1
            j += 1
            if j == m:
                ans.append(i - m)
                j = lps[j - 1]
        elif j:
            j = lps[j - 1]
        else:
            i += 1
    return ans
```

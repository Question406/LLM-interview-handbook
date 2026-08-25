---
id: lc-28-find-the-index-of-the-first-occurrence-in-a-string
section: array-string
order: 23
level: A
title: LC 28 · 找出字符串中第一个匹配项的下标
quick: >-
  朴素匹配：枚举起点，逐字符比 `needle`。找不到返回 $-1$。时间最坏 $O(nm)$。我会提一句 KMP 可到
  $O(n+m)$。
tags:
  - String
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 28. 找出字符串中第一个匹配项的下标
    url: https://leetcode.cn/problems/find-the-index-of-the-first-occurrence-in-a-string/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

在 `haystack` 中找出 `needle` 第一次出现的下标；不存在返回 $-1$。等价于 `str.index` / `strstr`。

## 思路

朴素：起点 $i$ 从 $0$ 到 $n-m$，比较 `haystack[i:i+m] == needle`。$m=0$ 按题面一般返回 $0$，但本题 `needle` 非空。

KMP：先对 `needle` 建最长真前后缀表（`lps` / `next`），匹配失败时模式串回退而主串不回头，线性。白板我一般先写对朴素，再口述 KMP。

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

## 复杂度

朴素最坏 $O((n-m+1)m)$，平均更好。KMP 时间 $O(n+m)$，额外空间 $O(m)$。

## 边界

- `needle` 等于整段 `haystack`：起点 $0$ 一次比完即返回 $0$。
- 只在末尾匹配：起点要扫到 $n-m$，别写成 `range(n-m)` 漏掉最后一次。
- 完全无公共子串：所有窗口都失败，返回 $-1$。

## 追问

- **KMP / Rabin-Karp？** 朴素最坏每个起点都比 $m$ 个字符，时间 $O((n-m+1)m)$。KMP 先对 `needle` 建 `lps`：`lps[i]` 是 `needle[:i+1]` 最长真前后缀长度。主串指针 `i` 只增不减，模式失配时 `j = lps[j-1]`，建表加匹配共 $O(n+m)$，额外空间 $O(m)$。这块容易栽：`lps` 回退写成 `j-1` 而不是 `lps[j-1]`，以及匹配成功后若还要继续找必须先回退。Rabin-Karp 用滚动哈希比较窗口，平均 $O(n+m)$，哈希碰撞时必须再比一次字符串，最坏仍 $O(nm)$。白板我先写对朴素，再口述 KMP 的「主串不回头」。

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

- **要所有出现位置？** 朴素是每个起点都比完，命中就记下再试下一个起点，重叠出现（`aaa` 里找 `aa`）不会漏，时间仍最坏 $O(nm)$。KMP 匹配成功后不要把 `j` 归零，而是 `j = lps[j-1]`，主串 `i` 不动（已经加过了），这样重叠模式也能接到。时间 $O(n+m)$。这块容易栽：成功后写成 `i += 1` 再从 $0$ 比，会漏重叠；以及 `needle` 为空时出现位置是 $0\ldots n$ 共 $n+1$ 个，要先和面试官定义。

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

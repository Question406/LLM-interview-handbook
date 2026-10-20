---
id: lc-5-longest-palindromic-substring
section: dp-2d
order: 4
level: S
title: LC 5 · 最长回文子串
quick: "分别以每个字符、每对相邻字符为中心，向两侧扩展回文并记录最长区间。也可用 $dp[l][r]=s[l]=s[r]\\land dp[l+1][r-1]$ 判断区间是否回文。两种方法时间都是 $O(n^2)$。"
tags:
  - DP
  - Two Pointers
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 5. 最长回文子串
    url: https://leetcode.cn/problems/longest-palindromic-substring/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

给出字符串 `s`，返回其中最长回文子串。若有多个，返回任意一个即可。

## 思路

中心扩展：回文由中心对称。枚举 $n$ 个奇数中心与 $n-1$ 个偶数中心（相邻两字符），向两侧扩到不能扩，更新最长区间。实现短、常数好。
DP：$dp[l][r]$ 表示 $s[l..r]$ 是否回文。转移是两端相等且内部是回文（长度为 $1$ 或 $2$ 单独初始化）。按长度递增填表。Manacher 是 $O(n)$，白板提到即可。

`babad` 的官方答案可以是 `bab` 或 `aba`。

## 参考代码

```python
def longestPalindrome(s: str) -> str:
    def expand(left: int, right: int) -> tuple:
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return left + 1, right - 1

    start = end = 0
    for i in range(len(s)):
        l1, r1 = expand(i, i)
        l2, r2 = expand(i, i + 1)
        if r1 - l1 > end - start:
            start, end = l1, r1
        if r2 - l2 > end - start:
            start, end = l2, r2
    return s[start : end + 1]


if __name__ == "__main__":
    assert longestPalindrome("babad") in ("bab", "aba")
    assert longestPalindrome("cbbd") == "bb"
    print("ok")
```

## 复杂度

中心扩展与区间 DP 都是时间 $O(n^2)$。扩展额外空间 $O(1)$，DP 额外空间 $O(n^2)$。

## 边界

- 单字符：奇数中心扩不动，答案就是它自己。
- 全相同：奇数、偶数中心都能扩到两端，返回整串。
- 没有长度 $\gt 1$ 的回文：偶数中心全都对不上，`start,end` 停在 $0$，返回首字符。

## 追问

- **区间 DP 怎么写？** $dp[l][r]$ 表示 $s[l..r]$ 是否回文。长度 $1$ 为真；长度 $2$ 看两端相等；更长则两端相等且 $dp[l+1][r-1]$。必须按长度递增填，否则内部还没算。填表时同步更新最长起止。时间 $O(n^2)$，额外 $O(n^2)$，比中心扩展更费空间。

```python
def longestPalindrome_dp(s):
    n = len(s)
    dp = [[False] * n for _ in range(n)]
    start = end = 0
    for i in range(n):
        dp[i][i] = True
    for length in range(2, n + 1):
        for l in range(n - length + 1):
            r = l + length - 1
            if s[l] == s[r] and (length == 2 or dp[l + 1][r - 1]):
                dp[l][r] = True
                if r - l > end - start:
                    start, end = l, r
    return s[start : end + 1]
```

- **最长回文子序列（LC 516）？** 子序列可删字符，不必连续。$dp[i][j]$ 为 $s[i..j]$ 的最长回文子序列长度：两端相等则 $dp[i+1][j-1]+2$，否则 $\max(dp[i+1][j], dp[i][j-1])$。从短区间或从右上填。时间 $O(n^2)$。本题要的是连续子串，不能用这套转移。

```python
def longestPalindromeSubseq(s):
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        dp[i][i] = 1
        for j in range(i + 1, n):
            if s[i] == s[j]:
                dp[i][j] = dp[i + 1][j - 1] + 2
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
    return dp[0][n - 1]
```

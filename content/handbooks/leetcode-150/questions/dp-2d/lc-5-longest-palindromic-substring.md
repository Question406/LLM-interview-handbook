---
id: lc-5-longest-palindromic-substring
section: dp-2d
order: 4
level: S
title: LC 5 · 最长回文子串
quick: "中心扩展：以每个字符、每对相邻字符为中心向两侧扩，记录最长区间，时间 $O(n^2)$、额外空间 $O(1)$。也可用区间 DP $dp[l][r]=s[l]=s[r]\\land dp[l+1][r-1]$ 判断区间是否回文，时间同样 $O(n^2)$，空间要 $O(n^2)$。"
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

## 题目描述

给定非空字符串 `s`，返回其中长度最大的回文子串。子串必须是原字符串中连续的一段；回文表示从左往右与从右往左读完全相同。若存在多个同样长的答案，返回其中任意一个即可。

### 输入与输出

实现 `longestPalindrome(s) -> str`，返回子串内容，不是长度，也不是允许跳过字符的子序列。

### 约束

- `1 <= len(s) <= 1000`。
- 字符串只包含英文字母和数字，大小写按不同字符处理。

### 示例

```text
输入：s = "babad"
输出："bab"
```

[LeetCode 原题](https://leetcode.com/problems/longest-palindromic-substring/description/)

## 解题思路与参考答案

## 题意

给出字符串 `s`，返回其中最长的回文子串；有多个时返回任意一个即可。

## 思路

我会用中心扩展。回文关于中心对称，所以只要枚举中心往两边扩：$n$ 个奇数中心（单个字符）加 $n-1$ 个偶数中心（相邻两字符），扩到两端不相等为止，更新最长区间。代码短，常数也好。

拿 `babad` 来说，以下标 $1$ 的 `a` 为中心，两边都是 `b`，扩出 `bab`；以下标 $2$ 的 `b` 为中心扩出 `aba`。两者一样长，官方答案是 `bab` 或 `aba` 都可以。`cbbd` 要靠偶数中心 `bb` 才能找到答案。

另一种写法是区间 DP：$dp[l][r]$ 表示 $s[l..r]$ 是否回文，两端相等且内部是回文就为真，长度 $1$、$2$ 单独初始化，按长度递增填表，代码放在追问里。Manacher 能做到 $O(n)$，白板上提一句就行。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert longestPalindrome("babad") in ("bab", "aba")
assert longestPalindrome("cbbd") == "bb"
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

中心扩展和区间 DP 时间都是 $O(n^2)$。中心扩展额外空间 $O(1)$，DP 要 $O(n^2)$。

## 边界

单字符时奇数中心扩不动，答案就是它自己。全相同时奇数、偶数中心都能扩到两端，返回整串。没有长度 $\gt 1$ 的回文时，偶数中心全都对不上，`start,end` 停在 $0$，返回首字符。

## 追问

**区间 DP 怎么写？**
$dp[l][r]$ 表示 $s[l..r]$ 是否回文。长度 $1$ 为真；长度 $2$ 看两端是否相等；更长的要两端相等且 $dp[l+1][r-1]$ 为真。必须按长度递增填，否则内部还没算出来。填表时顺便更新最长的起止位置。时间 $O(n^2)$，额外空间 $O(n^2)$，比中心扩展费空间。

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

**最长回文子序列（LC 516）怎么做？**
子序列可以删字符，不要求连续。$dp[i][j]$ 记 $s[i..j]$ 的最长回文子序列长度：两端相等就是 $dp[i+1][j-1]+2$，否则取 $\max(dp[i+1][j], dp[i][j-1])$，从短区间或从右上往回填，时间 $O(n^2)$。本题要的是连续子串，这套转移套不过来。

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

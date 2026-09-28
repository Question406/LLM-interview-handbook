---
id: lc-1143-longest-common-subsequence
section: dp-multi
order: 2
level: S
title: LC 1143 · 最长公共子序列
quick: >-
  $dp[i][j]$ 是 `text1` 前 $i$ 个与 `text2` 前 $j$ 个的 LCS 长度。末字符相等取 $dp[i-1][j-1]+1$，否则 $\max(dp[i-1][j],\,dp[i][j-1])$。时间
  $O(mn)$，额外空间可压到 $O(\min(m,n))$。
tags:
  - DP
  - String
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1143. Longest Common Subsequence
    url: https://leetcode.com/problems/longest-common-subsequence/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

两个字符串 `text1`、`text2`，求最长公共子序列的长度；没有公共子序列返回 $0$。子序列是删掉若干字符（可以不删）、剩余字符保持原相对顺序得到的串，不要求连续。长度都在 $[1, 1000]$，只含小写字母。

## 思路

$dp[i][j]$ 表示 `text1[:i]` 和 `text2[:j]` 的 LCS 长度，$dp[0][\cdot]=dp[\cdot][0]=0$。看两个前缀的末字符：

- 相等：这对字符一定可以放进某个最长公共子序列的末尾，$dp[i][j]=dp[i-1][j-1]+1$。
- 不等：至少有一个末字符用不上，丢掉 `text1` 的或丢掉 `text2` 的，$dp[i][j]=\max(dp[i-1][j],\ dp[i][j-1])$。

相等时不用再和 $\max$ 比，因为 $dp[i-1][j]$ 和 $dp[i][j-1]$ 都不会超过 $dp[i-1][j-1]+1$。暴力枚举一边的所有子序列是 $O(2^m)$。空间上每行只依赖上一行和本行左侧，滚动数组时要单独存左上角的旧值。

## 参考代码

```python
def longestCommonSubsequence(text1: str, text2: str) -> int:
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


if __name__ == "__main__":
    assert longestCommonSubsequence("abcde", "ace") == 3
    assert longestCommonSubsequence("abc", "abc") == 3
    assert longestCommonSubsequence("abc", "def") == 0
    assert longestCommonSubsequence("a", "a") == 1
    assert longestCommonSubsequence("bsbininm", "jmjkbkjkv") == 1
    assert longestCommonSubsequence("oxcpqrsvwf", "shmtulqrypy") == 2
    print("ok")
```

## 复杂度

时间 $O(mn)$，额外空间 $O(mn)$；滚动一行后 $O(\min(m,n))$。

## 边界

- 无公共字符：整张表都是 $0$。
- 两串相同：每步走对角，答案是串长。
- 重复字符（如 `"aaa"` 与 `"aa"`）：转移只看前缀，不会把同一字符用两次，答案 $2$。

## 追问

- **只用一行空间？** `dp[j]` 覆盖前是上一行的值，`dp[j-1]` 已是本行。对角 $dp[i-1][j-1]$ 会被覆盖，所以每格先用 `prev` 暂存旧的 `dp[j]`，下一格拿来当左上角。

```python
def lcs1d(a, b):
    if len(a) < len(b):
        a, b = b, a
    dp = [0] * (len(b) + 1)
    for ca in a:
        prev = 0
        for j, cb in enumerate(b, 1):
            cur = dp[j]
            dp[j] = prev + 1 if ca == cb else max(dp[j], dp[j - 1])
            prev = cur
    return dp[-1]
```

- **要输出 LCS 本身？** 保留二维表，从 $(m,n)$ 回溯：末字符相等就收下并走对角；否则往值更大的那边走（上或左）。收到的字符逆序，最后反转。

```python
def lcsString(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    out, i, j = [], m, n
    while i and j:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i, j = i - 1, j - 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return "".join(reversed(out))
```

- **和编辑距离的关系？** 只允许插入、删除时，最少操作数是 $m+n-2\cdot\mathrm{LCS}$：公共子序列不动，其余字符删掉再插。允许替换就要用 `lc-72-edit-distance` 的三向转移。

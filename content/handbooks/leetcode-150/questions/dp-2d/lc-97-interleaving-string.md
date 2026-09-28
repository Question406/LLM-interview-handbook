---
id: lc-97-interleaving-string
section: dp-2d
order: 5
level: A
title: LC 97 · 交错字符串
quick: >-
  $dp[i][j]$：`s1` 前 $i$ 与 `s2` 前 $j$ 能否交错成 `s3` 前 $i+j$。转移看
  $s3$ 末字符来自 $s1[i-1]$ 还是 $s2[j-1]$。先比长度。
tags:
  - DP
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 97. 交错字符串
    url: https://leetcode.cn/problems/interleaving-string/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

判断 `s3` 是否由 `s1`、`s2` 交错组成：相对顺序保持，只是合并指针交替前进。

## 思路

若 `len(s1)+len(s2) != len(s3)` 直接否。$dp[i][j]$ 为真当且仅当能用两串前缀拼出 `s3` 的前 $i+j$ 个字符。

转移：`dp[i-1][j] and s1[i-1]==s3[i+j-1]`，或 `dp[i][j-1] and s2[j-1]==s3[i+j-1]`。$dp[0][0]=\mathrm{true}$，第一行 / 列只沿一条串走。可压成一维。

错法：双指针贪心。分叉要回溯，得用 DP 或记忆化。

## 参考代码

```python
def isInterleave(s1: str, s2: str, s3: str) -> bool:
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        return False
    dp = [False] * (n + 1)
    dp[0] = True
    for j in range(1, n + 1):
        dp[j] = dp[j - 1] and s2[j - 1] == s3[j - 1]
    for i in range(1, m + 1):
        dp[0] = dp[0] and s1[i - 1] == s3[i - 1]
        for j in range(1, n + 1):
            take1 = dp[j] and s1[i - 1] == s3[i + j - 1]
            take2 = dp[j - 1] and s2[j - 1] == s3[i + j - 1]
            dp[j] = take1 or take2
    return dp[n]


if __name__ == "__main__":
    assert isInterleave("aabcc", "dbbca", "aadbbcbcac") is True
    assert isInterleave("aabcc", "dbbca", "aadbbbaccc") is False
    assert isInterleave("", "", "") is True
    print("ok")
```

## 复杂度

时间 $O(mn)$，额外空间一维 $O(n)$。

## 边界

- 两串都空：`s3` 也必须空，`dp[0]=True`。
- 长度和不相等：字符数对不上，直接否。
- 其中一串为空：另一串必须与 `s3` 完全相等，第一行或第一列按单串匹配滚动。

## 追问

- **贪心为什么错？** 当前字符两串都能接时，先吃 `s1` 可能把后面需要的字符用掉。反例：`s1=aabc`，`s2=abad`，`s3=aabadabc`。若能匹配就优先 `s1`，前三个 `aab` 全从 `s1` 拿走，下一个 `d` 谁都接不上；正确做法是第二个 `a` 起改走 `s2`。分叉要记忆，不能双指针贪心。

```python
def isInterleave_memo(s1, s2, s3):
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        return False
    memo = {}

    def dfs(i, j):
        if i == m and j == n:
            return True
        if (i, j) in memo:
            return memo[(i, j)]
        k = i + j
        ok = False
        if i < m and s1[i] == s3[k] and dfs(i + 1, j):
            ok = True
        if not ok and j < n and s2[j] == s3[k] and dfs(i, j + 1):
            ok = True
        memo[(i, j)] = ok
        return ok

    return dfs(0, 0)
```

- **输出一种交错方案？** 用二维布尔表。从 $(m,n)$ 回溯：若 `dp[i-1][j]` 为真且 `s1[i-1]` 对上 `s3` 当前位，则该字符来自 `s1`；否则来自 `s2`。逆序收集再反转。无方案时 `dp[m][n]` 为假。

```python
def interleave_path(s1, s2, s3):
    m, n = len(s1), len(s2)
    if m + n != len(s3):
        return None
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    for i in range(m + 1):
        for j in range(n + 1):
            k = i + j - 1
            if i and dp[i - 1][j] and s1[i - 1] == s3[k]:
                dp[i][j] = True
            if j and dp[i][j - 1] and s2[j - 1] == s3[k]:
                dp[i][j] = True
    if not dp[m][n]:
        return None
    seq, i, j = [], m, n
    while i or j:
        if i and dp[i - 1][j] and s1[i - 1] == s3[i + j - 1]:
            seq.append(("s1", s1[i - 1]))
            i -= 1
        else:
            seq.append(("s2", s2[j - 1]))
            j -= 1
    seq.reverse()
    return seq
```

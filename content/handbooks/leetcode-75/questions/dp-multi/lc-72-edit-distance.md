---
id: lc-72-edit-distance
section: dp-multi
order: 4
level: S
title: LC 72 · 编辑距离
quick: >-
  $dp[i][j]$：`word1` 前 $i$ 个变成 `word2` 前 $j$ 个的最少操作数。末字符相同抄左上；否则替换、删除、插入分别对应左上 / 上 / 左，取最小再加一。时间
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
  - title: 72. Edit Distance
    url: https://leetcode.com/problems/edit-distance/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

把 `word1` 变成 `word2`，每次操作可以插入、删除或替换一个字符。求最少操作次数。长度都在 $[0, 500]$，只含小写字母。

## 思路

$dp[i][j]$：`word1[:i]` 变到 `word2[:j]` 的最少操作数。边界 $dp[i][0]=i$（全删），$dp[0][j]=j$（全插）。

末字符相同：不用动，$dp[i][j]=dp[i-1][j-1]$。不同则三选一再加一：

$dp[i][j]=1+\min(dp[i-1][j-1],\ dp[i-1][j],\ dp[i][j-1])$

左上是把 `word1[i-1]` 替换成 `word2[j-1]`；上方是删掉 `word1[i-1]`；左方是在末尾插入 `word2[j-1]`。白板我把三种操作对上三个格子讲，不背公式。和 `lc-1143-longest-common-subsequence` 是同一张表的形状，只是那题求最大、这题求最小，并且多了替换这条对角转移。

## 参考代码

```python
def minDistance(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j - 1],
                    dp[i - 1][j],
                    dp[i][j - 1],
                )
    return dp[m][n]


if __name__ == "__main__":
    assert minDistance("horse", "ros") == 3
    assert minDistance("intention", "execution") == 5
    assert minDistance("", "") == 0
    assert minDistance("", "abc") == 3
    assert minDistance("abc", "") == 3
    assert minDistance("abc", "abc") == 0
    assert minDistance("a", "b") == 1
    print("ok")
```

## 复杂度

时间 $O(mn)$，额外空间 $O(mn)$，滚动后 $O(\min(m,n))$。

## 边界

- 一串为空：答案是另一串长度，边界行列已经覆盖。
- 两串相等：每步抄对角，答案 $0$。
- 单字符互异：替换一次即可，答案 $1$。

## 追问

- **只允许插入、删除？** 去掉替换分支：字符不同时只走上或左。答案等于 $m+n-2\cdot\mathrm{LCS}$，公共子序列不用动，其余全删再插。

```python
def minDistanceInsDel(a, b):
    m, n = len(a), len(b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev, dp[0] = dp[0], i
        for j in range(1, n + 1):
            cur = dp[j]
            dp[j] = prev if a[i - 1] == b[j - 1] else 1 + min(dp[j], dp[j - 1])
            prev = cur
    return dp[n]
```

- **一维滚动怎么写，对角会不会脏？** `dp[j]` 写之前是上一行（删除），`dp[j-1]` 已是本行（插入），对角必须是覆盖前的旧 `dp[j]`，用 `prev` 暂存再写。每行开头 `dp[0]` 要更新成 $i$。

```python
def minDistance1d(a, b):
    if len(a) < len(b):
        a, b = b, a
    dp = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev, dp[0] = dp[0], i
        for j, cb in enumerate(b, 1):
            cur = dp[j]
            dp[j] = prev if ca == cb else 1 + min(prev, dp[j], dp[j - 1])
            prev = cur
    return dp[-1]
```

- **要输出操作序列？** 保留二维表，从 $(m,n)$ 回溯：末字符相等走对角；否则看当前值来自左上 $+1$（替换）、上方 $+1$（删除）还是左方 $+1$（插入），平手任选。操作逆序收集再反转。

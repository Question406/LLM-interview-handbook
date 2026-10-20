---
id: lc-72-edit-distance
section: dp-2d
order: 6
level: S
title: LC 72 · 编辑距离
quick: >-
  $dp[i][j]$：`word1` 前 $i$ 变成 `word2` 前 $j$。相同抄对角；否则取替换、删除、插入的最小次数再加一，对应左上 / 上 / 左。
tags:
  - DP
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 72. 编辑距离
    url: https://leetcode.cn/problems/edit-distance/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

把 `word1` 变成 `word2`，可插入、删除、替换一个字符。求最少操作次数。

## 思路

$dp[i][j]$：`word1[:i]` 变到 `word2[:j]`。边界：$dp[i][0]=i$（全删），$dp[0][j]=j$（全插）。

字符相同：`dp[i][j] = dp[i-1][j-1]`。不同：替换来自左上，删除来自上方（丢掉 `word1` 当前），插入来自左方（补上 `word2` 当前），取 $\min$ 再加一。

先说明替换、删除和插入各自对应哪个前置状态，再写状态转移。空间上可压成两行。

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
    print("ok")
```

## 复杂度

时间 $O(mn)$，额外空间 $O(mn)$，滚动后 $O(\min(m,n))$。

## 边界

- 一串为空：边界 $dp[i][0]=i$、$dp[0][j]=j$，答案是另一串长度。
- 两串相等：每步抄对角，答案 $0$。
- 单字符互异：替换一次，或删再插，最少 $1$。

## 追问

- **只允许插入、删除？** 去掉替换分支：字符不同时只走「删 = 上」或「插 = 左」。替换代价若改成 $2$，最优解也不会选它，因为删+插恰好是 $2$。这与 $m+n-2\cdot\mathrm{LCS}$ 等价：公共子序列不用动，其余全删再插。

```python
def minDistance_ins_del(a, b):
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

- **输出操作序列？** 填表时不必另开选择数组：从 $(m,n)$ 回溯。两端相等就匹配并走对角；否则看当前值来自对角 $+1$（替换）、上方 $+1$（删 `word1`）还是左方 $+1$（插 `word2`），平手任选。操作逆序收集再反转。

```python
def edit_ops(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = (
                dp[i - 1][j - 1]
                if a[i - 1] == b[j - 1]
                else 1 + min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1])
            )
    ops, i, j = [], m, n
    while i or j:
        if i and j and a[i - 1] == b[j - 1]:
            i, j = i - 1, j - 1
        elif i and j and dp[i][j] == dp[i - 1][j - 1] + 1:
            ops.append(("replace", a[i - 1], b[j - 1]))
            i, j = i - 1, j - 1
        elif i and dp[i][j] == dp[i - 1][j] + 1:
            ops.append(("delete", a[i - 1]))
            i -= 1
        else:
            ops.append(("insert", b[j - 1]))
            j -= 1
    ops.reverse()
    return dp[m][n], ops
```

- **一维滚动数组会覆盖对角状态吗？** 关键是更新顺序：`dp[j]` 写之前是上一行（删除），`dp[j-1]` 已是本行（插入），对角必须是覆盖前的旧 `dp[j]`。用 `prev` 暂存再写。字符相同直接抄 `prev`，不要再 `min` 一遍。

```python
def minDistance_1d(a, b):
    if len(a) < len(b):
        a, b = b, a
    n, dp = len(b), list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev, dp[0] = dp[0], i
        for j, cb in enumerate(b, 1):
            cur = dp[j]
            dp[j] = prev if ca == cb else 1 + min(prev, dp[j], dp[j - 1])
            prev = cur
    return dp[n]
```

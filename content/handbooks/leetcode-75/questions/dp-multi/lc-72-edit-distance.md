---
id: lc-72-edit-distance
section: dp-multi
order: 4
level: S
title: LC 72 · 编辑距离
quick: "令 $dp[i][j]$ 为 `word1` 前 $i$ 个变成 `word2` 前 $j$ 个的最少操作数。末字符相同就抄左上；不同时替换、删除、插入分别对应左上、上、左，取最小再加一。时间 $O(mn)$，额外空间可压到 $O(\\min(m,n))$。"
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

## 题目描述

给定两个字符串，允许对第一个字符串进行三种单位代价操作：插入一个字符、删除一个字符，或把一个字符替换成另一个字符。求把第一个字符串变成第二个所需的最少操作次数。

### 输入与输出

实现 `minDistance(word1, word2) -> int`，返回最少次数，不要求返回具体编辑过程。字符串可以为空，字符顺序必须按编辑结果匹配。

### 约束与约定

- 两个字符串的长度均在 0 到 500 之间。
- 非空字符均为小写英文字母。

### 示例

```text
输入：word1 = "horse", word2 = "ros"
输出：3
```

horse 可以用三次允许的编辑变成 ros；不要求输出这三次编辑的具体位置。

[官方原题与完整题面](https://leetcode.com/problems/edit-distance/description/)。

## 解题思路与参考答案

## 题意

把 `word1` 变成 `word2`，每次操作可以插入、删除或替换一个字符。求最少操作次数。长度都在 $[0, 500]$，只含小写字母。

## 思路

这是两个前缀对齐的二维 DP，三种操作正好对应三个前置格子。$dp[i][j]$ 是 `word1[:i]` 变到 `word2[:j]` 的最少操作数。边界 $dp[i][0]=i$（全删），$dp[0][j]=j$（全插）。

末字符相同就不用动，$dp[i][j]=dp[i-1][j-1]$。不同的话三选一再加一：

$dp[i][j]=1+\min(dp[i-1][j-1],\ dp[i-1][j],\ dp[i][j-1])$

左上是把 `word1[i-1]` 替换成 `word2[j-1]`；上方是删掉 `word1[i-1]`；左方是在末尾插入 `word2[j-1]`。我会先讲清楚每种操作依赖哪个前置状态，再写公式。

拿 `"horse"` 变 `"ros"` 看：把 `h` 换成 `r`，删掉中间的 `r`，再删掉 `e`，三步，表格右下角也正好是 $3$。

它和 `lc-1143-longest-common-subsequence` 是同一张表的形状，那题求最大、这题求最小，并且多了替换这条对角转移。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert minDistance("horse", "ros") == 3
assert minDistance("intention", "execution") == 5
assert minDistance("", "") == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(mn)$，额外空间 $O(mn)$，滚动后 $O(\min(m,n))$。

## 边界

一个串为空时，答案就是另一个串的长度，边界行列已经覆盖。

两串相等时每步都抄对角，答案 $0$。

两个不同的单字符，替换一次就行，答案 $1$。

## 追问

**只允许插入和删除呢？**
去掉替换分支，字符不同时只走上或左。答案等于 $m+n-2\cdot\mathrm{LCS}$：公共子序列不动，其余全删再插。

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

**一维滚动怎么写，对角状态会不会被覆盖？**
会，所以要暂存。`dp[j]` 写之前是上一行（对应删除），`dp[j-1]` 已经是本行（对应插入），对角必须是覆盖前的旧 `dp[j]`，用 `prev` 先存下来再写。每行开头的 `dp[0]` 要更新成 $i$。

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

**要输出具体的操作序列呢？**
保留二维表，从 $(m,n)$ 往回走：末字符相等就走对角；否则看当前值来自左上 $+1$（替换）、上方 $+1$（删除）还是左方 $+1$（插入），打平就任选一个。操作是逆序收集的，最后反转。

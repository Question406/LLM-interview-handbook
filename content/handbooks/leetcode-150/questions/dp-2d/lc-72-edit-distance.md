---
id: lc-72-edit-distance
section: dp-2d
order: 6
level: S
title: LC 72 · 编辑距离
quick: "$dp[i][j]$ 是 `word1` 前 $i$ 个字符变成 `word2` 前 $j$ 个字符的最少操作数。末字符相同就抄左上；不同就在替换（左上）、删除（上）、插入（左）里取最小再加一，时间 $O(mn)$。"
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

把 `word1` 变成 `word2`，每次可以插入、删除或替换一个字符，求最少操作次数。

## 思路

我会用二维 DP 比较两个前缀。$dp[i][j]$ 表示把 `word1[:i]` 变成 `word2[:j]` 的最少操作数。边界是 $dp[i][0]=i$（全删）、$dp[0][j]=j$（全插）。

末字符相同时不用动，`dp[i][j] = dp[i-1][j-1]`。不同时有三种做法：替换来自左上，删除来自上方（丢掉 `word1` 的当前字符），插入来自左方（补上 `word2` 的当前字符），取 $\min$ 再加一。拿 `horse` 变 `ros` 来说，答案是 $3$：`h` 换成 `r`，删掉 `r`，再删掉 `e`。

面试时先讲清替换、删除和插入各自对应哪个前置状态，再写状态转移。空间上可以压成两行。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert minDistance("horse", "ros") == 3
assert minDistance("intention", "execution") == 5
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(mn)$，额外空间 $O(mn)$，滚动后 $O(\min(m,n))$。

## 边界

一串为空时，按边界 $dp[i][0]=i$、$dp[0][j]=j$，答案就是另一串的长度。两串相等时每步都抄对角，答案 $0$。单字符互异时替换一次，或者删一次再插一次，最少是 $1$。

## 追问

**只允许插入和删除呢？**
去掉替换分支，字符不同时只走「删 = 上」或「插 = 左」。替换代价改成 $2$ 也一样，最优解不会选它，因为删加插恰好是 $2$。这和 $m+n-2\cdot\mathrm{LCS}$ 等价：公共子序列不用动，其余全删再插。

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

**要输出操作序列呢？**
填表时不用另开选择数组，从 $(m,n)$ 回溯就行。两端相等算匹配，走对角；否则看当前值来自对角 $+1$（替换）、上方 $+1$（删 `word1`）还是左方 $+1$（插 `word2`），平手任选。操作逆序收集，最后反转。

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

**一维滚动数组会覆盖对角状态吗？**
会，关键在更新顺序。`dp[j]` 写之前是上一行的值（删除），`dp[j-1]` 已经是本行的值（插入），对角必须是覆盖前的旧 `dp[j]`，所以先用 `prev` 暂存再写。字符相同时直接抄 `prev`，不用再取一遍 `min`。

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

---
id: lc-97-interleaving-string
section: dp-2d
order: 5
level: A
title: LC 97 · 交错字符串
quick: >-
  先检查三串长度。$dp[i][j]$ 表示 `s1` 的前 $i$ 个字符和 `s2` 的前 $j$ 个字符能否交错成 `s3` 的前 $i+j$
  个字符，看 `s3` 当前末字符能否由 $s1[i-1]$ 或 $s2[j-1]$ 提供，从对应的前一个状态转移。表可以压成一维，时间 $O(mn)$。
tags:
  - DP
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 97. 交错字符串
    url: 'https://leetcode.cn/problems/interleaving-string/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定字符串 `s1`、`s2`、`s3`，判断能否把 s1 与 s2 中的全部字符交错合并，恰好组成 s3。合并过程中必须保持 s1 内部字符的相对顺序，也必须保持 s2 内部的相对顺序，但每次可以从任意一方取后续字符；不能漏掉、重复使用或额外添加字符。

### 输入与输出

实现 `isInterleave(s1, s2, s3) -> bool`。能够组成时返回 True，否则返回 False。各字符串可以为空；s3 的总长度必须与另外两串的长度之和一致，才有可能成功。

### 约束

- `0 <= len(s1), len(s2) <= 100`。
- `0 <= len(s3) <= 200`。
- 字符串只包含小写英文字母。

### 示例

```text
输入：s1 = "aabcc", s2 = "dbbca", s3 = "aadbbcbcac"
输出：true
```

[LeetCode 原题](https://leetcode.com/problems/interleaving-string/description/)

## 解题思路与参考答案

## 题意

判断 `s3` 是否由 `s1`、`s2` 交错组成：两串各自的相对顺序保持不变，只是合并时指针交替前进。

## 思路

我会用二维 DP，状态是两个串各用了多长的前缀。双指针贪心在两串都能接当前字符时可能选错分叉，要用 DP 或记忆化把分叉都记下来。

先判长度，`len(s1)+len(s2) != len(s3)` 直接返回否。$dp[i][j]$ 为真，当且仅当用两串的前缀能拼出 `s3` 的前 $i+j$ 个字符。转移有两条：`dp[i-1][j] and s1[i-1]==s3[i+j-1]`，或者 `dp[i][j-1] and s2[j-1]==s3[i+j-1]`。$dp[0][0]=\mathrm{true}$，第一行、第一列只沿一条串走。

拿 `s1="aabcc"`、`s2="dbbca"`、`s3="aadbbcbcac"` 来说，`s3` 开头的 `aa` 只能从 `s1` 拿，$dp[2][0]$ 为真；接下来的 `d` 只有 `s2` 能给，走到 $dp[2][1]$。这样一格格推到 $dp[5][5]$，结果为真。表可以压成一维，参考代码就是一维版。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert isInterleave("aabcc", "dbbca", "aadbbcbcac") is True
assert isInterleave("aabcc", "dbbca", "aadbbbaccc") is False
assert isInterleave("", "", "") is True
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(mn)$，一维额外空间 $O(n)$。

## Edge Cases

两串都空时 `s3` 也必须为空，`dp[0]=True`。长度和不相等说明字符数对不上，直接否。其中一串为空时，另一串必须和 `s3` 完全相等，第一行或第一列按单串匹配滚动。

## 追问

**贪心为什么错？**
当前字符两串都能接时，先吃 `s1` 可能把后面要用的字符用掉。反例是 `s1=aabc`、`s2=abad`、`s3=aabadabc`。如果能匹配就优先用 `s1`，前三个 `aab` 全从 `s1` 拿走，往后走到 `d` 时谁都接不上；正确做法是从第二个 `a` 起改走 `s2`。分叉要记下来，所以用记忆化搜索或 DP，双指针贪心不行。

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

**要输出一种交错方案呢？**
用二维布尔表，从 $(m,n)$ 回溯：如果 `dp[i-1][j]` 为真且 `s1[i-1]` 对得上 `s3` 的当前位，这个字符就来自 `s1`，否则来自 `s2`。逆序收集再反转。没有方案时 `dp[m][n]` 为假。

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

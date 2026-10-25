---
id: lc-1143-longest-common-subsequence
section: dp-multi
order: 2
level: S
title: LC 1143 · 最长公共子序列
quick: "用二维 DP，$dp[i][j]$ 是 `text1` 前 $i$ 个与 `text2` 前 $j$ 个的 LCS 长度。末字符相等取 $dp[i-1][j-1]+1$，否则取 $\\max(dp[i-1][j],\\,dp[i][j-1])$。时间 $O(mn)$，额外空间可压到 $O(\\min(m,n))$。"
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

## 题目描述

给定字符串 `text1` 与 `text2`，求它们最长公共子序列的长度。子序列是从原字符串删除任意一些字符后得到的序列，可以不删除，但保留字符的先后顺序不能改变；它不要求在原字符串中连续。公共子序列必须同时能从两个字符串中得到。

### 输入与输出

实现 `longestCommonSubsequence(text1, text2) -> int`，返回最大长度，不必返回具体字符序列。没有共同字符时返回0；这里要求的是子序列，不是连续子串。

### 约束

- `1 <= len(text1), len(text2) <= 1000`。
- 两个字符串都只包含小写英文字母。

### 示例

```text
输入：text1 = "abcde", text2 = "ace"
输出：3
```

[LeetCode 原题](https://leetcode.com/problems/longest-common-subsequence/description/)

## 解题思路与参考答案

## 题意

两个字符串 `text1`、`text2`，求最长公共子序列的长度；没有公共子序列返回 $0$。子序列是删掉若干字符（可以不删）、剩余字符保持原相对顺序得到的串，不要求连续。长度都在 $[1, 1000]$，只含小写字母。

## 思路

这是两个前缀对齐的二维 DP，每格只看两个前缀的末字符。$dp[i][j]$ 表示 `text1[:i]` 和 `text2[:j]` 的 LCS 长度，$dp[0][\cdot]=dp[\cdot][0]=0$。

末字符相等时，这对字符一定能放进某个最长公共子序列的末尾，$dp[i][j]=dp[i-1][j-1]+1$。不等时，至少有一个末字符用不上，要么丢掉 `text1` 的，要么丢掉 `text2` 的，$dp[i][j]=\max(dp[i-1][j],\ dp[i][j-1])$。

拿 `"abcde"` 和 `"ace"` 看：`a` 对上 `a`，`c` 对上 `c`，`e` 对上 `e`，每次相等都从左上角加一，中间的 `b`、`d` 对不上就从上或左继承，最后得 $3$。

相等时不用再和 $\max$ 比一次，因为 $dp[i-1][j]$ 和 $dp[i][j-1]$ 都不会超过 $dp[i-1][j-1]+1$。暴力枚举一边的所有子序列是 $O(2^m)$。空间上每行只依赖上一行和本行左边，滚动数组时要单独存左上角的旧值。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert longestCommonSubsequence("abcde", "ace") == 3
assert longestCommonSubsequence("abc", "abc") == 3
assert longestCommonSubsequence("abc", "def") == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(mn)$，额外空间 $O(mn)$；滚动一行后是 $O(\min(m,n))$。

## 边界

没有公共字符时，整张表都是 $0$。

两串相同时，每步都走对角，答案就是串长。

有重复字符，比如 `"aaa"` 和 `"aa"`，转移只看前缀，同一个字符不会被用两次，答案是 $2$。

## 追问

**只用一行空间怎么写？**
`dp[j]` 被覆盖前是上一行的值，`dp[j-1]` 已经是本行的。对角 $dp[i-1][j-1]$ 会被覆盖，所以每格先用 `prev` 暂存旧的 `dp[j]`，下一格拿来当左上角。

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

**要输出 LCS 本身呢？**
保留二维表，从 $(m,n)$ 往回走：末字符相等就收下这个字符并走对角；否则往值更大的那边走，上或者左。收到的字符是逆序的，最后反转一下。

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

**和编辑距离是什么关系？**
只允许插入和删除时，最少操作数是 $m+n-2\cdot\mathrm{LCS}$：公共子序列不动，其余字符删掉再插。允许替换就要用 `lc-72-edit-distance` 的三向转移。

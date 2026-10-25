---
id: lc-392-is-subsequence
section: two-pointers
order: 2
level: A
title: LC 392 · 判断子序列
quick: >-
  用双指针在 `t` 里按顺序匹配 `s` 的每个字符，每个字符都取最早出现的位置。`s` 的指针走完就是子序列。时间 $O(|t|)$，额外空间 $O(1)$。
tags:
  - String
  - Two Pointers
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 392. Is Subsequence
    url: https://leetcode.com/problems/is-subsequence/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题目描述

给定字符串 s 和 t，判断能否从 t 中删除零个或多个字符，在不改变剩余字符相对顺序的情况下恰好得到 s。如果可以，则 s 是 t 的子序列；所保留字符不要求连续。

### 接口与输出

实现 `isSubsequence(s: str, t: str) -> bool`。返回是否存在这样的保留方式，不要求返回所选下标。

### 合法输入与约束

`0 <= len(s) <= 100`，`0 <= len(t) <= 10000`，两者只含小写英文字母。空字符串是任意字符串的子序列，包括空字符串本身。

### 示例

```text
输入：s = "abc", t = "ahbgdc"
输出：true
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/is-subsequence/description/)。

## 解题思路与参考答案

## 题意

判断 `s` 是否为 `t` 的子序列：不改变相对顺序，从 `t` 里挑出若干字符恰好得到 `s`。$|s| \le 100$，$|t| \le 10^4$，只含小写字母。

## 思路

我会用双指针贪心，从左往右扫 `t`，每个 `s[i]` 都用 `t` 里最早出现的匹配。这样做是对的，因为越早匹配上，给后面的字符留的余地越多。

具体是 `i` 指向 `s` 下一个待匹配的字符，扫 `t` 时碰到相等就 `i` 加一，扫完后 `i == len(s)` 就成功。比如 `s="abc"`、`t="ahbgdc"`：`a` 匹配第 $0$ 位，跳过 `h`，`b` 匹配第 $2$ 位，跳过 `g`、`d`，`c` 匹配最后一位，`i` 走到 $3$，返回真。换成 `s="axc"`，`x` 在 `t` 里一直找不到，`i` 停在 $1$，返回假。`s` 是空串时恒为子序列。

## 参考代码

```python
def isSubsequence(s: str, t: str) -> bool:
    i = 0
    for ch in t:
        if i < len(s) and s[i] == ch:
            i += 1
    return i == len(s)


if __name__ == "__main__":
    assert isSubsequence("abc", "ahbgdc") is True
    assert isSubsequence("axc", "ahbgdc") is False
    assert isSubsequence("", "ahbgdc") is True
    assert isSubsequence("a", "") is False
    assert isSubsequence("aa", "a") is False
    assert isSubsequence("abc", "abc") is True
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert isSubsequence("abc", "ahbgdc") is True
assert isSubsequence("axc", "ahbgdc") is False
assert isSubsequence("", "ahbgdc") is True
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(|t|)$，额外空间 $O(1)$。`s` 的指针只前进、不回头。

## 边界

`s` 为空时返回真，空串是任何串的子序列。

`t` 为空而 `s` 非空时返回假。

`s` 里有重复字符时，比如 `"aa"`，`t` 里要有两个不同位置的 `a`，同一个位置不能用两次。

## 追问

**同一个 `t` 要对大量不同的 `s` 做判断呢？**
预处理 `t` 建一张跳转表，之后每次查询只要 $O(|s|)$。每次都跑双指针是 $O(|t|)$，询问一多就亏。`nxt[i][c]` 表示从下标 $i$ 起（含 $i$）字符 $c$ 下一次出现的位置，没有就记 $|t|$。从右往左填，先拷 `nxt[i+1]`，再把 `t[i]` 那一列改成 $i$。查询时指针从 $0$ 出发，对 `s` 的每个字符跳到 `nxt[pos][ch]`，跳到 $|t|$ 就失败，否则 `pos += 1`。预处理 $O(|t|\cdot\Sigma)$，单次查询 $O(|s|)$。这只适合字母表小的情况，$\Sigma$ 太大就改成每个字符一条下标列表，再二分。

```python
def preprocess(t):
    n = len(t)
    nxt = [[n] * 26 for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        nxt[i] = nxt[i + 1][:]
        nxt[i][ord(t[i]) - 97] = i
    return nxt

def isSubsequence(s, nxt, n):
    pos = 0
    for ch in s:
        pos = nxt[pos][ord(ch) - 97]
        if pos == n:
            return False
        pos += 1
    return True
```

**和最长公共子序列有什么关系？**
`s` 是 `t` 的子序列，当且仅当 $\mathrm{LCS}(s,t)=|s|$，但 DP 比双指针慢，判断题不要上 DP。子序列判断问的是 `s` 能否整段嵌进 `t`，LCS 两边都可以删字符，求最长的公共长度。$dp[i][j]$ 表示 `a` 前 $i$ 个和 `b` 前 $j$ 个字符的 LCS，相等时取 $dp[i-1][j-1]+1$，否则取 $\max(dp[i-1][j], dp[i][j-1])$。时间 $O(mn)$，空间可以滚动成 $O(\min(m,n))$。这题贪心用最早匹配，LCS 没有「最早一定最优」这种单指针结论。独立卡见 `lc-1143-longest-common-subsequence`。

```python
def longestCommonSubsequence(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]
```

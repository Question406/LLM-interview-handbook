---
id: lc-392-is-subsequence
section: two-pointers
order: 2
level: A
title: LC 392 · 判断子序列
quick: >-
  双指针扫 `s` 与 `t`：在 `t` 里按顺序匹配 `s` 的每个字符。`s` 指针走完即为子序列。时间
  $O(|t|)$，额外空间 $O(1)$。
tags:
  - Two Pointers
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 392. 判断子序列
    url: https://leetcode.cn/problems/is-subsequence/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

判断 `s` 是否为 `t` 的子序列：不改变相对顺序，从 `t` 里挑出若干字符恰好得到 `s`。

## 思路

`i` 指向 `s` 下一个待匹配字符，从左往右扫 `t`。碰上相等就 `i` 加一。扫完后 `i == len(s)` 即成功。`s` 空串恒为子序列。

贪心正确：每个 `s[i]` 用 `t` 里最早出现的匹配，给后面字符留更多余地。

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
    print("ok")
```

## 复杂度

时间 $O(|t|)$，额外空间 $O(1)$。`s` 只前进、不回头。

## 边界

- `s` 为空：空串是任何串的子序列，真。
- `t` 为空且 `s` 非空：假；`s` 与 `t` 相同则为真。

## 追问

- **大量不同的 `s` 对同一个 `t`？** 每次双指针是 $O(|t|)$，询问一多就亏。预处理 `t`：`nxt[i][c]` 表示从下标 $i$ 起（含 $i$）字符 $c$ 下一次出现的位置，没有则记 $|t|$。从右往左填，先拷 `nxt[i+1]`，再把 `t[i]` 的列改成 $i$。查询时指针从 $0$ 出发，对 `s` 的每个字符跳到 `nxt[pos][ch]`，跳到 $|t|$ 就失败，否则 `pos += 1`。预处理 $O(|t|\cdot\Sigma)$，单次查询 $O(|s|)$。只适用于字母表小；$\Sigma$ 太大改成「每个字符一条下标列表 + 二分」。

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

- **最长公共子序列（LC 1143）？** 子序列判断是「`s` 能否整段嵌进 `t`」；LCS 是两边都可删，求最长公共长度。$dp[i][j]$：`a` 前 $i$ 与 `b` 前 $j$ 的 LCS。相等则 $dp[i-1][j-1]+1$，否则取 $\max(dp[i-1][j], dp[i][j-1])$。时间 $O(mn)$，空间可滚成 $O(\min(m,n))$。`s` 是 `t` 的子序列当且仅当 $\mathrm{LCS}(s,t)=|s|$，但 DP 比双指针慢，判断题不要上 DP。这题贪心用最早匹配；LCS 没有「最早一定最优」的单指针结论。

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

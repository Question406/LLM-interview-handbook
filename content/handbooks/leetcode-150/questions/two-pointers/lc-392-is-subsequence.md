---
id: lc-392-is-subsequence
section: two-pointers
order: 2
level: A
title: LC 392 · 判断子序列
quick: "双指针贪心：从左往右扫 `t`，按顺序匹配 `s` 的每个字符，每个字符都用 `t` 里最早能匹配的位置。`s` 的指针走完就是子序列。时间 $O(|t|)$，额外空间 $O(1)$。"
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

## 题目描述

给定两个字符串 s 和 t，判断能否仅从 t 中删除零个或多个字符，在不改变其余字符相对顺序的情况下得到 s。删除后留下的字符不必在原串中连续。

### 输入与输出

实现 `isSubsequence(s, t) -> bool`。若 s 是 t 的子序列返回 True，否则返回 False；空字符串是任何字符串的子序列。

### 约束与约定

- `0 <= len(s) <= 100`。
- `0 <= len(t) <= 10000`。
- 所有字符均为小写英文字母。

### 示例

```text
输入：s = "abc", t = "ahbgdc"
输出：true
```

abc 在 ahbgdc 中依次出现，虽然不连续，仍然是它的子序列。

[官方原题与完整题面](https://leetcode.com/problems/is-subsequence/description/)。

## 解题思路与参考答案

## 题意

判断 `s` 是否为 `t` 的子序列：不改变相对顺序，从 `t` 里挑出若干字符恰好得到 `s`。

## 思路

我会用双指针贪心。`i` 指向 `s` 里下一个待匹配的字符，从左往右扫 `t`，碰到相等的就 `i` 加一，扫完后 `i == len(s)` 就是子序列。贪心之所以对，是因为每个 `s[i]` 都用 `t` 里最早出现的匹配，给后面的字符留了最多余地。

拿 `s="abc"`、`t="ahbgdc"` 看。`a` 匹配上 `t` 的第一个字符，跳过 `h`，`b` 匹配上，跳过 `g`、`d`，`c` 匹配上，`s` 走完，返回真。换成 `"axc"`，扫完整个 `t` 也找不到 `x`，返回假。

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

`s` 为空时，空串是任何串的子序列，返回真。

`t` 为空而 `s` 非空，返回假；`s` 和 `t` 相同则为真。

## 追问

**大量不同的 `s` 查同一个 `t` 呢？**
每次双指针都是 $O(|t|)$，询问一多就亏，可以先预处理 `t`。`nxt[i][c]` 表示从下标 $i$ 起（含 $i$）字符 $c$ 下一次出现的位置，没有就记 $|t|$。从右往左填：先拷贝 `nxt[i+1]`，再把 `t[i]` 那一列改成 $i$。查询时指针从 $0$ 出发，对 `s` 的每个字符跳到 `nxt[pos][ch]`，跳到 $|t|$ 就失败，否则 `pos += 1`。预处理 $O(|t|\cdot\Sigma)$，单次查询 $O(|s|)$。这只适合字母表小的情况；$\Sigma$ 太大就改成「每个字符一条下标列表，查询时二分」。

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

**最长公共子序列（LC 1143）和这题什么关系？**
判断子序列问的是 `s` 能不能整段嵌进 `t`；LCS 两边都可以删，求最长的公共长度。$dp[i][j]$ 表示 `a` 的前 $i$ 个字符和 `b` 的前 $j$ 个字符的 LCS。字符相等取 $dp[i-1][j-1]+1$，否则取 $\max(dp[i-1][j], dp[i][j-1])$。时间 $O(mn)$，空间可以滚动成 $O(\min(m,n))$。`s` 是 `t` 的子序列当且仅当 $\mathrm{LCS}(s,t)=|s|$，但 DP 比双指针慢，判断题别上 DP。另外这题的贪心用最早匹配；LCS 没有「最早一定最优」这种单指针结论。

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

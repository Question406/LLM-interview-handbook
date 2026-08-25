---
id: ali-algo-interval-lcs
section: alibaba-oa
order: 37
level: A
title: 阿里手撕：合并区间和最长公共子序列差在哪？
quick: >-
  56 我会先按左端排序，能并就扩右端。1143 是二维 DP：字符相等走对角，否则取左或上。一个扫区间，一个对齐字符串。
tags:
  - Alibaba
  - 区间
  - LCS
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 合并区间
    url: https://leetcode.cn/problems/merge-intervals/
    type: primary
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
---

## 真题 / 考点说明

- 对应：LeetCode 56 / 1143

56 是一维扫描贪心：排序后维护当前右端。1143 是二维对齐 DP。一个处理区间覆盖，一个处理字符对齐。这块容易和最长公共**子串**搞混，子串必须连续，断了就归零。笔试「两排列字典序最大公共子序列」是贪心特化，见 `ali-oa-max-common-subseq`，不是这道 $O(n^2)$。

## 思路

合并：按左端排序。维护当前区间 `[l,r]`，下一个 `[L,R]` 若 $L\le r$ 则 `r=\max(r,R)`，否则把当前结算并开启新段。相接（$L=r$）通常也合并。日程冲突、会议室，都是这个扫描。

LCS：`dp[i][j]` 为 $a[:i]$ 与 $b[:j]$ 的 LCS 长度。`a[i-1]==b[j-1]` 时对角加一，否则取左或上的最大。空串边界为 $0$。只要长度可滚一维；要还原序列，从右下沿相等格子回溯。

## 参考代码

```python
from typing import List


def merge(intervals: List[List[int]]) -> List[List[int]]:
    intervals.sort(key=lambda x: x[0])
    ans = [intervals[0][:]]
    for left, right in intervals[1:]:
        if left <= ans[-1][1]:
            ans[-1][1] = max(ans[-1][1], right)
        else:
            ans.append([left, right])
    return ans


def longest_common_subsequence(text1: str, text2: str) -> int:
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
    assert merge([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]
    assert merge([[1, 4], [4, 5]]) == [[1, 5]]
    assert longest_common_subsequence("abcde", "ace") == 3
    assert longest_common_subsequence("abc", "abc") == 3
    assert longest_common_subsequence("abc", "def") == 0
    print("ok")
```

## 复杂度

- 56：排序 $O(n\log n)$，随后线性扫描；空间 $O(n)$ 存答案。
- 1143：时间 $O(mn)$，空间 $O(mn)$；滚动一行 $O(\min(m,n))$。

## 边界与追问

1. 56：单区间、完全包含、只在端点相接。开口问清闭区间相接点要不要并。
2. 1143：空串、无公共字符、整串相等。追问子串：相等连续加一，不等归零，再扫全局 max。
3. 追问会议室 / 字典序最大公共子序列：前者是扫描线或堆；后者对排列走贪心，不要上 $O(n^2)$ DP。

---
id: ali-algo-interval-lcs
section: alibaba-oa
order: 37
level: A
title: 阿里手撕：合并区间和最长公共子序列差在哪？
quick: "合并区间（56）先按左端点排序，遇到重叠就把当前区间的右端点往外扩；最长公共子序列（1143）用二维 DP，字符相同取对角加一，不同取左边和上边的较大值。前者扫描区间，后者比较两个字符串的前缀。"
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

## 题目描述

本卡包含两个独立的算法练习，接口按手册统一为 Python 函数，不要求把它们合并成一个程序。

### 输入与输出

- `merge(intervals)`：输入非空闭区间列表，每项为 `[start, end]`，保证 `start <= end`。返回覆盖范围相同、互不重叠的合并区间列表，按左端点递增排列。只在端点相接也算重叠，例如 `[1,4]` 与 `[4,5]` 要合并；允许修改输入列表的顺序。
- `longest_common_subsequence(text1, text2)`：输入两个字符串，返回最长公共子序列的长度。子序列可以删除任意字符，但剩余字符的相对顺序不能改变；不要求连续。任一输入为空时返回 0。

### 示例

```text
merge([[1,3],[2,6],[8,10]]) -> [[1,6],[8,10]]
merge([[1,4],[4,5]])       -> [[1,5]]
longest_common_subsequence("abcde", "ace") -> 3
longest_common_subsequence("abc", "def")   -> 0
```

公开面经未给出统一的数据上界；本卡以这两个接口的合法输入和上述语义作为练习约定。

## 解题思路与参考答案

## 真题 / 考点说明

- 对应：LeetCode 56 / 1143

两道题一个是一维扫描贪心，一个是二维对齐 DP。56 排序后维护当前右端点，处理的是区间覆盖；1143 比较两个字符串的前缀，处理的是字符对齐。最常见的混淆是把 LCS 和最长公共子串搞混，子串必须连续，断了就归零。笔试里「两排列字典序最大公共子序列」是贪心特化，见 `ali-oa-max-common-subseq`，用不上这道的 $O(n^2)$。

## 思路

合并区间先按左端点排序，维护当前区间 `[l,r]`。下一个 `[L,R]` 如果 $L\le r$，就 `r=\max(r,R)`；否则把当前区间结算，开一段新的。只在端点相接（$L=r$）通常也合并。日程冲突、会议室，都是这种扫描。

LCS 的状态 `dp[i][j]` 是 $a[:i]$ 与 $b[:j]$ 的 LCS 长度。`a[i-1]==b[j-1]` 时对角加一，否则取左边或上边的较大值，空串边界为 $0$。只求长度时可以用一维滚动数组；要还原序列，就从右下角沿着相等的格子回溯。

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

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert merge([[1, 3], [2, 6], [8, 10], [15, 18]]) == [[1, 6], [8, 10], [15, 18]]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 复杂度

56 排序 $O(n\log n)$，之后线性扫描，空间 $O(n)$ 存答案。1143 时间 $O(mn)$、空间 $O(mn)$，滚动一行可以降到 $O(\min(m,n))$。

## 追问

**合并区间要测哪些边界？**
单区间、完全包含、只在端点相接。闭区间端点相接要不要并，开口先问清楚。

**LCS 要测哪些边界？换成最长公共子串呢？**
空串、无公共字符、整串相等。子串的话，相等就在对角上连续加一，不等归零，再扫一遍全局 max。

**会议室、字典序最大公共子序列怎么做？**
会议室用扫描线或堆；字典序最大公共子序列对排列走贪心，不要上 $O(n^2)$ DP。

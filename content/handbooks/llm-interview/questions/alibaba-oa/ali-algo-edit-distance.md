---
id: ali-algo-edit-distance
section: alibaba-oa
order: 32
level: A
title: 阿里手撕：编辑距离的状态和边界怎么写？
quick: >-
  `dp[i][j]` 是 $a[:i]$ 变 $b[:j]$ 的最少操作。删/插/改取 min，加一。空串边界是 $i$ 或 $j$。
tags:
  - Alibaba
  - DP
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-18
sources:
  - title: 编辑距离
    url: https://leetcode.cn/problems/edit-distance/
    type: primary
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
---

## 真题 / 考点说明

- 对应：LeetCode 72，阿里校招 DP 深挖题

状态：`dp[i][j]` 表示把 $a$ 的前 $i$ 个字符变成 $b$ 的前 $j$ 个字符的最少操作数。边界：空串对长度为 $i$ 的串要 $i$ 次删除（或插入）。

更干净的转移：删 = `dp[i-1][j]+1`，插 = `dp[i][j-1]+1`，改 = `dp[i-1][j-1]+[a[i-1]\neq b[j-1]]`。相等时改的代价为 $0$，不要再加一。

追问搜索纠错：编辑距离是召回候选的代价，线上还要加词典先验和性能截断。

## 思路

先填第 $0$ 行和第 $0$ 列。然后对每个 `(i,j)`：

- 若 `a[i-1]==b[j-1]`，直接继承对角 `dp[i-1][j-1]`。
- 否则在「删 $a$ 一个 / 插 $b$ 一个 / 改当前」里取最小再加一。

滚动一维时必须从右往左，或保留上一行，避免覆盖还要用的对角值。

$$
dp[i][j]=\min\bigl(dp[i-1][j]+1,\; dp[i][j-1]+1,\; dp[i-1][j-1]+[a_{i-1}\neq b_{j-1}]\bigr)
$$

## 参考代码

```python
def min_distance(word1: str, word2: str) -> int:
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
                    dp[i - 1][j],
                    dp[i][j - 1],
                    dp[i - 1][j - 1],
                )
    return dp[m][n]


def min_distance_1d(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        cur = [i] + [0] * n
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                cur[j] = prev[j - 1]
            else:
                cur[j] = 1 + min(prev[j], cur[j - 1], prev[j - 1])
        prev = cur
    return prev[n]


if __name__ == "__main__":
    assert min_distance("horse", "ros") == 3
    assert min_distance("intention", "execution") == 5
    assert min_distance("", "abc") == 3
    assert min_distance("abc", "") == 3
    assert min_distance("", "") == 0
    assert min_distance_1d("horse", "ros") == 3
    print("ok")
```

## 复杂度

二维：$O(mn)$ 时间、$O(mn)$ 空间。滚动两行或一行：$O(mn)$ 时间、$O(\min(m,n))$ 空间。只求距离不必还原路径。

## 边界与追问

1. 空串对空串是 $0$；一侧为空则答案等于另一侧长度。
2. 追问只允许插入/删除（LCS 对偶）：最少操作 $= m+n-2\cdot\mathrm{LCS}$。
3. 追问搜索纠错：先倒排/ngram 召回再算编辑距离，加词典先验，P99 超时截断；不要对全词典两两 DP。

---
id: lc-120-triangle
section: dp-2d
order: 1
level: A
title: LC 120 · 三角形最小路径和
quick: >-
  自底向上：$dp[j]=\textit{row}[j]+\min(dp[j],dp[j+1])$，从倒数第二层滚到顶。避免自顶向下的边界分叉。时间
  $O(n^2)$。
tags:
  - DP
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 120. 三角形最小路径和
    url: https://leetcode.cn/problems/triangle/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

三角形数组，每步只能走到下一层相邻下标。求从顶到底的最小路径和。

## 思路

自底向上更干净：底层就是初值。上一层位置 $j$ 只能接 $j$ 或 $j+1$，所以 `dp[j] = triangle[i][j] + min(dp[j], dp[j+1])`。一层一层滚到顶，`dp[0]` 即答案。

自顶向下要处理左右边界，还得在最后一层再扫一遍最小值。可以原地改三角形，或单独开一维 $O(n)$。白板我主答自底向上。

## 参考代码

```python
from typing import List


def minimumTotal(triangle: List[List[int]]) -> int:
    dp = triangle[-1][:]
    for i in range(len(triangle) - 2, -1, -1):
        for j in range(i + 1):
            dp[j] = triangle[i][j] + min(dp[j], dp[j + 1])
    return dp[0]


if __name__ == "__main__":
    assert minimumTotal([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]) == 11
    assert minimumTotal([[-10]]) == -10
    print("ok")
```

## 复杂度

时间 $O(n^2)$（$n$ 为层数），额外空间 $O(n)$。原地修改可达 $O(1)$ 额外空间。

## 边界

- 只有一层：循环不进，`dp` 就是底层拷贝，返回 `dp[0]`。
- 含负数：不能每层贪心选最小，局部最小可能接上更大的后续。
- 自底向上时 $j$ 与 $j+1$ 总在下一层范围内，左右边界不用特判。

## 追问

- **自顶向下怎么写？** 第一层只有一个入口。第 $i$ 层下标 $0$ 只能来自正上，下标 $i$ 只能来自左上，中间格取 $\min(\textit{左上},\textit{正上})$ 再加当前值。最后在底层扫一遍最小值。比自底向上多边界分叉，也要多开一层或原地改。时间仍 $O(n^2)$。

```python
def minimumTotal_topdown(triangle):
    n = len(triangle)
    dp = [triangle[0][0]]
    for i in range(1, n):
        row = [0] * (i + 1)
        row[0] = dp[0] + triangle[i][0]
        row[i] = dp[-1] + triangle[i][i]
        for j in range(1, i):
            row[j] = triangle[i][j] + min(dp[j - 1], dp[j])
        dp = row
    return min(dp)
```

- **输出一条最小路径？** 自底向上时额外记 `choice[i][j]`：该格选了下一层的 $j$ 还是 $j+1$。从顶沿选择走到低，顺带取出原值。只留一维 `dp` 会丢历史，要路径就必须留选择或整张表。时间仍 $O(n^2)$，额外 $O(n^2)$。

```python
def minimumTotal_path(triangle):
    n = len(triangle)
    dp = triangle[-1][:]
    choice = [[0] * (i + 1) for i in range(n)]
    for i in range(n - 2, -1, -1):
        for j in range(i + 1):
            choice[i][j] = 0 if dp[j] <= dp[j + 1] else 1
            dp[j] = triangle[i][j] + min(dp[j], dp[j + 1])
    path, j = [triangle[0][0]], 0
    for i in range(n - 1):
        j += choice[i][j]
        path.append(triangle[i + 1][j])
    return dp[0], path
```

---
id: lc-120-triangle
section: dp-2d
order: 1
level: A
title: LC 120 · 三角形最小路径和
quick: >-
  自底向上 DP：底层作初值，$dp[j]=\textit{row}[j]+\min(dp[j],dp[j+1])$ 一层层滚到顶，`dp[0]`
  就是答案。这样不用处理自顶向下的 left / right bounds，时间 $O(n^2)$，额外空间 $O(n)$。
tags:
  - DP
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 120. 三角形最小路径和
    url: 'https://leetcode.cn/problems/triangle/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定由若干行整数构成的三角形 `triangle`，从最顶端的唯一元素出发，每一行选择一个元素，直到最底行。若当前位于第 i 行下标 j，下一步只能到第 i+1 行的下标 j 或 j+1。求所选元素总和的最小值。

### 输入与输出

实现 `minimumTotal(triangle) -> int`，返回最小路径和。路径必须包含顶点和最后一行的一个元素，不能提前停止；元素可为负数。

### 约束

- 三角形有 1 到 200 行。
- 第一行恰有一个元素，每下一行比上一行多一个元素。
- `-10^4 <= triangle[i][j] <= 10^4`。

### 示例

```text
输入：triangle = [[2],[3,4],[6,5,7],[4,1,8,3]]
输出：11
```

[LeetCode 原题](https://leetcode.com/problems/triangle/description/)

## 解题思路与参考答案

## 题意

给一个三角形数组，每一步只能走到下一层相邻的下标，求从顶到底的最小路径和。

## 思路

我会自底向上做 DP。从下往上看，每个位置恰好有 $j$ 和 $j+1$ 两个下家，没有 edge-case branches，最后也不用在底层再扫一遍最小值。

底层就是初值。上一层的位置 $j$ 只能接 $j$ 或 $j+1$，所以 `dp[j] = triangle[i][j] + min(dp[j], dp[j+1])`，逐层更新到顶部，`dp[0]` 就是答案。拿 `[[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]` 来说，底层是 `[4, 1, 8, 3]`；第三层变成 `[6+1, 5+1, 7+3] = [7, 6, 10]`；第二层是 `[3+6, 4+6] = [9, 10]`；顶上是 `2+9 = 11`。

自顶向下也能做，但要处理 left / right bounds，最后还得在底层扫最小值，放在追问里。可以原地改三角形，也可以单独开一维 $O(n)$ 的数组。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert minimumTotal([[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]) == 11
assert minimumTotal([[-10]]) == -10
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n^2)$，$n$ 为层数；额外空间 $O(n)$，原地修改可以做到 $O(1)$。

## Edge Cases

只有一层时循环不进，`dp` 就是底层的拷贝，返回 `dp[0]`。有负数时不能每层贪心选最小，局部最小可能接上更大的后续。自底向上时 $j$ 和 $j+1$ 总在下一层范围内，left / right bounds 不用特判。

## 追问

**自顶向下怎么写？**
第一层只有一个入口。第 $i$ 层下标 $0$ 只能来自正上，下标 $i$ 只能来自左上，中间的格子取 $\min(\textit{左上},\textit{正上})$ 再加当前值，最后在底层扫一遍最小值。比自底向上多了 edge-case branches，也要多开一层或原地改，时间仍是 $O(n^2)$。

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

**要输出一条最小路径呢？**
自底向上时额外记 `choice[i][j]`，即这一格选了下一层的 $j$ 还是 $j+1$，再从顶部沿着记录走到底部，顺带取出原值。只留一维 `dp` 会丢掉历史，要路径就得留下选择或整张表。时间仍是 $O(n^2)$，额外空间 $O(n^2)$。

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

---
id: lc-221-maximal-square
section: dp-2d
order: 9
level: A
title: LC 221 · 最大正方形
quick: >-
  $dp[i][j]$ 记以 $(i,j)$ 为右下角的最大正方形边长：格子为 $1$ 时
  $dp[i][j]=\min(\text{上},\text{左},\text{左上})+1$，否则为
  $0$。边长受三个方向里最短的那个限制，最后返回最大边长的平方，时间 $O(mn)$。
tags:
  - DP
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 221. 最大正方形
    url: 'https://leetcode.cn/problems/maximal-square/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定只含字符 0 和 1 的矩形矩阵，寻找其中完全由 1 构成、边与 matrix boundaries 平行的最大正方形。正方形必须由连续的行和连续的列组成。

### 输入与输出

实现 `maximalSquare(matrix) -> int`，返回最大正方形的面积，而不是边长。若不存在任何 1，返回 0。输入元素是字符串 "0" 或 "1"，不是布尔值。

### 约束与约定

- 矩阵有 `1 <= m,n <= 300` 行列。
- 每一行长度相同，元素仅为字符 "0"、"1"。

### 示例

```text
输入：matrix = [["1","0","1","0","0"],["1","0","1","1","1"],["1","1","1","1","1"],["1","0","0","1","0"]]
输出：4
```

示例里最大的全 1 正方形边长为 2，面积为 4。

[官方原题与完整题面](https://leetcode.com/problems/maximal-square/description/)。

## 解题思路与参考答案

## 题意

给一个 `0`/`1` 矩阵，找只含 `1` 的最大正方形，返回它的面积。

## 思路

我会用二维 DP，把 $dp[i][j]$ 定义为以这一格为右下角能形成的最大边长。当前是 `0` 就是 $0$；当前是 `1` 时，边长受上、左、左上三个方向的短板限制，三者取 $\min$ 再加一。道理是三个方向都至少有边长 $k-1$ 的正方形，才能在这里收成边长 $k$。

举个小例子，`[["1","1"],["1","1"]]` 右下角那一格的上、左、左上都是 $1$，所以它是 $\min(1,1,1)+1=2$，面积 $4$。如果左上角换成 `0`，右下角的左上邻居就是 $0$，边长只能是 $1$。

下标可以整体加一圈空边，省掉第一行、第一列的特判。最后返回 $\textit{side}^2$，题目要的是面积。

## 参考代码

```python
from typing import List


def maximalSquare(matrix: List[List[str]]) -> int:
    m, n = len(matrix), len(matrix[0])
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    side = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if matrix[i - 1][j - 1] == "1":
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1
                side = max(side, dp[i][j])
    return side * side


if __name__ == "__main__":
    assert (
        maximalSquare(
            [
                ["1", "0", "1", "0", "0"],
                ["1", "0", "1", "1", "1"],
                ["1", "1", "1", "1", "1"],
                ["1", "0", "0", "1", "0"],
            ]
        )
        == 4
    )
    assert maximalSquare([["0", "1"], ["1", "0"]]) == 1
    assert maximalSquare([["0"]]) == 0
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert (
    maximalSquare(
        [
            ["1", "0", "1", "0", "0"],
            ["1", "0", "1", "1", "1"],
            ["1", "1", "1", "1", "1"],
            ["1", "0", "0", "1", "0"],
        ]
    )
    == 4
)
assert maximalSquare([["0", "1"], ["1", "0"]]) == 1
assert maximalSquare([["0"]]) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(mn)$，额外空间 $O(mn)$，可以滚成一维 $O(n)$。

## Edge Cases

全 $0$ 时 `side` 保持 $0$，面积 $0$。单格 `"1"` 的三个邻居都是哨兵 $0$，$\min+1=1$，面积 $1$。最大正方形贴着边时，多开一圈空边后第一行、第一列按普通格子转移，不用特判。

## 追问

**要找最大矩形（LC 85）怎么办？**
这个 $\min$ 就用不上了。正方形靠上、左、左上三条边长的短板，矩形的宽和高是解耦的。做法是逐行把当前格上方连续 `1` 的个数收成直方图高度，再对每一层直方图用单调栈求最大矩形，时间 $O(mn)$。

```python
def maximalRectangle(matrix):
    if not matrix:
        return 0
    n, heights, ans = len(matrix[0]), [0] * len(matrix[0]), 0
    for row in matrix:
        for j, x in enumerate(row):
            heights[j] = heights[j] + 1 if x == "1" else 0
        st, h = [-1], heights + [0]
        for i, x in enumerate(h):
            while st[-1] != -1 and h[st[-1]] > x:
                height = h[st.pop()]
                ans = max(ans, height * (i - st[-1] - 1))
            st.append(i)
    return ans
```

**压成一维时，对角为什么会脏？**
因为左上的旧值会被本行覆盖。转移要用上、左、左上：滚动后 `dp[j]` 写之前是上一行的「上」，`dp[j-1]` 已经是本行的「左」，左上本应是上一行的 `dp[j-1]`，它刚被本行覆盖了。所以写 `dp[j]` 前先把旧值存进 `prev`，下一列的对角就用这个旧值。漏存的话会把本行左边当成左上，边长虚高。

```python
def maximalSquare_1d(matrix):
    n, side = len(matrix[0]), 0
    dp = [0] * (n + 1)
    for i in range(1, len(matrix) + 1):
        prev = 0
        for j in range(1, n + 1):
            tmp = dp[j]
            if matrix[i - 1][j - 1] == "1":
                dp[j] = min(dp[j], dp[j - 1], prev) + 1
                side = max(side, dp[j])
            else:
                dp[j] = 0
            prev = tmp
    return side * side
```

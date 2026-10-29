---
id: openai-largest-subgrid-histogram-extension
section: openai
order: 932
level: A
title: "OpenAI 题型扩展：最大 all-ones sub-rectangle 与 histogram stack"
quick: "我会先把二维问题固定到某一行：如果 rectangle 的底在这里，每列最多能往上延伸多少格？这就是连续 1 的 heights。"
companies:
  - openai
tags:
  - "Frontier Coding 扩展 2026-10-28"
  - 完整编程练习
  - "公开题型扩展"
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "公开来源：OpenAI 题型扩展：最大 all-ones sub-rectangle 与 histogram stack"
    url: "https://aceoffer.app/interviews/oai_largest_sub_grid_in_2d_array"
    type: secondary
---

## 题目描述

来源：AceOffer 公开页面提供 Largest Sub-Grid in 2D Array 的题名与能力标签。这里采用手册自定的 all-ones rectangle 条件，练习 matrix-to-histogram 转换。

### 输入、接口与规则

实现 `max_ones_rectangle(matrix) -> int`。输入为等宽的二维 list，每个元素严格为 0 或 1；matrix 可为空，或包含空 rows。返回只含 1、连续 rows 与连续 columns 构成的 axis-aligned rectangle 的最大 area。没有 1 则返回 0；不要求返回 coordinates，不修改输入。

Rows 与 columns 最多各 1000；希望时间 `O(H*W)`，额外空间 `O(W)`。每处理一行，把该行当作 rectangle 的底部，用每列连续 1 的 height 构造 histogram。需要处理相同 heights，以及某个 column 为 0 后高度重置的情况；rectangle 不要求是 square。

### 输入输出示例

```text
matrix=[[1,0,1,0,0],[1,0,1,1,1],[1,1,1,1,1],[1,0,0,1,0]] -> 6。
matrix=[[1,1,1]] -> 3；matrix=[] -> 0。
```

## 回答思路

> **Situation / Task：** 求最大 rectangle area，不限制长宽相等。  
> **Approach / Why：** 逐行累计 heights，再用 monotonic stack 解决每行 histogram。  
> **Result / Check：** 与小 matrix 的全部 rectangles 穷举比较，检查 equal heights 与零值。

## 解题思路与参考答案

我会先把二维问题固定到某一行：如果 rectangle 的底在这里，每列最多能往上延伸多少格？这就是连续 1 的 heights。

对 histogram 使用 increasing stack。遇到较矮的柱子，就能确定更高柱子能延伸到的最右位置，弹出时计算 area。行尾补一个虚拟高度零，把剩余候选一次算完。

### 完整参考实现

```python
def max_ones_rectangle(matrix):
    if not matrix:
        return 0
    heights = [0] * len(matrix[0])
    best = 0
    for row in matrix:
        heights = [h + 1 if bit else 0 for h, bit in zip(heights, row)]
        stack = []
        for i in range(len(heights) + 1):
            current = heights[i] if i < len(heights) else 0
            while stack and heights[stack[-1]] > current:
                height = heights[stack.pop()]
                left = stack[-1] + 1 if stack else 0
                best = max(best, height * (i - left))
            stack.append(i)
    return best
```

## 简单测试怎么写

将实现和测试按顺序放入同一个 Python 文件，运行 `python solution.py`。这些测试仅使用 Python standard library；先核对题面的具体输出，再检查容易出错的情况。

```python
assert (
    max_ones_rectangle(
        [[1, 0, 1, 0, 0], [1, 0, 1, 1, 1], [1, 1, 1, 1, 1], [1, 0, 0, 1, 0]]
    )
    == 6
)
assert max_ones_rectangle([]) == 0
assert max_ones_rectangle([[]]) == 0
from itertools import product

for bits in product([0, 1], repeat=9):
    matrix = [list(bits[i : i + 3]) for i in range(0, 9, 3)]
    expected = 0
    for top in range(3):
        for bottom in range(top + 1, 4):
            for left in range(3):
                for right in range(left + 1, 4):
                    if all(
                        matrix[r][c]
                        for r in range(top, bottom)
                        for c in range(left, right)
                    ):
                        expected = max(expected, (bottom - top) * (right - left))
    assert max_ones_rectangle(matrix) == expected
print('matrix rectangle tests passed')
```

## 复杂度与追问

每行每个 column 最多入栈、出栈一次，时间 `O(H*W)`；heights 与 stack 空间 `O(W)`。追问返回 coordinates 时，在计算 area 的位置同时记录 bottom、height、left 与 right。

---
id: lc-2352-equal-row-and-column-pairs
section: hashmap
order: 4
level: A
title: LC 2352 · 相等行列对
quick: "把每一行转成 tuple 放进 `Counter` 计数，再把每一列拼成 tuple 去表里查，次数累加就是答案。时间 $O(n^2)$，额外空间 $O(n^2)$。"
tags:
  - Array
  - Hash
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 2352. Equal Row and Column Pairs
    url: https://leetcode.com/problems/equal-row-and-column-pairs/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题目描述

给定一个 n×n 的整数矩阵，统计有多少个行下标 r 与列下标 c 组成的有序对，使第 r 行从左到右的元素序列，与第 c 列从上到下的元素序列逐项相同。相同数值的不同下标对需要分别计数。

### 输入与输出

实现 `equalPairs(grid: List[List[int]]) -> int`。比较的是整个行列序列，不能先排序；r 与 c 可以相等。返回下标对数量，而不是去重后的序列数量。

### 约束

- 输入是正方形矩阵，`1 <= n <= 200`。
- `1 <= grid[i][j] <= 10^5`。

### 示例

```text
输入：grid = [[3,2,1],[1,7,6],[2,7,7]]
输出：1
```

示例的第 2 行 `[2,7,7]` 与第 1 列 `[2,7,7]` 相同；下标从 0 开始，这一对是唯一匹配。

## 解题思路与参考答案

## 题意

给 $n \times n$ 整数矩阵 `grid`，统计满足「第 $r$ 行与第 $c$ 列按顺序逐个元素相等」的 $(r, c)$ 对数。$1 \le n \le 200$。

## 思路

我把一整行当成一个哈希键，这样每列只要查一次表，避开 $O(n^3)$ 的逐对比较。行转成 `tuple`（列表不可哈希）后计数，相同的行会累积次数；然后每一列也转成 `tuple` 去查，查到几次就贡献几对。Python 里 `zip(*grid)` 直接给出所有列。

拿 `[[3,2,1],[1,7,6],[2,7,7]]` 看：三行是 `(3,2,1)`、`(1,7,6)`、`(2,7,7)`，三列是 `(3,1,2)`、`(2,7,7)`、`(1,6,7)`，只有第二列在表里，答案 1。

重复行要按次数计。两行相同、某一列和它们相等，就是两对，所以用 `Counter`；换成 `set` 会少算。

## 参考代码

```python
from collections import Counter
from typing import List


def equalPairs(grid: List[List[int]]) -> int:
    rows = Counter(tuple(row) for row in grid)
    return sum(rows[col] for col in zip(*grid))


if __name__ == "__main__":
    assert equalPairs([[3, 2, 1], [1, 7, 6], [2, 7, 7]]) == 1
    assert equalPairs([[3, 1, 2, 2], [1, 4, 4, 5], [2, 4, 2, 2], [2, 4, 2, 2]]) == 3
    assert equalPairs([[1]]) == 1
    assert equalPairs([[1, 1], [1, 1]]) == 4
    assert equalPairs([[1, 2], [3, 4]]) == 0
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert equalPairs([[3, 2, 1], [1, 7, 6], [2, 7, 7]]) == 1
assert equalPairs([[3, 1, 2, 2], [1, 4, 4, 5], [2, 4, 2, 2], [2, 4, 2, 2]]) == 3
assert equalPairs([[1]]) == 1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n^2)$：每行、每列建键和哈希各是 $O(n)$。额外空间 $O(n^2)$，存了 $n$ 个长度为 $n$ 的 tuple。

## 边界

有重复行、重复列时，计数相乘式累加，全 $1$ 的 $2 \times 2$ 矩阵答案是 $4$。

$n = 1$ 时唯一的行和列相同，答案 $1$。

对称矩阵每行都等于对应的列，答案至少是 $n$。

## 追问

**不想拿整行做哈希键呢？**
把行插进 Trie，每个节点对应一个元素值，行末节点记次数；每一列沿 Trie 走一遍，走到底就加上次数。复杂度同样 $O(n^2)$，相同前缀的行可以共享节点。Trie 的写法见 `lc-208-implement-trie-prefix-tree`。

```python
def equalPairsTrie(grid):
    root = {}
    for row in grid:
        node = root
        for v in row:
            node = node.setdefault(v, {})
        node["#"] = node.get("#", 0) + 1
    n, ans = len(grid), 0
    for c in range(n):
        node = root
        for r in range(n):
            node = node.get(grid[r][c])
            if node is None:
                break
        else:
            ans += node.get("#", 0)
    return ans
```

**用滚动哈希把一行压成一个整数行不行？**
行，空间能省到 $O(n)$，但有碰撞风险，要么用双模数，要么命中后再逐元素复核一遍。

---
id: lc-135-candy
section: array-string
order: 15
level: A
title: LC 135 · 分发糖果
quick: "左右各扫一遍：从左扫保证比左边分高就比左边多一颗，从右扫保证比右边分高就比右边多，每位取两次结果的 $\\max$。每人至少 $1$ 颗。时间 $O(n)$，额外空间 $O(n)$。"
tags:
  - Array
  - Greedy
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 135. 分发糖果
    url: https://leetcode.cn/problems/candy/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

一排孩子各有一个评分。你需要为每个孩子分配糖果，使每人至少拿到一颗；对于任意两个相邻孩子，评分较高的孩子必须拿到更多糖果。求满足这些条件时所需的最少糖果总数。

### 输入与输出

实现 `candy(ratings) -> int`。`ratings[i]` 是第 i 个孩子的评分，返回总糖果数。评分相同的相邻孩子没有糖果数必须相等的要求。

### 约束与约定

- 孩子数 `1 <= n == len(ratings) <= 50000`。
- 评分在 `0` 到 `50000` 之间；只比较相邻孩子的评分。

### 示例

```text
输入：ratings = [1,0,2]
输出：5
```

评分 [1,0,2] 的一种最少分配为 [2,1,2]，总数为 5。

[官方原题与完整题面](https://leetcode.com/problems/candy/description/)。

## 解题思路与参考答案

## 题意

$n$ 个孩子站成一排，`ratings[i]` 是评分。每个孩子至少一颗糖；相邻里评分更高的必须糖更多。求最少糖果总数。

## 思路

我会左右各扫一遍再取较大值，因为单方向贪心不够，升序段和降序段会互相约束。第一遍从左往右，只保证比左边分高就比左边多一颗；第二遍从右往左，比右边分高就至少是右边加一。每位取两遍的较大值，两边约束就同时满足了。

拿 `[1, 0, 2]` 走一遍：初始都是 $1$；从左扫，只有 $2$ 比左边的 $0$ 高，变成 `[1, 1, 2]`；从右扫，第一个孩子比右边的 $0$ 高，抬成 $2$，得到 `[2, 1, 2]`，总数 $5$。

峰顶会被左右两趟一起抬高，这样分是正确的，也是最少的。一次扫描硬算谷到峰的长度容易漏，白板上别硬上。

## 参考代码

```python
from typing import List


def candy(ratings: List[int]) -> int:
    n = len(ratings)
    cand = [1] * n
    for i in range(1, n):
        if ratings[i] > ratings[i - 1]:
            cand[i] = cand[i - 1] + 1
    for i in range(n - 2, -1, -1):
        if ratings[i] > ratings[i + 1]:
            cand[i] = max(cand[i], cand[i + 1] + 1)
    return sum(cand)


if __name__ == "__main__":
    assert candy([1, 0, 2]) == 5
    assert candy([1, 2, 2]) == 4
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert candy([1, 0, 2]) == 5
assert candy([1, 2, 2]) == 4
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(n)$。

## 边界

全相等时相邻没有「更高」，每人 $1$ 颗，总数 $n$。严格递增时从左扫成 $1,2,\ldots,n$，严格递减时从右扫成 $n,\ldots,1$。山峰取左右约束的较大值，谷底保持 $1$。

## 追问

**相邻评分相等怎么分？**
相等就断开斜坡，从 $1$ 重新计。题面只约束「评分更高必须糖更多」，相等时糖数可以相同也可以不同，最少的策略就是只有不相等才加糖。两遍扫描的写法里只有 `>` 才更新，`==` 什么都不做，自然是对的。写成 `>=` 的话相等也会被迫递增，总数偏大。

**只要 $O(1)$ 额外空间呢？**
可以按斜坡分段算。每人先给 $1$ 颗；连续上升长度为 `up` 时额外加 $1+2+\cdots+\texttt{up}$，连续下降长度为 `down` 同理。峰顶被左右两边都加过，总和里多算了 $\min(\texttt{up},\texttt{down})$，要减掉；相等评分把斜坡断开，从下一段重新计。时间 $O(n)$，额外空间 $O(1)$。峰顶要取左右坡较长的那一侧，平台之后要重置，别把两段山连在一起。面试时两遍扫描更稳，这版只适合追问空间时讲。

```python
def candy_o1(ratings):
    n = len(ratings)
    ans = n
    i = 1
    while i < n:
        if ratings[i] == ratings[i - 1]:
            i += 1
            continue
        up = 0
        while i < n and ratings[i] > ratings[i - 1]:
            up += 1
            ans += up
            i += 1
        down = 0
        while i < n and ratings[i] < ratings[i - 1]:
            down += 1
            ans += down
            i += 1
        ans -= min(up, down)
    return ans
```

---
id: lc-135-candy
section: array-string
order: 15
level: A
title: LC 135 · 分发糖果
quick: >-
  左右各扫一遍：相邻分数更高必须更多糖，取两次结果的 $\max$。每人至少 $1$ 颗。时间 $O(n)$，额外空间
  $O(n)$。
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

## 题意

$n$ 个孩子站成一排，`ratings[i]` 是评分。每个孩子至少一颗糖；相邻里评分更高的必须糖更多。求最少糖果总数。

## 思路

单方向贪心不够：升序段和降序段会互相约束。我先从左往右，只保证比左边高就比左边多一颗。再从右往左，比右边高则至少是右边加一。每位取两次分配的较大值，两边约束就同时满足。

峰顶会被左右两趟一起抬高，这是正确且最少的。一次扫描硬算谷到峰长度容易漏，白板别硬上。

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

## 复杂度

时间 $O(n)$，额外空间 $O(n)$。

## 边界

- 全相等：相邻没有「更高」，每人 $1$ 颗，总数 $n$。
- 严格递增：从左扫成 $1,2,\ldots,n$；严格递减：从右扫成 $n,\ldots,1$。
- 山峰、山谷：峰顶取左右约束的较大值；谷底保持 $1$。

## 追问

- **相邻评分相等怎么分？** 题面只约束「评分更高必须糖更多」，相等时糖数可以相同也可以不同。最少策略是不相等才加糖，相等就断开斜坡、从 $1$ 重新计。两遍扫描的写法里，只有 `>` 才更新，`==` 什么都不做，自然正确。不要写成 `>=`，否则相等也会被迫递增加糖，总数偏大。

- **只要 $O(1)$ 额外空间？** 每人先给 $1$ 颗。按斜坡分段：连续上升长度为 `up` 时额外加 $1+2+\cdots+\texttt{up}$，连续下降长度 `down` 同理。峰顶被左右两边都加过，总和里多算了 $\min(\texttt{up},\texttt{down})$，要减掉。相等评分把斜坡断开，从下一段重新计。时间 $O(n)$，额外空间 $O(1)$。这块容易栽：峰顶要取左右坡较长的那一侧，平台（相等）后要重置，不能把两段山连在一起。面试两遍扫描更稳，这版只适合追问空间。

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

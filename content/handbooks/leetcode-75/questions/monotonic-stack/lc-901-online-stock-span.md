---
id: lc-901-online-stock-span
section: monotonic-stack
order: 2
level: S
title: LC 901 · 股票价格跨度
quick: >-
  栈里存 `(价格, 跨度)`，价格从底到顶严格递减。新价格把所有 $\le$ 它的栈顶弹掉，并把它们的跨度累加到自己身上，再入栈。`next`
  均摊 $O(1)$，空间 $O(n)$。
tags:
  - Stack
  - Monotonic Stack
  - Design
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 901. Online Stock Span
    url: https://leetcode.com/problems/online-stock-span/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

实现 `StockSpanner`：`next(price)` 接收当天股价，返回当天的跨度，即从今天往前数（含今天）连续多少天价格 $\le$ 今天的价格。价格 $\le 10^5$，最多调用 $10^4$ 次。

## 思路

跨度就是「今天到上一个严格更高价格之间的天数」。在线处理时，维护一个单调栈，存「价格，这个价格已经吞掉的天数」。新价格来了，栈顶价格 $\le$ 它的全部弹出，跨度加起来再加上今天的 $1$。

被弹掉的那些天以后也用不到：之后任何一天如果能越过今天，也一定能越过它们，它们的天数已经合并进今天的跨度。所以栈里剩下的价格严格递减。每天暴力往回数是 $O(n)$ 一次，单调递增序列会退化到总体 $O(n^2)$。

## 参考代码

```python
from typing import List, Tuple


class StockSpanner:
    def __init__(self) -> None:
        self.stack: List[Tuple[int, int]] = []

    def next(self, price: int) -> int:
        span = 1
        while self.stack and self.stack[-1][0] <= price:
            span += self.stack.pop()[1]
        self.stack.append((price, span))
        return span


if __name__ == "__main__":
    s = StockSpanner()
    prices = [100, 80, 60, 70, 60, 75, 85]
    assert [s.next(p) for p in prices] == [1, 1, 1, 2, 1, 4, 6]

    s2 = StockSpanner()
    assert [s2.next(p) for p in [5, 5, 5]] == [1, 2, 3]

    s3 = StockSpanner()
    assert [s3.next(p) for p in [3, 2, 1]] == [1, 1, 1]

    s4 = StockSpanner()
    assert [s4.next(p) for p in [1, 2, 3, 4]] == [1, 2, 3, 4]
    print("ok")
```

## 复杂度

`next` 均摊 $O(1)$：每个价格入栈、出栈各一次。空间 $O(n)$。

## 边界

- 相等价格要算进跨度：弹栈条件是 $\le$，`[5, 5, 5]` 得到 `[1, 2, 3]`。
- 单调递减：每次都不弹，跨度全是 $1$，栈长到 $n$。
- 单调递增：每次弹掉唯一的栈顶，栈始终只有一个元素。

## 追问

- **离线版本，给整个数组求每一天的跨度？** 从左往右维护下标的单调栈，弹完后栈顶就是上一个严格更高的下标 `p`，跨度为 `i - p`（栈空时是 `i + 1`）。和 `lc-739-daily-temperatures` 是同一个模板的反方向。

```python
def stockSpans(prices):
    ans, stack = [], []
    for i, p in enumerate(prices):
        while stack and prices[stack[-1]] <= p:
            stack.pop()
        ans.append(i - stack[-1] if stack else i + 1)
        stack.append(i)
    return ans
```

- **改成数「严格小于今天」的连续天数？** 弹栈条件改成 `<`，栈里就允许出现相等价格，其它不变。

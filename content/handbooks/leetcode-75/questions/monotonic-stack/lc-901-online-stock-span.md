---
id: lc-901-online-stock-span
section: monotonic-stack
order: 2
level: S
title: LC 901 · 股票价格跨度
quick: >-
  跨度就是今天到上一个严格更高价格之间的天数，用单调栈存 `(价格, 跨度)`，价格从底到顶严格递减。新价格把所有 $\le$
  它的栈顶弹掉，把它们的跨度累加到自己身上，再入栈。`next` 均摊 $O(1)$，空间 $O(n)$。
tags:
  - Stack
  - Monotonic Stack
  - Design
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 901. Online Stock Span
    url: 'https://leetcode.com/problems/online-stock-span/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

设计一个按天接收股票价格的对象。每次给出今天的价格时，返回今天的价格跨度：从今天向过去连续数，有多少天的价格都不大于今天，包括今天本身。遇到第一个价格高于今天的历史日就停止，不能跳过该日继续往前计数。

### 输入与输出

实现类 `StockSpanner`：构造器创建没有历史数据的对象；`next(price: int) -> int` 记录当天价格并返回当天跨度。价格按时间先后依次传入，第一天跨度必为 1。

### 约束

- `1 <= price <= 10^5`。
- next 最多调用 `10^4` 次。

### 示例

```text
输入：["StockSpanner", "next", "next", "next", "next", "next", "next", "next"]
[[], [100], [80], [60], [70], [60], [75], [85]]
输出：[null, 1, 1, 1, 2, 1, 4, 6]
```

构造器输出记为 null。最后一天价格为 85，之前紧邻的 75、60、70、60、80 均不超过 85，更早的 100 则超过，所以跨度为 6。

## 解题思路与参考答案

## 题意

实现 `StockSpanner`：`next(price)` 接收当天股价，返回当天的跨度，即从今天往前数（含今天）连续多少天价格 $\le$ 今天的价格。价格 $\le 10^5$，最多调用 $10^4$ 次。

## 思路

跨度就是「今天到上一个严格更高价格之间的天数」，我会维护一个单调栈，存「价格，这个价格已覆盖的连续天数」。新价格来了，栈顶价格 $\le$ 它的全部弹出，跨度加起来再加上今天的 $1$。每天暴力往回数是一次 $O(n)$，遇到单调递增序列总体会退化到 $O(n^2)$。

被弹掉的那些天以后用不到了。之后任何一天如果能越过今天，也一定能越过它们，它们的天数已经合并进今天的跨度里。所以栈里剩下的价格严格递减。

拿 `[100, 80, 60, 70, 60, 75, 85]` 走一遍。前三天依次入栈，跨度都是 1。70 弹掉 `(60, 1)`，跨度 2；下一个 60 不弹，跨度 1。75 弹掉 `(60, 1)` 和 `(70, 2)`，跨度 $1+1+2=4$。85 再弹掉 `(75, 4)` 和 `(80, 1)`，跨度 $1+4+1=6$。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

把一次完整的操作序列当作一个测试：新建对象、执行操作，再检查返回值和操作后的状态。下一个独立场景重新建对象，避免历史状态掩盖错误。

```python
s = StockSpanner()
prices = [100, 80, 60, 70, 60, 75, 85]
assert [s.next(p) for p in prices] == [1, 1, 1, 2, 1, 4, 6]
s2 = StockSpanner()
assert [s2.next(p) for p in [5, 5, 5]] == [1, 2, 3]
s3 = StockSpanner()
assert [s3.next(p) for p in [3, 2, 1]] == [1, 1, 1]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

`next` 均摊 $O(1)$：每个价格入栈、出栈各一次。空间 $O(n)$。

## Edge Cases

相等价格要算进跨度，所以弹栈条件是 $\le$，`[5, 5, 5]` 得到 `[1, 2, 3]`。

单调递减时每次都不弹，跨度全是 $1$，栈长到 $n$。

单调递增时每次弹掉唯一的栈顶，栈里始终只有一个元素。

## 追问

**离线版本，给整个数组求每一天的跨度呢？**
从左往右维护下标的单调栈，弹完以后栈顶就是上一个严格更高的下标 `p`，跨度为 `i - p`，栈空时是 `i + 1`。和 `lc-739-daily-temperatures` 是同一个模板，方向反过来。

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

**改成数「严格小于今天」的连续天数呢？**
弹栈条件改成 `<`，栈里就允许出现相等价格，其它不变。

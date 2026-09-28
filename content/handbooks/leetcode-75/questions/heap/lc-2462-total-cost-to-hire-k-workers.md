---
id: lc-2462-total-cost-to-hire-k-workers
section: heap
order: 4
level: A
title: LC 2462 · 雇佣 K 位工人的总代价
quick: >-
  左右各一个小根堆，分别装前 `candidates` 个和后 `candidates` 个工人，两个指针往中间补人。每轮比较两个堆顶，取更小的（相等取左边），弹出后从同一侧补一个。时间
  $O((k+c)\log c)$，额外空间 $O(c)$。
tags:
  - Heap
  - Two Pointers
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 2462. Total Cost to Hire K Workers
    url: https://leetcode.com/problems/total-cost-to-hire-k-workers/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

`costs[i]` 是第 $i$ 个工人的代价。进行 $k$ 轮雇佣，每轮从剩余工人的前 `candidates` 个和后 `candidates` 个里选代价最小的，代价相同选下标更小的。被雇的人移出队伍。剩余人数少于 `2 * candidates` 时前后两组会重叠，就从全体剩余里选。返回总代价。

## 思路

每轮只看两端各 `candidates` 个人，用两个小根堆分别维护左侧组和右侧组。指针 `l`、`r` 指向还没进入任何堆的区间 $[l, r]$，某侧堆弹出后就从同一侧补一个人，`l` 右移或 `r` 左移。

左右组不能重叠：补人时要求 $l\le r$，指针交错后中间已经没人，两个堆合起来就是全部剩余工人，继续比堆顶即可。平局选下标小的：左堆里的下标全都小于右堆，所以两堆顶相等时取左边。

每轮线性扫两端 $2c$ 个人找最小值是 $O(k\cdot c)$，最坏 $10^{10}$ 量级，太慢。

## 参考代码

```python
import heapq
import random
from typing import List


def totalCost(costs: List[int], k: int, candidates: int) -> int:
    l, r = 0, len(costs) - 1
    left: List[int] = []
    right: List[int] = []
    total = 0
    for _ in range(k):
        while len(left) < candidates and l <= r:
            heapq.heappush(left, costs[l])
            l += 1
        while len(right) < candidates and l <= r:
            heapq.heappush(right, costs[r])
            r -= 1
        if right and (not left or right[0] < left[0]):
            total += heapq.heappop(right)
        else:
            total += heapq.heappop(left)
    return total


def simulate(costs: List[int], k: int, candidates: int) -> int:
    workers = list(costs)
    total = 0
    for _ in range(k):
        n = len(workers)
        pool = set(range(min(candidates, n))) | set(range(max(0, n - candidates), n))
        best = min(pool, key=lambda i: (workers[i], i))
        total += workers.pop(best)
    return total


if __name__ == "__main__":
    assert totalCost([17, 12, 10, 2, 7, 2, 11, 20, 8], 3, 4) == 11
    assert totalCost([1, 2, 4, 1], 3, 3) == 4
    assert totalCost([5], 1, 1) == 5
    assert totalCost([3, 3, 3, 3], 4, 1) == 12
    random.seed(1)
    for _ in range(300):
        n = random.randint(1, 10)
        costs = [random.randint(1, 6) for _ in range(n)]
        k = random.randint(1, n)
        c = random.randint(1, n)
        assert totalCost(costs, k, c) == simulate(costs, k, c)
    print("ok")
```

## 复杂度

初始建堆最多 $2c$ 次入堆，之后每轮一次出堆、至多一次入堆，时间 $O((k+c)\log c)$，$c$ 为 `candidates`。额外空间 $O(c)$。

## 边界

- $2c\ge n$：第一轮左堆装满后 `l` 和 `r` 交错，右堆可能为空或很少，比较时要处理某侧堆空。
- 平局：左右堆顶相等时取左，因为左侧下标更小；同一个堆内平局不影响总代价。
- $k=n$：所有人都会被雇，答案等于 `sum(costs)`，可以用来自检。

## 追问

- **要返回被雇工人的下标？** 堆里存 `(cost, index)`，元组比较自动按代价再按下标，平局规则直接由元组保证，两堆顶也改为比较元组。
- **为什么不能只用一个堆？** 一个堆存所有候选时，弹出后不知道该从哪一侧补人。存 `(cost, index)` 后按下标判断属于左组还是右组也可以，但两个堆更直观。和 `lc-215-kth-largest-element-in-an-array` 一样，都是用堆把「每轮取最小」从线性降到对数。

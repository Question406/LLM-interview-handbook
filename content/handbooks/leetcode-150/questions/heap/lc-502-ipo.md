---
id: lc-502-ipo
section: heap
order: 2
level: A
title: LC 502 · IPO
quick: >-
  项目按启动资本排序。资本够的利润进大根堆，每次取堆顶做，最多 $k$ 次。时间
  $O(n\log n)$。
tags:
  - Heap
  - Greedy
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 502. IPO
    url: https://leetcode.cn/problems/ipo/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

$n$ 个项目，启动资本 `capital[i]`，做完利润 `profits[i]` 加进当前资本。初始资本 $w$，最多做 $k$ 个，求最终资本。

## 思路

当前资本下，能做的项目里应选利润最大。我把项目按资本升序，指针向右扫入所有 `capital <= w` 的利润（取负放进小根堆当大根堆）。每次弹堆顶，$w$ 增加，再解锁新项目。堆空说明做不下去。

常见误区是：每次扫描全部未做项目，那是 $O(kn)$。

## 参考代码

```python
import heapq
from typing import List


def findMaximizedCapital(k: int, w: int, profits: List[int], capital: List[int]) -> int:
    projects = sorted(zip(capital, profits))
    heap = []
    i, n = 0, len(projects)
    for _ in range(k):
        while i < n and projects[i][0] <= w:
            heapq.heappush(heap, -projects[i][1])
            i += 1
        if not heap:
            break
        w += -heapq.heappop(heap)
    return w


if __name__ == "__main__":
    assert findMaximizedCapital(2, 0, [1, 2, 3], [0, 1, 1]) == 4
    assert findMaximizedCapital(3, 0, [1, 2, 3], [0, 1, 2]) == 6
    assert findMaximizedCapital(1, 0, [1, 2, 3], [1, 1, 2]) == 0
    print("ok")
```

## 复杂度

排序 $O(n\log n)$，每个项目进出堆一次 $O(n\log n)$。额外空间 $O(n)$。

## 边界

- 初始资本一个都做不了：第一轮解锁循环不进，堆空，直接返回 $w$。
- $k$ 大于能做的数量：某次堆空就 `break`，不会空弹。
- 利润为 $0$：仍可能解锁后续更高资本项目，该做还是做，只是 $w$ 不变。

## 追问

- **项目只能做一次？** 已经保证了：按资本排序后指针 `i` 只增不减，每个项目的利润最多入堆一次，弹出就是「做完」。别每次从全部未做项目里重扫，那是 $O(kn)$，实现上也容易重复选。

```python
# 指针 i 只前进：projects[i] 入堆后不会再看
while i < n and projects[i][0] <= w:
    heapq.heappush(heap, -projects[i][1])
    i += 1
```

- **有截止日期？** 这题没有时间，资本够就能做。若每个项目占 $1$ 单位时间且有截止时刻 $d_i$，就变成「带截止的单位时间调度」：按截止升序扫，小根堆装着已选利润；还能塞进当前截止前就做，否则若当前利润大于堆里最小利润就替换。堆的键是利润不是资本。更一般的「时长 $+ $ 截止 $+ $ 利润」是加权区间调度，要按截止 DP，不再是这题这套贪心。

```python
def maxProfitWithDeadline(jobs):
    # jobs: (deadline, profit)，每个占时 1，时间从 1 计
    jobs = sorted(jobs)
    heap = []
    for d, p in jobs:
        heapq.heappush(heap, p)
        if len(heap) > d:
            heapq.heappop(heap)
    return sum(heap)
```

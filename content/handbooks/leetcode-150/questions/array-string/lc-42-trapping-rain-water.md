---
id: lc-42-trapping-rain-water
section: array-string
order: 16
level: S
title: LC 42 · 接雨水
quick: >-
  左右指针加左右最大高度。矮的一侧先结算：当前柱与该侧最大值的差就是积水。时间 $O(n)$，额外空间 $O(1)$。
tags:
  - Array
  - Two Pointers
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 42. 接雨水
    url: https://leetcode.cn/problems/trapping-rain-water/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

`height[i]` 是宽度为 $1$ 的柱子高度。下雨后，柱子之间能接多少单位水。

## 思路

位置 $i$ 的水位由左右最高柱的较小值决定：$\min(L_{\max}, R_{\max}) - \texttt{height}[i]$（为正才积水）。双指针：维护 `left_max` / `right_max`。哪侧最大高度更小，水位就被该侧卡住，先结算该侧并收缩指针。

单调栈按「凹槽」分段累加也对，空间 $O(n)$。白板我优先双指针，画一列说明「矮侧先算」。

## 参考代码

```python
from typing import List


def trap(height: List[int]) -> int:
    lo, hi = 0, len(height) - 1
    left_max = right_max = 0
    ans = 0
    while lo < hi:
        if height[lo] < height[hi]:
            left_max = max(left_max, height[lo])
            ans += left_max - height[lo]
            lo += 1
        else:
            right_max = max(right_max, height[hi])
            ans += right_max - height[hi]
            hi -= 1
    return ans


if __name__ == "__main__":
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
    assert trap([4, 2, 0, 3, 2, 5]) == 9
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。每个下标结算一次。

## 边界

- 长度 $\lt 3$ 或整体单调：形不成凹槽，积水 $0$。
- 高度全相等：左右最高相等且等于自身，差值为 $0$。
- 最高柱在两端或在中间：水位由较矮一侧卡住，双指针仍从矮侧先结算。

## 追问

- **二维接雨水（LC 407）？** 一维里水位是左右最高的较小值；二维里是「通向边界的所有路径上，路径最高点的最小值」。从边界灌水：把所有边界格放进小根堆并标记访问，堆顶是当前最矮的「墙」。弹出高度 $h$，看四邻：没访问的邻居若比 $h$ 矮，差值就是积水，再把邻居以 $\max(h, \text{邻居高})$ 入堆，相当于水位被抬到至少 $h$。每个格子入堆一次，时间 $O(mn\log(mn))$，额外空间 $O(mn)$。这块容易栽：从内部开始搜（边界会漏水），以及入堆高度用邻居原高而不是抬升后的水位。不要对每一格再跑一遍一维接雨水。

```python
import heapq


def trapRainWater(heightMap):
    if not heightMap or not heightMap[0]:
        return 0
    m, n = len(heightMap), len(heightMap[0])
    vis = [[False] * n for _ in range(m)]
    heap = []
    for i in range(m):
        for j in range(n):
            if i in (0, m - 1) or j in (0, n - 1):
                heapq.heappush(heap, (heightMap[i][j], i, j))
                vis[i][j] = True
    ans = 0
    while heap:
        h, x, y = heapq.heappop(heap)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < m and 0 <= ny < n and not vis[nx][ny]:
                vis[nx][ny] = True
                ans += max(0, h - heightMap[nx][ny])
                heapq.heappush(heap, (max(h, heightMap[nx][ny]), nx, ny))
    return ans
```

- **要输出每一列的水量？** 第 $i$ 列积水仍是 $\min(L_{\max}[i], R_{\max}[i]) - \texttt{height}[i]$。可以预处理：从左扫 `left[i]` 为 $0\ldots i$ 的最高，从右扫 `right[i]` 为 $i\ldots n-1$ 的最高，再逐列写差值。双指针也能边走边填数组，但预处理更好讲。时间 $O(n)$，额外空间 $O(n)$。总和就是原题答案。这块容易栽：`left[i]` 写成严格左侧而漏掉自身。自身更高时水位被自己顶掉，差值仍为 $0$，包含自身是对的。高度全相等或单调时数组应全 $0$。

```python
def trap_per_column(height):
    n = len(height)
    if n == 0:
        return []
    left = [0] * n
    right = [0] * n
    left[0] = height[0]
    for i in range(1, n):
        left[i] = max(left[i - 1], height[i])
    right[-1] = height[-1]
    for i in range(n - 2, -1, -1):
        right[i] = max(right[i + 1], height[i])
    return [min(left[i], right[i]) - height[i] for i in range(n)]
```

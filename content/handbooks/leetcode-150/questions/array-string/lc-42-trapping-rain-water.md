---
id: lc-42-trapping-rain-water
section: array-string
order: 16
level: S
title: LC 42 · 接雨水
quick: >-
  用双指针从两端往中间走，记下两侧见过的最高柱，每次先处理较低的一侧：这一侧的最高柱减当前柱高就是这里的积水，因为另一侧已经有足够高的挡板。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Array
  - Two Pointers
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 42. 接雨水
    url: 'https://leetcode.cn/problems/trapping-rain-water/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

用数组 `height` 表示从左到右排列的一组柱子，第 i 根柱子的高度是 `height[i]`，每根柱子的宽度都是 1。雨水只能停留在柱子之间有较高柱子围住的凹处，左右两端外侧的水会流走。求下雨后能够存住的总水量。

### 接口与输出

实现 `trap(height: List[int]) -> int`，返回按单位方格计量的总水量；不要返回每个位置的水量列表。

### 合法输入与约束

`1 <= len(height) <= 20000`，`0 <= height[i] <= 100000`。柱子高度为 0 合法；只有一根柱子或没有形成凹处时，结果可以为 0。

### 示例

```text
输入：height = [0,1,0,2,1,0,1,3,2,1,2,1]
输出：6
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/trapping-rain-water/description/)。

## 解题思路与参考答案

## 题意

`height[i]` 是宽度为 $1$ 的柱子高度。下雨后，柱子之间能接多少单位水。

## 思路

我会用双指针，一遍扫完、只用常数空间。出发点是位置 $i$ 的水位由左右最高柱的较小值决定，积水是 $\min(L_{\max}, R_{\max}) - \texttt{height}[i]$（为正才算）。双指针从两端向中间走，维护已见的 `left_max` / `right_max`；较低那一侧的另一边已经有足够高的柱子挡水，所以这一侧的水量现在就能定下来，定完再移动指针。

拿 `[4, 2, 0, 3, 2, 5]` 走一遍：右端的 $5$ 比左边都高，所以一直从左边结算，`left_max` 是 $4$，于是 $2$ 上存 $2$、$0$ 上存 $4$、$3$ 上存 $1$、$2$ 上存 $2$，合计 $9$。

单调栈按凹槽分段累加也对，空间 $O(n)$。白板上我优先写双指针，画一列说明为什么矮的一侧先算。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
assert trap([4, 2, 0, 3, 2, 5]) == 9
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。每个下标结算一次。

## Edge Cases

长度 $\lt 3$ 或整体单调时形不成凹槽，积水是 $0$。高度全相等时左右最高都等于自身，差值为 $0$。最高柱在两端还是中间都一样，水位由较矮的一侧卡住，双指针照样从矮侧先结算。

## 追问

**二维接雨水怎么做（LC 407）？**
从 outer edge 向内灌水，用小根堆。一维里水位是左右最高的较小值；二维里是「通向 outer edge 的所有路径上，路径最高点的最小值」。先把所有 outer-edge cells 放进小根堆并标记访问，堆顶就是当前最矮的「墙」。弹出高度 $h$，看四个邻居：没访问过且比 $h$ 矮的，差值就是积水，再把邻居以 $\max(h, \text{邻居高})$ 入堆，相当于水位被抬到至少 $h$。每个格子入堆一次，时间 $O(mn\log(mn))$，额外空间 $O(mn)$。从内部开始搜会漏掉流向 outer edge 的排水路径；入堆高度要用抬升后的水位，用邻居原高就错了。也别对每一格再跑一遍一维接雨水。

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

**要输出每一列的水量呢？**
预处理左右最高就行，第 $i$ 列积水仍是 $\min(L_{\max}[i], R_{\max}[i]) - \texttt{height}[i]$。从左扫出 `left[i]`，即 $0\ldots i$ 的最高；从右扫出 `right[i]`，即 $i\ldots n-1$ 的最高；再逐列写差值，总和就是原题答案。双指针也能边走边填数组，但预处理更好讲。时间 $O(n)$，额外空间 $O(n)$。`left[i]` 要包含自身：自身更高时水位被自己顶掉，差值为 $0$，这正是对的，写成严格左侧就漏了。高度全相等或单调时，结果应该全是 $0$。

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

---
id: lc-1732-find-the-highest-altitude
section: prefix-sum
order: 1
level: A
title: LC 1732 · 找到最高海拔
quick: >-
  海拔就是 `gain` 的前缀和，起点海拔 $0$ 也算。一边累加一边取最大值。时间 $O(n)$，额外空间 $O(1)$。
tags:
  - Array
  - Prefix Sum
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1732. Find the Highest Altitude
    url: https://leetcode.com/problems/find-the-highest-altitude/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

骑行经过 $n+1$ 个点，起点海拔为 $0$。`gain[i]` 是从点 $i$ 到点 $i+1$ 的净海拔变化。返回所有点中的最高海拔。$1 \le n \le 100$，$-100 \le gain[i] \le 100$。

## 思路

点 $i$ 的海拔是 $\sum_{t \lt i} gain[t]$，也就是前缀和。用一个变量 `cur` 累加，同时维护 `best`。`best` 初始化为 $0$，因为起点本身也是一个点；全程下坡时答案就是 $0$。

不需要真开一个前缀和数组，只看最大值时滚动变量就够了。

## 参考代码

```python
from typing import List


def largestAltitude(gain: List[int]) -> int:
    cur = best = 0
    for g in gain:
        cur += g
        best = max(best, cur)
    return best


if __name__ == "__main__":
    assert largestAltitude([-5, 1, 5, 0, -7]) == 1
    assert largestAltitude([-4, -3, -2, -1, 4, 3, 2]) == 0
    assert largestAltitude([5]) == 5
    assert largestAltitude([-1]) == 0
    assert largestAltitude([1, -1, 1, -1, 3]) == 3
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- 全是负数：最高点是起点，返回 $0$。`best` 若初始化为负无穷或 `gain[0]` 就错了。
- 最高点在最后一步：循环里每步都要比较，不能只在下坡前比。
- 中间回到 $0$：不影响，照常累加。

## 追问

- **求一段路上的最大净爬升（某点海拔减去更早某点海拔的最大值）？** 这是「前缀和差的最大值」，扫的同时记录见过的最小前缀和 `low`，用 `cur - low` 更新答案。等价于对 `gain` 做最大子数组和（Kadane）。时间 $O(n)$，额外空间 $O(1)$。

```python
def maxClimb(gain):
    cur = low = 0
    best = 0
    for g in gain:
        cur += g
        best = max(best, cur - low)
        low = min(low, cur)
    return best
```

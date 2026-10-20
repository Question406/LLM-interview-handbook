---
id: lc-55-jump-game
section: array-string
order: 9
level: S
title: LC 55 · 跳跃游戏
quick: >-
  维护最远可达下标 `farthest`。扫到 $i$ 时若 $i \gt$ `farthest` 则失败；否则用 $i+$`nums[i]`
  更新最远。时间 $O(n)$，额外空间 $O(1)$。
tags:
  - Array
  - Greedy
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 55. 跳跃游戏
    url: https://leetcode.cn/problems/jump-game/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

`nums[i]` 表示从下标 $i$ 最多向前跳的步数。从 $0$ 出发，问能否到达最后一个下标。

## 思路

贪心维护当前能覆盖的最远下标。按顺序扫 $i=0\ldots n-1$：若 $i$ 已经超出 `farthest`，后面都到不了，返回失败；否则 `farthest = max(farthest, i + nums[i])`。`farthest` 碰到或越过终点即可成功。

DP「每个位置是否可达」也是 $O(n)$，但常写出 $O(n^2)$。先解释当前可以到达的覆盖范围。

## 参考代码

```python
from typing import List


def canJump(nums: List[int]) -> bool:
    farthest = 0
    for i, step in enumerate(nums):
        if i > farthest:
            return False
        farthest = max(farthest, i + step)
        if farthest >= len(nums) - 1:
            return True
    return True


if __name__ == "__main__":
    assert canJump([2, 3, 1, 1, 4]) is True
    assert canJump([3, 2, 1, 0, 4]) is False
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- $n=1$：已经站在终点，返回 `true`。
- 中间有 $0$ 但能从更早位置越过：`farthest` 会先跨过这个 $0$。
- 最后一个是 $0$：只要能踩到它就算到达，不必再往前跳。

## 追问

- **最少跳跃次数？** 覆盖范围只能回答「能不能」，步数要把覆盖区间当成 BFS 的一层。扫 $i$，用 $i+$`nums[i]` 更新下一层最远 `farthest`；当 $i$ 走到本层右端 `end` 时必须再跳一次：`steps += 1`，`end = farthest`。循环扫到倒数第二个即可，站在终点不用再跳。时间 $O(n)$，额外空间 $O(1)$。本题若不保证可达，某层结束时 `farthest == end` 且还没到终点就是失败。不要每个位置枚举落点做 $O(n^2)$ DP。独立卡见 `lc-45-jump-game-ii`。

```python
def jump(nums):
    steps = end = farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == end:
            steps += 1
            end = farthest
    return steps
```

- **每跳有代价呢？** 覆盖最远不再最优：可能故意跳得近，到达代价更低的格子。令 `dp[i]` 为到达 $i$ 的最小代价，初始 `dp[0]=0` 其余为无穷。从 $i$ 枚举一步到 $j=i+1\ldots i+$`nums[i]`，用 `dp[i] + cost[i]` 松弛 `dp[j]`。时间 $O(\sum \texttt{nums}[i])$，最坏 $O(n^2)$，额外空间 $O(n)$。代价任意且像边权一样时，也可以把「$i \to i+k$」看成边，跑 Dijkstra。常见错误是继续用「每层只跳一次」的贪心，以及不可达位置没有跳过导致用无穷去更新。若代价全是 $1$，DP 就退回最少步数。

```python
def jump_with_cost(nums, cost):
    n = len(nums)
    inf = 10**18
    dp = [inf] * n
    dp[0] = 0
    for i in range(n):
        if dp[i] >= inf:
            continue
        for step in range(1, nums[i] + 1):
            j = i + step
            if j >= n:
                break
            cand = dp[i] + cost[i]
            if cand < dp[j]:
                dp[j] = cand
    return dp[-1]
```

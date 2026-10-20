---
id: lc-45-jump-game-ii
section: array-string
order: 10
level: A
title: LC 45 · 跳跃游戏 II
quick: "把相同跳数能到达的区间看作 BFS 一层。end 记录当前层右端，farthest 记录这一层各位置再跳一次能到的最远位置。扫描到 end 就完成一层，跳数加一。题目保证可达，时间 $O(n)$，额外空间 $O(1)$。"
tags:
  - Array
  - Greedy
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 45. 跳跃游戏 II
    url: https://leetcode.cn/problems/jump-game-ii/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

`nums[i]` 为从 $i$ 最多可跳步数，保证能到达最后一格。求到达终点的最少跳跃次数。

## 思路

把相同跳跃次数能够到达的位置看作 BFS 的一层。遍历这一层时，用 `i + nums[i]` 记录再跳一次的最远位置 `farthest`。扫到本层右端 `end` 后，当前层已经处理完，将跳数加一，并把 `end` 更新为 `farthest`，开始下一层。

不要在每个位置枚举落点做 $O(n^2)$ DP。把「一次跳跃能落到的区间」当 BFS 一层讲清楚，再写 `end` / `farthest`。循环只需扫到倒数第二个：站在终点不必再跳。

## 参考代码

```python
from typing import List


def jump(nums: List[int]) -> int:
    steps = 0
    end = 0
    farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == end:
            steps += 1
            end = farthest
    return steps


if __name__ == "__main__":
    assert jump([2, 3, 1, 1, 4]) == 2
    assert jump([2, 3, 0, 1, 4]) == 2
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。每个下标进一层、出一层。

## 边界

- $n=1$：已在终点，循环不进，返回 $0$ 步。
- 每步都是 $1$：每一层只多覆盖一格，答案是 $n-1$。
- 第一步就能到终点：第一次碰到 `i == end` 时 `farthest` 已 $\ge n-1$，返回 $1$。

## 追问

- **只问能否到达？** 不再分层计数，只维护最远可达 `farthest`。扫到 $i$ 时若 $i \gt$ `farthest`，中间出现跨越不了的 $0$，失败；否则用 $i+$`nums[i]` 更新最远，碰到或越过终点就成功。时间 $O(n)$，额外空间 $O(1)$。本题保证可达，所以最少步数版不用写失败分支；改成「能否」后必须写。不要对每个位置枚举落点做成 $O(n^2)$ DP。独立卡见 `lc-55-jump-game`。

```python
def canJump(nums):
    farthest = 0
    for i, step in enumerate(nums):
        if i > farthest:
            return False
        farthest = max(farthest, i + step)
        if farthest >= len(nums) - 1:
            return True
    return True
```

- **输出一条最少跳数路径？** 贪心分层本身就是 BFS，第一次覆盖到的下标一定来自最短路径上的某一跳。扩展 `farthest` 时，把新覆盖的 `(old_farthest, reach]` 全部记 `parent[j] = i`。扫完从终点沿 `parent` 回 $0$ 再反转。时间 $O(n)$，额外空间 $O(n)$。从终点往左找「最左能跳到当前点的 $i$」也能还原，但是 $O(n^2)$。这块容易栽：整层共用同一个前驱（层内不是所有格都能跳到层右端），以及 $n=1$ 时 `parent[0]` 仍是 $-1$ 要单独返回 `[0]`。路径下标序列长度应等于最少步数加一。

```python
def jump_path(nums):
    n = len(nums)
    if n == 1:
        return [0]
    parent = [-1] * n
    farthest = 0
    end = 0
    for i in range(n - 1):
        reach = i + nums[i]
        if reach > farthest:
            for j in range(farthest + 1, min(reach + 1, n)):
                parent[j] = i
            farthest = reach
        if i == end:
            end = farthest
            if end >= n - 1:
                break
    path = []
    cur = n - 1
    while cur != -1:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path
```

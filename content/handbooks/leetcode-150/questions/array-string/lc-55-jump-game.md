---
id: lc-55-jump-game
section: array-string
order: 9
level: S
title: LC 55 · 跳跃游戏
quick: "贪心维护最远可达下标 `farthest`：扫到 $i$ 时若 $i \\gt$ `farthest` 就失败，否则用 $i+$`nums[i]` 更新最远，碰到终点就成功。时间 $O(n)$，额外空间 $O(1)$。"
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

## 题目描述

给定非负整数数组 `nums`。你最初站在下标 0，处于下标 i 时，可以向右跳不超过 `nums[i]` 个位置。判断是否存在一系列合法跳跃，使你到达数组最后一个位置。数组只有一个元素时，起点已经是终点。

### 输入与输出

实现 `canJump(nums) -> bool`。能够到达最后一个下标返回 True，否则返回 False；不要求输出跳跃路径或跳跃次数。

### 约束

- `1 <= len(nums) <= 10^4`。
- `0 <= nums[i] <= 10^5`。
- 只能向下标增大的方向移动，某一项为 0 表示不能从该位置继续向前跳。

### 示例

```text
输入：nums = [2,3,1,1,4]
输出：true
```

[LeetCode 原题](https://leetcode.com/problems/jump-game/description/)

## 解题思路与参考答案

## 题意

`nums[i]` 表示从下标 $i$ 最多向前跳的步数。从 $0$ 出发，问能否到达最后一个下标。

## 思路

我会贪心维护当前能覆盖到的最远下标，能不能到终点只取决于覆盖范围有没有断。按顺序扫 $i=0\ldots n-1$：$i$ 已经超出 `farthest` 的话，后面都到不了，返回失败；否则 `farthest = max(farthest, i + nums[i])`，碰到或越过终点就成功。

拿 `[3, 2, 1, 0, 4]` 走一遍：下标 $0$ 到 $3$ 每一步算出来的最远都是 $3$，全卡在那个 $0$ 上；扫到下标 $4$ 时 $4 \gt 3$，返回 `false`。

「每个位置是否可达」的 DP 也能做到 $O(n)$，但很容易写成 $O(n^2)$，所以我先讲覆盖范围。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert canJump([2, 3, 1, 1, 4]) is True
assert canJump([3, 2, 1, 0, 4]) is False
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

$n=1$ 时已经站在终点，返回 `true`。中间有 $0$ 但能从更早的位置越过时，`farthest` 会先跨过这个 $0$。最后一个是 $0$ 也没关系，踩到它就算到达，不用再往前跳。

## 追问

**最少跳跃次数呢？**
把覆盖区间当成 BFS 的一层来数。覆盖范围只能回答「能不能」，要步数就扫 $i$、用 $i+$`nums[i]` 更新下一层的最远 `farthest`，$i$ 走到本层右端 `end` 时必须再跳一次：`steps += 1`，`end = farthest`。循环扫到倒数第二个就行，站在终点不用再跳。时间 $O(n)$，额外空间 $O(1)$。如果不保证可达，某层结束时 `farthest == end` 还没到终点就是失败。每个位置枚举落点做 $O(n^2)$ DP 没必要。独立卡见 `lc-45-jump-game-ii`。

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

**每跳有代价呢？**
这时候改用 DP，因为覆盖最远不一定最便宜，可能故意跳近一点，落到代价更低的格子。令 `dp[i]` 为到达 $i$ 的最小代价，初始 `dp[0]=0`、其余为无穷；从 $i$ 枚举一步能到的 $j=i+1\ldots i+$`nums[i]`，用 `dp[i] + cost[i]` 松弛 `dp[j]`。时间 $O(\sum \texttt{nums}[i])$，最坏 $O(n^2)$，额外空间 $O(n)$。代价任意、像边权一样时，也可以把「$i \to i+k$」看成边跑 Dijkstra。常见错误是继续用「每层只跳一次」的贪心，或者不可达的位置没跳过、拿无穷去更新。代价全是 $1$ 时，DP 就退回最少步数。

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

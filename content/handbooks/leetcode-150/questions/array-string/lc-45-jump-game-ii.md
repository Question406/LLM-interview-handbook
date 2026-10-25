---
id: lc-45-jump-game-ii
section: array-string
order: 10
level: A
title: LC 45 · 跳跃游戏 II
quick: "把同样跳数能到达的区间看成 BFS 的一层：`end` 记当前层的右端，`farthest` 记这一层各位置再跳一次能到的最远处，扫到 `end` 就跳数加一、进入下一层。题目保证可达，时间 $O(n)$，额外空间 $O(1)$。"
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

## 题目描述

你站在非负整数数组的下标 0。位于下标 i 时，可以向右跳到 i+j，其中步长 j 为 1 到 nums[i] 之间的整数，且落点不能超出数组。给定保证可以到达末尾的数组，求到达最后一个下标所需的最少跳跃次数。

### 输入与输出

实现 `jump(nums) -> int`。`nums[i]` 表示从位置 i 最远能向右跳多少步，返回跳跃次数；长度为 1 时已经到达终点，返回 0。

### 约束与约定

- `1 <= len(nums) <= 10000`。
- `0 <= nums[i] <= 1000`。
- 题目保证存在从下标 0 到最后一个下标的合法路线。

### 示例

```text
输入：nums = [2,3,1,1,4]
输出：2
```

示例可以从下标 0 跳到 1，再跳到 4，共两次。

[官方原题与完整题面](https://leetcode.com/problems/jump-game-ii/description/)。

## 解题思路与参考答案

## 题意

`nums[i]` 为从 $i$ 最多可跳步数，保证能到达最后一格。求到达终点的最少跳跃次数。

## 思路

我会把它当成按层的 BFS 来贪心，因为同样跳数能到的位置是一段连续区间。遍历这一层时，用 `i + nums[i]` 记下再跳一次能到的最远位置 `farthest`；扫到本层右端 `end` 时这一层处理完，跳数加一，`end` 更新为 `farthest`，开始下一层。循环只要扫到倒数第二个，站在终点不用再跳。

拿 `[2, 3, 1, 1, 4]` 走一遍：第一层只有下标 $0$，扫到它时 `farthest` 变成 $2$，跳数记 $1$、`end` 设为 $2$；扫下标 $1$ 时 `farthest` 变成 $4$，扫到下标 $2$ 碰到 `end`，跳数记 $2$、`end` 设为 $4$，已经覆盖终点，答案是 $2$。

在每个位置枚举落点做 DP 是 $O(n^2)$，没必要。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert jump([2, 3, 1, 1, 4]) == 2
assert jump([2, 3, 0, 1, 4]) == 2
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。每个下标进一层、出一层。

## 边界

$n=1$ 时已在终点，循环不进，返回 $0$ 步。每步都是 $1$ 时每层只多覆盖一格，答案是 $n-1$。第一步就能到终点时，第一次碰到 `i == end`，`farthest` 已经 $\ge n-1$，返回 $1$。

## 追问

**只问能不能到达呢？**
不用分层计数，只维护最远可达 `farthest`。扫到 $i$ 时如果 $i \gt$ `farthest`，说明中间有跨不过去的 $0$，失败；否则用 $i+$`nums[i]` 更新最远，碰到或越过终点就成功。时间 $O(n)$，额外空间 $O(1)$。本题保证可达，所以最少步数版不用写失败分支，改成「能否」后就必须写。同样别对每个位置枚举落点做成 $O(n^2)$ DP。独立卡见 `lc-55-jump-game`。

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

**要输出一条最少跳数的路径呢？**
扩展 `farthest` 时顺手记前驱。贪心分层本身就是 BFS，下标第一次被覆盖时一定来自最短路径上的某一跳，所以把新覆盖的 `(old_farthest, reach]` 全部记成 `parent[j] = i`，扫完从终点沿 `parent` 走回 $0$ 再反转。时间 $O(n)$，额外空间 $O(n)$。从终点往左找「最左能跳到当前点的 $i$」也能还原，但是 $O(n^2)$。整层共用同一个前驱是错的，层内不是每一格都能跳到层右端；$n=1$ 时 `parent[0]` 仍是 $-1$，要单独返回 `[0]`。路径下标序列的长度应该等于最少步数加一。

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

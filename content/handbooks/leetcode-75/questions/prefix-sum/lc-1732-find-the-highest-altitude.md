---
id: lc-1732-find-the-highest-altitude
section: prefix-sum
order: 1
level: A
title: LC 1732 · 找到最高海拔
quick: 海拔就是 `gain` 的前缀和，起点海拔 $0$ 也算一个点，所以一边累加一边取最大值，最大值从 $0$ 起。时间 $O(n)$，额外空间 $O(1)$。
tags:
  - Array
  - Prefix Sum
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 1732. Find the Highest Altitude
    url: 'https://leetcode.com/problems/find-the-highest-altitude/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

一次骑行依次经过 n+1 个点，起点海拔为 0。数组 gain 长度为 n，`gain[i]` 表示从第 i 个点到第 i+1 个点的净海拔变化，正数表示上升，负数表示下降。求整个行程所有点中的最高海拔，包括起点。

### 接口与输出

实现 `largestAltitude(gain: List[int]) -> int`，返回海拔值，不是到达它的位置或最大的单段上升量。

### 合法输入与约束

`1 <= len(gain) <= 100`，`-100 <= gain[i] <= 100`。即使所有后续点都低于起点，结果仍为 0。

### 示例

```text
输入：gain = [-5,1,5,0,-7]
输出：1
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/find-the-highest-altitude/description/)。

## 解题思路与参考答案

## 题意

骑行经过 $n+1$ 个点，起点海拔为 $0$。`gain[i]` 是从点 $i$ 到点 $i+1$ 的净海拔变化。返回所有点中的最高海拔。$1 \le n \le 100$，$-100 \le gain[i] \le 100$。

## 思路

点 $i$ 的海拔是 $\sum_{t \lt i} gain[t]$，也就是前缀和，所以我一边累加一边取最大就行。只看最大值时不需要真开一个前缀和数组，滚动变量就够了。用 `cur` 累加，同时维护 `best`；`best` 初始化为 $0$，因为起点本身也是一个点，全程下坡时答案就是 $0$。

拿 `[-5, 1, 5, 0, -7]` 走一遍，`cur` 依次是 -5、-4、1、1、-6，`best` 从 0 变成 1，答案 1。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert largestAltitude([-5, 1, 5, 0, -7]) == 1
assert largestAltitude([-4, -3, -2, -1, 4, 3, 2]) == 0
assert largestAltitude([5]) == 5
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## Edge Cases

全是负数时最高点是起点，返回 $0$。`best` 如果初始化成负无穷或 `gain[0]` 就错了。

最高点可能在最后一步，所以循环里每步都要比较。

中间回到 $0$ 不影响，照常累加。

## 追问

**求一段路上的最大净爬升（某点海拔减去更早某点海拔的最大值）呢？**
这是「前缀和差的最大值」。扫的同时记录见过的最小前缀和 `low`，用 `cur - low` 更新答案，等价于对 `gain` 做最大子数组和（Kadane）。时间 $O(n)$，额外空间 $O(1)$。

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

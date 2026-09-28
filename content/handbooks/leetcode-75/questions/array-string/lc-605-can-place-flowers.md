---
id: lc-605-can-place-flowers
section: array-string
order: 4
level: A
title: LC 605 · 种花问题
quick: >-
  从左到右贪心：当前为空且左右都空（越界当空）就立刻种下并计数，够 $n$ 朵提前返回。能种就种不会让后面变差。时间
  $O(m)$，额外空间 $O(1)$。
tags:
  - Array
  - Greedy
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 605. Can Place Flowers
    url: https://leetcode.com/problems/can-place-flowers/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

`flowerbed` 由 $0$（空）和 $1$（已种）组成，原数组保证没有相邻的 $1$。花不能种在相邻格子。问能否再种下 $n$ 朵花。长度 $m$ 在 $[1, 2\cdot 10^4]$，$0 \le n \le m$。

## 思路

从左往右扫，位置 $i$ 为空、左邻为空或越界、右邻为空或越界，就种下（把 `flowerbed[i]` 置 $1$）并计数。种下后下一格自动不满足条件，相当于跳过。

贪心正确性：设最优方案第一朵种在 $j$，贪心在最早可种的 $i \le j$ 种下。把最优方案里的 $j$ 换成 $i$ 仍合法，因为 $i$ 左侧没有花、右侧冲突只会更少。所以尽早种不会减少总数。

计数够 $n$ 就返回，不必扫完。我会顺带说明 $n=0$ 直接为真。

## 参考代码

```python
from typing import List


def canPlaceFlowers(flowerbed: List[int], n: int) -> bool:
    bed = flowerbed[:]
    m = len(bed)
    count = 0
    for i in range(m):
        if count >= n:
            return True
        if bed[i] == 0 and (i == 0 or bed[i - 1] == 0) and (i == m - 1 or bed[i + 1] == 0):
            bed[i] = 1
            count += 1
    return count >= n


if __name__ == "__main__":
    assert canPlaceFlowers([1, 0, 0, 0, 1], 1) is True
    assert canPlaceFlowers([1, 0, 0, 0, 1], 2) is False
    assert canPlaceFlowers([0], 1) is True
    assert canPlaceFlowers([1], 0) is True
    assert canPlaceFlowers([0, 0, 1, 0, 0], 2) is True
    assert canPlaceFlowers([0, 0], 2) is False
    assert canPlaceFlowers([0, 0, 0, 0, 0], 3) is True
    print("ok")
```

## 复杂度

时间 $O(m)$。额外空间 $O(1)$；参考代码拷了一份数组是为了不改调用方的输入，面试里可直接原地改。

## 边界

- 两端格子：越界那一侧视为空，`[0]` 能种一朵。
- $n = 0$：不管花坛如何都为真。
- 全空长度 $m$：最多种 $\lceil m/2\rceil$ 朵，隔一个种一个。

## 追问

- **不允许修改数组、也不想拷贝？** 按连续 $0$ 段算容量。两端补一个虚拟 $0$ 后，每段长度为 $z$ 的连续空位能种 $\lfloor (z-1)/2\rfloor$ 朵。扫一遍累加即可，时间 $O(m)$，额外空间 $O(1)$。

```python
def canPlaceFlowers_runs(flowerbed, n):
    total = 0
    z = 1
    for x in flowerbed:
        if x == 0:
            z += 1
        else:
            total += (z - 1) // 2
            z = 0
    total += z // 2
    return total >= n
```

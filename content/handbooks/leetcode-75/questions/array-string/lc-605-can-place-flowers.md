---
id: lc-605-can-place-flowers
section: array-string
order: 4
level: A
title: LC 605 · 种花问题
quick: >-
  从左到右贪心：当前格为空、左右也为空（越界算空）就立刻种下并计数，够 $n$ 朵提前返回。能种就种不会让后面变差。时间 $O(m)$，额外空间 $O(1)$。
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

## 题目描述

给定一排花坛 `flowerbed`，0 表示空位置，1 表示已经种有花。原花坛中保证没有相邻的花。现在还想种 n 朵新花，每个位置最多一朵，且种完后仍不能有两朵花左右相邻。判断是否能够全部种下；花坛两端不相连。

### 输入与输出

实现 `canPlaceFlowers(flowerbed, n) -> bool`。能够种下至少 n 朵新花返回 True，否则返回 False。只需返回判断，不要求给出布局或修改输入；n=0 时返回 True。

### 约束

- `1 <= len(flowerbed) <= 2 * 10^4`。
- 所有元素均为0或1，并且不存在相邻的1。
- `0 <= n <= len(flowerbed)`。

### 示例

```text
输入：flowerbed = [1,0,0,0,1], n = 1
输出：true
```

[LeetCode 原题](https://leetcode.com/problems/can-place-flowers/description/)

## 解题思路与参考答案

## 题意

`flowerbed` 由 $0$（空）和 $1$（已种）组成，原数组保证没有相邻的 $1$。花不能种在相邻格子。问能否再种下 $n$ 朵花。长度 $m$ 在 $[1, 2\cdot 10^4]$，$0 \le n \le m$。

## 思路

我会从左往右贪心，能种就种，因为尽早种不会减少能种的总数。位置 $i$ 为空、左邻为空或越界、右邻为空或越界，就种下（把 `flowerbed[i]` 置 $1$）并计数。种下后下一格自然不满足条件，相当于跳过。计数够 $n$ 就返回，不必扫完；$n=0$ 直接为真。

拿 `[1, 0, 0, 0, 1]` 走一遍：下标 1 左边有花，不能种；下标 2 左右都空，种下；下标 3 左边刚种了，不能种。总共 1 朵，所以 $n=1$ 为真，$n=2$ 为假。

贪心为什么对？设最优方案第一朵种在 $j$，贪心在最早可种的 $i \le j$ 种下。把最优方案里的 $j$ 换成 $i$ 仍然合法，因为 $i$ 左侧没有花，右侧冲突只会更少。所以尽早种不会减少总数。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert canPlaceFlowers([1, 0, 0, 0, 1], 1) is True
assert canPlaceFlowers([1, 0, 0, 0, 1], 2) is False
assert canPlaceFlowers([0], 1) is True
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(m)$。额外空间 $O(1)$；参考代码拷了一份数组，是为了不改调用方的输入，面试里可以直接原地改。

## 边界

- 两端格子越界那一侧视为空，所以 `[0]` 能种一朵。
- $n = 0$ 时，不管花坛怎样都为真。
- 长度为 $m$ 的全空花坛最多种 $\lceil m/2\rceil$ 朵，隔一个种一个。

## 追问

**不允许修改数组、也不想拷贝呢？**
按连续 $0$ 段算容量。两端补一个虚拟 $0$ 后，每段长度为 $z$ 的连续空位能种 $\lfloor (z-1)/2\rfloor$ 朵。扫一遍累加即可，时间 $O(m)$，额外空间 $O(1)$。

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

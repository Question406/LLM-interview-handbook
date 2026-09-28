---
id: lc-2300-successful-pairs-of-spells-and-potions
section: binary-search
order: 2
level: A
title: LC 2300 · 咒语和药水的成功对数
quick: >-
  药水排序后，对每个咒语 $s$ 求最小的合格强度 $\lceil success/s\rceil$，用 `bisect_left`
  找到第一个不小于它的位置，后面全部成功。时间 $O((n+m)\log m)$，额外空间 $O(m)$。
tags:
  - Binary Search
  - Sorting
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 2300. Successful Pairs of Spells and Potions
    url: https://leetcode.com/problems/successful-pairs-of-spells-and-potions/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

`spells` 长度 $n$，`potions` 长度 $m$，都是正整数。咒语 $i$ 和药水 $j$ 的乘积 `spells[i] * potions[j]` 不小于 `success` 就算一对成功。返回长度 $n$ 的数组，第 $i$ 个是咒语 $i$ 能与多少瓶药水成功配对。$n, m\le 10^5$，`success` 最大 $10^{10}$。

## 思路

对固定的咒语 $s$，成功条件 $s\cdot p\ge success$ 对 $p$ 单调：药水越强越容易成功。把 `potions` 升序排序后，合格的药水是一段后缀，只要找到后缀起点。

条件等价于 $p\ge \lceil success/s\rceil$，整数上取整写成 `(success + s - 1) // s`，然后 `bisect_left` 找第一个不小于它的下标 `i`，答案 $m-i$。用整数阈值而不是浮点除法，避免 $10^{10}$ 量级下的精度问题。

暴力两重循环是 $O(nm)$，$10^{10}$ 次，超时。

## 参考代码

```python
from bisect import bisect_left
from typing import List


def successfulPairs(spells: List[int], potions: List[int], success: int) -> List[int]:
    potions = sorted(potions)
    m = len(potions)
    ans = []
    for s in spells:
        need = (success + s - 1) // s
        ans.append(m - bisect_left(potions, need))
    return ans


if __name__ == "__main__":
    assert successfulPairs([5, 1, 3], [1, 2, 3, 4, 5], 7) == [4, 0, 3]
    assert successfulPairs([3, 1, 2], [8, 5, 8], 16) == [2, 0, 2]
    assert successfulPairs([1], [1], 1) == [1]
    assert successfulPairs([1], [1], 2) == [0]
    assert successfulPairs([10**5], [10**5], 10**10) == [1]
    assert successfulPairs([4, 4], [2, 2, 3, 3], 8) == [4, 4]
    print("ok")
```

## 复杂度

排序 $O(m\log m)$，每个咒语一次二分 $O(\log m)$，总时间 $O((n+m)\log m)$。额外空间 $O(m)$ 存排序后的副本（不计答案）。

## 边界

- 乘积恰好等于 `success`：算成功，所以用 `bisect_left` 而不是 `bisect_right`。
- 阈值大于最大药水：`bisect_left` 返回 $m$，答案 $0$。
- 阈值小于等于最小药水：返回 $0$，全部 $m$ 瓶都成功。

## 追问

- **不用二分可以吗？** 把咒语也按值排序（记住原下标），咒语从小到大时阈值单调不增，药水指针从右往左只会左移，双指针 $O(n\log n + m\log m)$，扫描部分线性。

```python
def successfulPairsTwoPointers(spells, potions, success):
    potions = sorted(potions)
    order = sorted(range(len(spells)), key=lambda i: spells[i])
    ans = [0] * len(spells)
    j = len(potions)
    for i in order:
        while j > 0 and spells[i] * potions[j - 1] >= success:
            j -= 1
        ans[i] = len(potions) - j
    return ans
```

- **为什么不直接用浮点 `success / s`？** 值到 $10^{10}$ 时浮点仍能精确表示，但除法结果可能有舍入，和整数比较时边界容易差一。整数上取整或直接比较乘积最稳。

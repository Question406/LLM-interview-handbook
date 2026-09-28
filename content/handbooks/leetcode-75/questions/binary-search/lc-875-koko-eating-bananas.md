---
id: lc-875-koko-eating-bananas
section: binary-search
order: 4
level: S
title: LC 875 · 爱吃香蕉的珂珂
quick: >-
  对速度 $k$ 二分答案，范围 $[1, \max(piles)]$。速度越快用时越少，判定「$\sum \lceil p/k\rceil \le h$」单调，找最小的可行 $k$。时间
  $O(n\log M)$，额外空间 $O(1)$。
tags:
  - Binary Search
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 875. Koko Eating Bananas
    url: https://leetcode.com/problems/koko-eating-bananas/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

`piles[i]` 是第 $i$ 堆香蕉数。珂珂每小时选一堆吃 $k$ 根，不足 $k$ 根就吃完这堆，这一小时剩下的时间也不再吃别的。警卫 $h$ 小时后回来，$h\ge n$。求能在 $h$ 小时内吃完的最小整数速度 $k$。

## 思路

速度 $k$ 下吃完第 $i$ 堆要 $\lceil p_i/k\rceil$ 小时，总时间 $T(k)=\sum_i \lceil p_i/k\rceil$ 随 $k$ 单调不增。所以「$T(k)\le h$」在 $k$ 轴上是一段后缀，二分找第一个满足的 $k$。

下界 $1$；上界 $\max(piles)$，此时每堆一小时，总共 $n\le h$，一定可行。区间写成左闭右闭找最小可行值：可行就 `hi = mid`，不可行就 `lo = mid + 1`，收敛时 `lo` 就是答案。上取整用整数写 `(p + k - 1) // k`。

从 $1$ 往上逐个试是 $O(n\cdot M)$，$M$ 可到 $10^9$，不可行。

## 参考代码

```python
from typing import List


def minEatingSpeed(piles: List[int], h: int) -> int:
    def hours(k: int) -> int:
        return sum((p + k - 1) // k for p in piles)

    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        if hours(mid) <= h:
            hi = mid
        else:
            lo = mid + 1
    return lo


if __name__ == "__main__":
    assert minEatingSpeed([3, 6, 7, 11], 8) == 4
    assert minEatingSpeed([30, 11, 23, 4, 20], 5) == 30
    assert minEatingSpeed([30, 11, 23, 4, 20], 6) == 23
    assert minEatingSpeed([1], 1) == 1
    assert minEatingSpeed([10**9], 2) == 5 * 10**8
    assert minEatingSpeed([312884470], 968709470) == 1
    for piles, h in (([3, 6, 7, 11], 8), ([2, 2], 3), ([5, 1, 9], 7)):
        k = minEatingSpeed(piles, h)
        assert sum((p + k - 1) // k for p in piles) <= h
        if k > 1:
            assert sum((p + k - 2) // (k - 1) for p in piles) > h
    print("ok")
```

## 复杂度

时间 $O(n\log M)$，$M=\max(piles)$，每次判定扫一遍数组。额外空间 $O(1)$。

## 边界

- $h=n$：每堆必须一小时吃完，答案是 $\max(piles)$。
- $h$ 远大于总数：答案 $1$，下界不能从 $0$ 开始，否则除零。
- 堆很大（$10^9$）：Python 不溢出；别的语言累加小时数要用 64 位。

## 追问

- **上界能再收紧吗？** 下界可取 $\lceil \sum p/h\rceil$，因为总量除以总时间是平均速度下限；上界 $\max(piles)$ 已经够紧。收紧只是常数优化，量级不变。
- **同类「二分答案」题？** 「在 D 天内送达包裹的能力」（LC 1011）：对载重二分，判定按顺序贪心装船，天数不超过 $D$ 即可行，下界是最重的包裹。框架和本题一样，只换判定函数。

```python
def shipWithinDays(weights, days):
    def need(cap):
        d, cur = 1, 0
        for w in weights:
            if cur + w > cap:
                d += 1
                cur = 0
            cur += w
        return d

    lo, hi = max(weights), sum(weights)
    while lo < hi:
        mid = (lo + hi) // 2
        if need(mid) <= days:
            hi = mid
        else:
            lo = mid + 1
    return lo
```

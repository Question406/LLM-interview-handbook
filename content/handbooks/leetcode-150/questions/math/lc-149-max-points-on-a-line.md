---
id: lc-149-max-points-on-a-line
section: math
order: 6
level: A
title: LC 149 · 直线上最多的点数
quick: >-
  枚举定点，其余点按斜率分组。斜率用约分后的 $(\Delta x,\Delta y)$ 做 key，`gcd`
  后统一符号。重复点单独累加，竖线 $\Delta x=0$ 也能进同一 key。
tags:
  - Math
  - Hash
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 149. 直线上最多的点数
    url: https://leetcode.cn/problems/max-points-on-a-line/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

平面整点数组，求最多有多少个点在同一条直线上。

## 思路

过定点 $i$ 的直线由斜率唯一确定。对每个 $i$，把 $j\gt i$ 的点按斜率计数，再加上 $i$ 自己。全局取最大。

斜率别用 `float`，精度会把不同直线并到一起。用分数 $(\Delta x,\Delta y)$，先 `gcd` 约分，再把符号归一（例如让 $\Delta x\gt 0$，竖线让 $\Delta y\gt 0$），同一直线落到同一 key。与 $i$ 重合的点不能当斜率，单独记 `same`，最后加到每条直线上。

点数 $\le 2$ 直接返回。我会先讲「定点 + 哈希斜率」，再写约分。

## 参考代码

```python
from math import gcd
from typing import List


def maxPoints(points: List[List[int]]) -> int:
    n = len(points)
    if n <= 2:
        return n
    ans = 1
    for i in range(n):
        cnt = {}
        same = 1
        for j in range(i + 1, n):
            dx = points[j][0] - points[i][0]
            dy = points[j][1] - points[i][1]
            if dx == 0 and dy == 0:
                same += 1
                continue
            g = gcd(dx, dy)
            dx //= g
            dy //= g
            if dx < 0 or (dx == 0 and dy < 0):
                dx, dy = -dx, -dy
            cnt[(dx, dy)] = cnt.get((dx, dy), 0) + 1
        local = same
        for v in cnt.values():
            local = max(local, same + v)
        ans = max(ans, local)
    return ans


if __name__ == "__main__":
    assert maxPoints([[1, 1], [2, 2], [3, 3]]) == 3
    assert maxPoints([[1, 1], [3, 2], [5, 3], [4, 1], [2, 3], [1, 4]]) == 4
    print("ok")
```

## 复杂度

时间 $O(n^2\log C)$（`gcd`），额外空间 $O(n)$。$C$ 为坐标差的量级。

## 边界

- 全重合：`same` 累加到 $n$，没有斜率，`local=same`。
- 全在竖线：`dx=0` 约分后 key 都是 $(0,1)$。
- 全在横线：key 都是 $(1,0)$。
- 只有 $1$ 或 $2$ 个点：直接返回 $n$。

## 追问

- **为什么不用浮点斜率？** `1/3` 与相近分数可能被当成同一直线，或同一直线因舍入拆成两条。坐标一大，`dy/dx` 精度更差。整数 `gcd` 约分后的 $(\Delta x,\Delta y)$ 是精确 key，再统一符号避免 $(-1,2)$ 与 $(1,-2)$ 各计一次。

- **三点共线判定？** 叉积 $(b_x-a_x)(c_y-a_y)-(b_y-a_y)(c_x-a_x)=0$ 则 $a,b,c$ 共线。用来验证「某个点是否在已选的两点确定的直线上」，但不能当哈希 key：同一直线上不同点对相对不同原点，叉积数值不同。分组仍用约分斜率。

```python
def collinear(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) == 0
```

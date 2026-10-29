---
id: lc-149-max-points-on-a-line
section: math
order: 6
level: A
title: LC 149 · 直线上最多的点数
quick: >-
  枚举每个点当定点，其余点按斜率分组计数。斜率用约分后的 $(\Delta x,\Delta y)$ 做 key，`gcd` 后统一符号，竖线 $\Delta
  x=0$ 也能进同一个 key；和定点重合的点单独累加。
tags:
  - Math
  - Hash
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 149. 直线上最多的点数
    url: 'https://leetcode.cn/problems/max-points-on-a-line/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定平面上若干个互不重复的点 `points`，其中 `points[i]=[x_i,y_i]`。选择任意一条直线，统计输入中落在该直线上的点，返回可以达到的最大点数。竖直线、水平线与其他方向的直线都允许。

### 输入与输出

实现 `maxPoints(points) -> int`。返回点的数量，不需要返回直线方程或对应点的下标；只有一个点时结果为 1。

### 约束

- `1 <= len(points) <= 300`。
- 每个点包含两个整数坐标，坐标均在 -10000 到 10000 之间。
- 输入点两两不同。

### 示例

```text
输入：points = [[1,1],[2,2],[3,3]]
输出：3
```

[LeetCode 原题](https://leetcode.com/problems/max-points-on-a-line/description/)

## 解题思路与参考答案

## 题意

给一组平面整点，求最多有多少个点落在同一条直线上。

## 思路

我用「定点 + 哈希斜率」。过一个定点的直线由斜率唯一确定，所以对每个点 $i$，把 $j\gt i$ 的点按斜率计数，再加上 $i$ 自己，全局取最大。

拿 `[[1, 1], [2, 2], [3, 3]]` 来说，以 (1,1) 为定点，另外两个点的差是 (1,1) 和 (2,2)，约分后都是 (1,1)，这个 key 计到 2，加上定点自己就是 3。

斜率别用 `float`，精度问题会把不同的直线并到一起。我用分数 $(\Delta x,\Delta y)$，先 `gcd` 约分，再把符号归一，比如让 $\Delta x\gt 0$，竖线让 $\Delta y\gt 0$，这样同一条直线就落到同一个 key。和 $i$ 重合的点算不出斜率，单独记在 `same` 里，最后加到每条直线上。点数 $\le 2$ 时直接返回。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert maxPoints([[1, 1], [2, 2], [3, 3]]) == 3
assert maxPoints([[1, 1], [3, 2], [5, 3], [4, 1], [2, 3], [1, 4]]) == 4
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n^2\log C)$（`gcd`），额外空间 $O(n)$。$C$ 为坐标差的量级。

## Edge Cases

- 全部重合时 `same` 累加到 $n$，没有斜率，`local=same`。
- 全在一条竖线上时，`dx=0` 约分后 key 都是 $(0,1)$。
- 全在一条横线上时，key 都是 $(1,0)$。
- 只有 $1$ 或 $2$ 个点时直接返回 $n$。

## 追问

**为什么不用浮点斜率？**
因为会算错。`1/3` 和相近的分数可能被当成同一条直线，同一条直线也可能因为舍入被拆成两条，坐标一大，`dy/dx` 的精度更差。整数 `gcd` 约分后的 $(\Delta x,\Delta y)$ 是精确的 key，再统一符号，避免 $(-1,2)$ 和 $(1,-2)$ 各计一次。

**三点共线怎么判？**
用叉积，$(b_x-a_x)(c_y-a_y)-(b_y-a_y)(c_x-a_x)=0$ 时 $a,b,c$ 共线。它适合验证某个点在不在已选两点确定的直线上，但当不了哈希 key，同一直线上的不同点对相对不同的原点，叉积数值不同。分组还是用约分斜率。

```python
def collinear(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) == 0
```

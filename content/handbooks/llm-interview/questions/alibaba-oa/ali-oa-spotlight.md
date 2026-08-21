---
id: ali-oa-spotlight
section: alibaba-oa
order: 20
level: A
title: 阿里 2022.03.14：聚光灯覆盖人数如何用二维前缀和？
quick: >-
  人先落进网格计数，矩形查询用二维前缀 $S[x_2][y_2]-S[x_1-1][y_2]-S[x_2][y_1-1]+S[x_1-1][y_1-1]$。坐标先离散。
tags:
  - Alibaba
  - OA
  - 前缀和
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-18
sources:
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
---

## 真题记录

- 公司 / 场次：阿里 2022.03.14 研发（公开回忆：聚光灯照人）
- 典型问法：平面上若干人，多次查询矩形聚光灯盖住多少人。

## 题面

（公开回忆等价转述）平面上有 $n$ 个人，第 $i$ 人在整数坐标 $(x_i,y_i)$。有 $q$ 次查询，每次给出矩形 $[x_1,x_2]\times[y_1,y_2]$（闭区间），问矩形内有多少人。

公开回忆未给出坐标范围。若坐标落在小网格里可直接开二维数组；坐标很大时先离散化。同一格子多人按人数累加，除非题面写「一人只算一次」。

输入假设：第一行 $n$，随后 $n$ 行坐标，再 $q$，随后 $q$ 行 $x_1,y_1,x_2,y_2$。输出每个查询一行。

## 思路

观察：静态矩形计数是二维前缀和的标准用法。把人落到网格计数矩阵 $c$，令

$$
S[i][j]=\sum_{a\le i}\sum_{b\le j} c[a][b]
$$

则闭矩形查询为

$$
S[x_2][y_2]-S[x_1-1][y_2]-S[x_2][y_1-1]+S[x_1-1][y_1-1]
$$

算法：收集所有人和矩形端点的 $x,y$，分别排序去重，把原坐标映射到 $1\ldots X$、$1\ldots Y$。建 $c$ 与 $S$。查询时若某端点不在离散表里，用 `bisect` 找到第一个 $\ge x_1$ 和最后一个 $\le x_2$ 的离散下标；空矩形返回 $0$。

为什么对：容斥扣掉左、下两条带后又补回左下角。离散化是严格单调映射，矩形包含关系不变。

`x1>x2` 或 `y1>y2` 时先交换。边界是闭还是开必须和题面一致：开区间把 $x_2$ 改成「最后一个 $\lt x_2$」。

## 参考代码

```python
import sys
from bisect import bisect_left, bisect_right


def discretize(vals):
    uniq = sorted(set(vals))
    return uniq


def idx_ge(uniq, v):
    return bisect_left(uniq, v) + 1


def idx_le(uniq, v):
    return bisect_right(uniq, v)


def main():
    data = list(map(int, sys.stdin.read().split()))
    t = 0
    n = data[t]
    t += 1
    pts = []
    xs, ys = [], []
    for _ in range(n):
        x, y = data[t], data[t + 1]
        t += 2
        pts.append((x, y))
        xs.append(x)
        ys.append(y)
    q = data[t]
    t += 1
    queries = []
    for _ in range(q):
        x1, y1, x2, y2 = data[t : t + 4]
        t += 4
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        queries.append((x1, y1, x2, y2))
        xs.extend([x1, x2])
        ys.extend([y1, y2])

    ux, uy = discretize(xs), discretize(ys)
    X, Y = len(ux), len(uy)
    c = [[0] * (Y + 1) for _ in range(X + 1)]
    for x, y in pts:
        c[idx_ge(ux, x)][idx_ge(uy, y)] += 1

    S = [[0] * (Y + 1) for _ in range(X + 1)]
    for i in range(1, X + 1):
        row = 0
        for j in range(1, Y + 1):
            row += c[i][j]
            S[i][j] = S[i - 1][j] + row

    out = []
    for x1, y1, x2, y2 in queries:
        li, ri = idx_ge(ux, x1), idx_le(ux, x2)
        lj, rj = idx_ge(uy, y1), idx_le(uy, y2)
        if li > ri or lj > rj:
            out.append("0")
            continue
        ans = S[ri][rj] - S[li - 1][rj] - S[ri][lj - 1] + S[li - 1][lj - 1]
        out.append(str(ans))
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
```

边界：矩形内无人输出 $0$；所有人叠在同一点要累加；退化成一条线或一个点的矩形仍按闭区间计。

## 复杂度

离散化 $O((n+q)\log(n+q))$，建表 $O(XY)$，单次查询 $O(1)$ 加两次二分。空间 $O(XY)$。若只把「人的坐标」离散、查询端点用二分定位，网格是 $n\times n$ 而不是 $(n+2q)\times(n+2q)$。

## 易错 / 面试追问

- 容斥漏加回左下角，或把开闭区间搞反。
- 重复坐标去重后人变少。
- 坐标为负时直接当数组下标。
- 追问动态加点：二维前缀和不够，改树套树 / CDQ；本题是静态查询。

---
id: ali-oa-spotlight
section: alibaba-oa
order: 20
level: A
title: 阿里 2022.03.14：聚光灯覆盖人数如何用二维前缀和？
quick: "坐标先离散化，把每个位置的人数累加进网格，再建二维前缀和，每次查询用 $S[x_2][y_2]-S[x_1-1][y_2]-S[x_2][y_1-1]+S[x_1-1][y_1-1]$ 容斥出矩形人数。同一点站了多个人，要按人数累加。"
tags:
  - Alibaba
  - OA
  - 前缀和
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
---

## 题目描述

平面上有 n 个人，每个人位于一个整数坐标。需要回答 q 个静态查询：给定一个轴对齐矩形，返回其中有多少个人。位于边界上的人也算在内；同一坐标上的多个人要分别计数。

### 输入与输出

本卡使用 `main()` 标准输入：先给 n，再给 n 行 `x y` 坐标，接着给 q，最后给 q 行 `x1 y1 x2 y2`。矩形分别由两组 x、y 端点的较小值和较大值确定，包含两端，可以退化为线或点。每个查询输出一行人数。

坐标可为负，查询期间人的位置不变。公开回忆未完整给出数量和坐标上界；上述输入格式和端点归一化是手册练习约定。

### 示例

```text
输入：
3
0 0
1 1
2 2
3
0 0 1 1
3 3 4 4
2 2 0 0

输出：
2
0
3
```

第一次查询计入 (0,0) 和 (1,1)，第三次查询覆盖三个点。

## 解题思路与参考答案

这是静态矩形计数，二维前缀和加离散化就够了：把人落到离散后的网格上累加人数，建前缀和，每次查询用容斥 $O(1)$ 算出矩形里有多少人。

## 真题记录

阿里 2022.03.14 研发的公开回忆（聚光灯照人）。典型问法是平面上有若干人，多次查询矩形聚光灯盖住多少人。

## 题面

（公开回忆等价转述）平面上有 $n$ 个人，第 $i$ 人在整数坐标 $(x_i,y_i)$。有 $q$ 次查询，每次给出矩形 $[x_1,x_2]\times[y_1,y_2]$（闭区间），问矩形内有多少人。

公开回忆没有给出坐标范围。坐标落在小网格里可以直接开二维数组；坐标很大时先离散化。同一格子有多人时按人数累加，除非题面写了「一人只算一次」。

输入假设第一行是 $n$，随后 $n$ 行坐标，再给 $q$，随后 $q$ 行 $x_1,y_1,x_2,y_2$；每个查询输出一行。

## 思路

静态矩形计数是二维前缀和的标准用法。把人落到网格计数矩阵 $c$ 上，令

$$
S[i][j]=\sum_{a\le i}\sum_{b\le j} c[a][b]
$$

闭矩形查询就是

$$
S[x_2][y_2]-S[x_1-1][y_2]-S[x_2][y_1-1]+S[x_1-1][y_1-1]
$$

容斥的意思是先扣掉左边和下边两条带，左下角被扣了两次，再补回来一次。

坐标大时先离散化：收集所有人和矩形端点的 $x,y$，各自排序去重，把原坐标映射到 $1\ldots X$、$1\ldots Y$，再建 $c$ 和 $S$。离散化是严格单调的映射，矩形的包含关系不变。查询端点不在离散表里时，用 `bisect` 找第一个 $\ge x_1$、最后一个 $\le x_2$ 的离散下标；找出来是空矩形就返回 $0$。

`x1>x2` 或 `y1>y2` 时先交换。边界是闭区间还是开区间要和题面一致，开区间就把 $x_2$ 改成「最后一个 $\lt x_2$」。

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

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。原来负责读标准输入的 `if __name__ == "__main__": main()` 入口先注释掉，只保留函数定义，由测试调用函数或模拟输入。

三个点做三次矩形查询：包含边界得到 2，空区域得到 0，反向给角点仍得到 3。 用 StringIO 模拟标准输入，redirect_stdout 捕获输出；finally 恢复 stdin，避免影响后续测试。

```python
import io
from contextlib import redirect_stdout

previous_stdin = sys.stdin
try:
    sys.stdin = io.StringIO('3\n0 0\n1 1\n2 2\n3\n0 0 1 1\n3 3 4 4\n2 2 0 0\n')
    output = io.StringIO()
    with redirect_stdout(output):
        main()
    assert output.getvalue().strip() == '2\n0\n3'
finally:
    sys.stdin = previous_stdin
print("simple tests passed")
```

## 复杂度

离散化 $O((n+q)\log(n+q))$，建表 $O(XY)$，单次查询 $O(1)$ 加两次二分，空间 $O(XY)$。如果只离散化「人的坐标」，查询端点用二分定位，网格就是 $n\times n$，不用开到 $(n+2q)\times(n+2q)$。

## 边界

矩形内无人时输出 $0$；所有人叠在同一点时要累加；退化成一条线或一个点的矩形，仍然按闭区间计。

## 追问

**容斥最容易错在哪？**
漏加回左下角，或者把开闭区间搞反。

**重复坐标能去重吗？**
坐标表可以去重，人数要累加。把重复坐标的人也去重，人数就少了。

**坐标为负怎么办？**
别直接当数组下标，离散化之后就没有这个问题。

**要动态加点呢？**
二维前缀和不够，要改成树套树或 CDQ。本题是静态查询。

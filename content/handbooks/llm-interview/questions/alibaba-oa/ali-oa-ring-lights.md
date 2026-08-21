---
id: ali-oa-ring-lights
section: alibaba-oa
order: 3
level: A
title: 淘天/阿里国际实习笔试：环形黄蓝灯最大积分怎么做？
quick: >-
  每盏灯黄 / 蓝 / 不亮，相邻颜色不能相同，灯首尾相连。拆成「首黄 / 首蓝 / 首不亮」三条线性 DP，并禁止尾灯与首灯同色。
tags:
  - Alibaba
  - OA
  - 环形DP
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-18
sources:
  - title: 淘天/阿里国际 2025 实习笔试解析
    url: http://www.jsqmd.com/news/1167387/
    type: secondary
---

## 真题记录

- 公司 / 场次：淘天 / 阿里国际 2025 实习笔试
- 原始题意：$n$ 盏灯成环，第 $i$ 盏可选黄得 $x_i$、蓝得 $y_i$、或不亮得 $0$；相邻颜色不能相同。求最大总分。
- 示例：$x=[1,4,4,50,1000]$，$y=[2,5,100,30,1]$，一种最优是黄蓝黄蓝黄，总分 $1+5+4+30+1000=1106$。

## 题面

有 $n$ 盏灯围成一圈（第 $1$ 盏与第 $n$ 盏相邻）。每盏灯有三种选择：

- 亮黄灯，得分 $x_i$
- 亮蓝灯，得分 $y_i$
- 不亮，得分 $0$

约束：任意两盏相邻灯不能亮相同颜色。不亮可以和任何选择相邻，包括另一盏也不亮。求合法方案的最大得分之和。

公开复盘未写死 $n$ 的上界；线性 $O(n)$ DP 即可。$n=1$ 时只有自己，无相邻约束，答案为 $\max(x_1,y_1,0)$。

输入：第一行 $n$，随后 $n$ 行或两行分别给出 $x_i,y_i$。输出一个整数。

## 思路

观察：这是环形约束下的三状态选择。不亮是「万能分隔」，黄只能挨着蓝或不亮，蓝只能挨着黄或不亮。

算法：先写线性转移。令 $0/1/2$ 分别表示不亮 / 黄 / 蓝，`dp[i][s]` 为考虑前 $i$ 盏、第 $i$ 盏状态为 $s$ 的最大分。

$$
\begin{aligned}
\mathrm{dp}[i][0] &= \max(\mathrm{dp}[i-1][0],\mathrm{dp}[i-1][1],\mathrm{dp}[i-1][2])\\
\mathrm{dp}[i][1] &= x_i+\max(\mathrm{dp}[i-1][0],\mathrm{dp}[i-1][2])\\
\mathrm{dp}[i][2] &= y_i+\max(\mathrm{dp}[i-1][0],\mathrm{dp}[i-1][1])
\end{aligned}
$$

环不能直接套这条链。固定第 $1$ 盏的状态，跑 $i=2\ldots n$ 的线性 DP，最后若第 $n$ 盏与第 $1$ 盏同为黄或同为蓝，则该方案非法，丢弃。三条分支取最大。

为什么对：环上唯一的额外边是 $(n,1)$。拆成「首状态固定」后，这条边变成对尾状态的过滤器；不亮与黄、蓝都兼容，所以首不亮时尾无颜色禁令。

贪心每次选 $\max(x_i,y_i)$ 会在 $[10,1],[1,10],[10,1]$ 上翻车：局部全选黄会撞色，正确做法是隔开或穿插蓝。

## 参考代码

```python
import sys

NEG = -10**30


def linear_best(x, y, first_state):
    n = len(x)
    prev = [NEG, NEG, NEG]
    if first_state == 0:
        prev[0] = 0
    elif first_state == 1:
        prev[1] = x[0]
    else:
        prev[2] = y[0]
    for i in range(1, n):
        cur = [NEG, NEG, NEG]
        cur[0] = max(prev)
        cur[1] = x[i] + max(prev[0], prev[2])
        cur[2] = y[i] + max(prev[0], prev[1])
        prev = cur
    return prev


def max_ring_score(x, y):
    n = len(x)
    if n == 0:
        return 0
    if n == 1:
        return max(0, x[0], y[0])
    ans = NEG
    for first in range(3):
        tail = linear_best(x, y, first)
        for last in range(3):
            if first in (1, 2) and last == first:
                continue
            ans = max(ans, tail[last])
    return ans


def main():
    data = list(map(int, sys.stdin.read().split()))
    n = data[0]
    x = data[1:1 + n]
    y = data[1 + n:1 + 2 * n]
    print(max_ring_score(x, y))


if __name__ == "__main__":
    main()
```

## 复杂度

时间 $O(n)$（三个首状态各扫一遍），空间滚成 $O(1)$。

## 易错 / 面试追问

- 只做线性 DP、忘记第 $n$ 盏与第 $1$ 盏同色非法。
- $n=1$ 时「首尾相同」若仍按环禁色，会错误地禁止黄/蓝，答案应允许单灯。
- 分数可能为负，初始化要用 $-inf$，不能从 $0$ 开始。
- 追问「不能连续两盏不亮」：给不亮也加相邻约束，转移改成 `dp[i][0]` 只能接黄或蓝。

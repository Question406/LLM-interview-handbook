---
id: ali-oa-ring-lights
section: alibaba-oa
order: 3
level: A
title: 淘天/阿里国际实习笔试：环形黄蓝灯最大积分怎么做？
quick: >-
  每盏灯黄 / 蓝 / 不亮，相邻不能同色，首尾相连。我会固定第一盏的状态，拆成「首黄 / 首蓝 / 首不亮」三次线性 DP，最后丢掉尾灯与首灯同色的方案，三条取最大。
tags:
  - Alibaba
  - OA
  - 环形DP
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 淘天/阿里国际 2025 实习笔试解析
    url: http://www.jsqmd.com/news/1167387/
    type: secondary
---

## 题目描述

n 盏灯围成一圈，每盏可以不亮、亮黄色或亮蓝色。第 i 盏亮黄的得分为 x[i]，亮蓝的得分为 y[i]，不亮得分为 0。要求相邻两盏已亮的灯不能同色，最大化总得分。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `max_ring_score(x, y)`。x、y 是等长整数列表，允许负分；第一个与最后一个位置相邻。本卡允许空列表。

### 输出与约束

返回最大总分，允许全部不亮。不亮可以与任意状态相邻，包括另一盏不亮。n=1 时不对灯自身施加相邻限制；n=0 返回 0。接口与这些边界为本卡重构约定。

### 示例

```text
x=[10,10], y=[8,8] -> 18
两盏分别亮黄与蓝即可。
x=[5], y=[3] -> 5
x=[-1,-2], y=[-3,-4] -> 0
```

## 解题思路与参考答案

这是环形 DP 的常规拆法：固定第一盏灯的状态（不亮 / 黄 / 蓝），各跑一遍线性 DP，最后把第 $n$ 盏和第 $1$ 盏同色的方案丢掉，三条分支取最大。每条分支都是 $O(n)$。

## 真题记录

淘天 / 阿里国际 2025 实习笔试。原始题意是 $n$ 盏灯成环，第 $i$ 盏可选黄得 $x_i$、蓝得 $y_i$、或不亮得 $0$；相邻颜色不能相同，求最大总分。示例是 $x=[1,4,4,50,1000]$，$y=[2,5,100,30,1]$，一种最优是黄蓝黄蓝黄，总分 $1+5+4+30+1000=1106$。

## 题面

有 $n$ 盏灯围成一圈（第 $1$ 盏与第 $n$ 盏相邻）。每盏灯有三种选择：

- 亮黄灯，得分 $x_i$
- 亮蓝灯，得分 $y_i$
- 不亮，得分 $0$

约束：任意两盏相邻灯不能亮相同颜色。不亮可以和任何选择相邻，包括另一盏也不亮。求合法方案的最大得分之和。

公开复盘没有写死 $n$ 的上界，线性 $O(n)$ DP 即可。$n=1$ 时只有自己，没有相邻约束，答案为 $\max(x_1,y_1,0)$。

输入第一行是 $n$，随后 $n$ 行或两行分别给出 $x_i,y_i$，输出一个整数。

## 思路

这是环形约束下的三状态选择。不亮相当于一个万能分隔：黄只能挨着蓝或不亮，蓝只能挨着黄或不亮。

先写线性转移。令 $0/1/2$ 分别表示不亮 / 黄 / 蓝，`dp[i][s]` 为考虑前 $i$ 盏、第 $i$ 盏状态为 $s$ 时的最大分：

$$
\begin{aligned}
\mathrm{dp}[i][0] &= \max(\mathrm{dp}[i-1][0],\mathrm{dp}[i-1][1],\mathrm{dp}[i-1][2])\\
\mathrm{dp}[i][1] &= x_i+\max(\mathrm{dp}[i-1][0],\mathrm{dp}[i-1][2])\\
\mathrm{dp}[i][2] &= y_i+\max(\mathrm{dp}[i-1][0],\mathrm{dp}[i-1][1])
\end{aligned}
$$

环不能直接套这条链。环上多出来的只有 $(n,1)$ 这一条边，所以固定第 $1$ 盏的状态，跑 $i=2\ldots n$ 的线性 DP，这条边就变成对尾状态的过滤：第 $n$ 盏和第 $1$ 盏同为黄或同为蓝，方案非法，丢掉。不亮和黄、蓝都兼容，所以首灯不亮时，尾灯没有颜色禁令。三条分支取最大。

每盏贪心选 $\max(x_i,y_i)$ 会翻车，比如 $[10,1],[1,10],[10,1]$ 这组，局部全选黄会撞色，正确做法是把它们隔开，或者穿插蓝。

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

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。原来负责读标准输入的 `if __name__ == "__main__": main()` 入口先注释掉，只保留函数定义，由测试调用函数或模拟输入。

单点可以选收益最大的颜色；两点环不能同时选同色，下面最优是两个不同颜色相加得到 18；全负时可以全部不点亮。

```python
assert max_ring_score([5], [3]) == 5
assert max_ring_score([10, 10], [8, 8]) == 18
assert max_ring_score([-1, -2], [-3, -4]) == 0
print("simple tests passed")
```

## 复杂度

时间 $O(n)$（三个首状态各扫一遍），空间滚动成 $O(1)$。

## 追问

**只做线性 DP 行吗？**
不行，会忘掉第 $n$ 盏与第 $1$ 盏也相邻，同色的方案必须排除。

**$n=1$ 时还要按环禁色吗？**
不要。如果首尾相同仍按环禁色，会错误地禁止黄和蓝；单灯应该允许亮。

**DP 初值能从 $0$ 开始吗？**
分数可能为负，非法状态要初始化成 $-\infty$，代码里是 `NEG`。

**如果不能连续两盏都不亮呢？**
给不亮也加相邻约束，转移改成 `dp[i][0]` 只能接黄或蓝。

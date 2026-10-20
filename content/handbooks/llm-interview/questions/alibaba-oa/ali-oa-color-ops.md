---
id: ali-oa-color-ops
section: alibaba-oa
order: 23
level: A
title: 淘天 0403：数组染色最少操作的 DP 怎么设？
quick: "先确认一次染色能做什么。如果允许把任意连续区间染成同色并覆盖旧色，可用区间 DP，合并相邻同色段后计算最少次数；若操作是全局换色或扩展同色块，状态与算法会不同。公开回忆没有完整规则，不能直接套题。"
tags:
  - Alibaba
  - OA
  - DP
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
---

## 真题记录

- 公司 / 场次：淘天笔试 0403（公开回忆：数组染色最少操作）
- 现场先确认操作定义：是「选区间染成颜色 $c$」，还是「每次扩展一个同色块」。

## 题面

公开回忆只留下「数组染色最少操作」，没有官方完整规则。下面按笔试最常见、也和卡片提示一致的区间涂色 / 奇怪打印机来写，并标明这是假设，不是官方原文。

假设：

- 初始数组为空（或全未染色）
- 一次操作选择一段连续区间，把它染成同一种颜色（可覆盖已有颜色）
- 目标是得到给定数组 / 字符串 $a$
- 求最少操作次数

这与 LeetCode 664 Strange Printer 同一模型：一次打印会写出一段连续相同字符，允许覆盖。

输入假设：第一行 $n$，第二行 $n$ 个整数颜色，或一行字符串。输出一个整数。$n$ 未公开，区间 DP 按 $O(n^3)$。

## 思路

我先把相邻相同颜色压成一个字符：连续相同段一次就能打出，压缩不改变答案。之后 $a$ 满足相邻不同。

令 `dp[l][r]` 为打出子段 $a[l\ldots r]$ 的最少次数。先花 $1$ 次打出 $a[l]$，再解决后面；若后面某个位置 $k$ 也是颜色 $a[l]$，可以在同一次涂色里「顺便」带上它，于是 $a[l+1\ldots k-1]$ 和 $a[k\ldots r]$ 拆开做：

$$
\mathrm{dp}[l][r]=\min_k \mathrm{dp}[l+1][k]+\mathrm{dp}[k][r]
\quad (a[k]=a[l],\; l\lt k\le r)
$$

更常用的等价形式：

- $\mathrm{dp}[i][i]=1$
- 若 $a[i]=a[j]$，则 $\mathrm{dp}[i][j]=\mathrm{dp}[i][j-1]$（两端同色可一次覆盖）
- 否则枚举切点 $\mathrm{dp}[i][j]=\min_k(\mathrm{dp}[i][k]+\mathrm{dp}[k+1][j])$

最优方案里，最左边那个字符对应某一次涂色区间 $[l,r']$，这次涂色的颜色是 $a[l]$，区间内部被后续覆盖的部分递归求解。区间 DP 枚举了这次数的右端。

若现场操作其实是「每次把整个数组里颜色 $x$ 改成 $y$」，那是另一题（全局字符替换），用并查集或映射表，不要套区间 DP。先举 $n\le 3$ 的例子把操作说死。

## 参考代码

```python
import sys


def min_paint(a):
    b = []
    for x in a:
        if not b or b[-1] != x:
            b.append(x)
    n = len(b)
    if n == 0:
        return 0
    dp = [[0] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = 1
    for length in range(2, n + 1):
        for i in range(0, n - length + 1):
            j = i + length - 1
            best = dp[i][j - 1] + 1
            if b[i] == b[j]:
                best = min(best, dp[i][j - 1])
            for k in range(i, j):
                best = min(best, dp[i][k] + dp[k + 1][j])
            dp[i][j] = best
    return dp[0][n - 1]


def main():
    data = sys.stdin.read().split()
    if not data:
        print(0)
        return
    if data[0].isalpha() or (len(data) == 1 and not data[0].lstrip("-").isdigit()):
        a = list(data[0])
    else:
        n = int(data[0])
        a = data[1:1 + n]
    print(min_paint(a))


if __name__ == "__main__":
    main()
```

边界：空串 $0$；单字符 $1$；已全部相同 $1$；`aba` 答案 $2$（先打三个 `a`，再覆盖中间 `b`）。

## 复杂度

时间 $O(n^3)$，空间 $O(n^2)$。压缩连续段后 $n$ 是段数。

## 易错 / 面试追问

- 没确认操作就套「戳气球 / 染色房子」，状态对不上。
- 相邻相同段不压缩，DP 仍对但常数更大，也更容易把「一次打连续段」写漏。
- 把「变成全同一颜色」理解成本题：那种只要 $1$ 次涂整段，题就没了。
- 追问「已染色不可覆盖」：转移更像「恰好用若干段拼接」，变成贪心数段数。

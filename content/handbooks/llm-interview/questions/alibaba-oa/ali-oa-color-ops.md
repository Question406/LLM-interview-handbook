---
id: ali-oa-color-ops
section: alibaba-oa
order: 23
level: A
title: 淘天 0403：数组染色最少操作的 DP 怎么设？
quick: "这题要先问清一次染色能做什么。如果允许把任意连续区间染成同色并覆盖旧色，就是奇怪打印机模型：先合并相邻同色段，再用区间 DP 算最少次数。操作如果是全局换色或扩展同色块，状态和算法都会变；公开回忆没有完整规则，直接套题有风险。"
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

## 题目描述

有一排尚未染色的位置，目标颜色从左到右由数组 a 给出。一次操作可以选择任意连续区间，把该区间全部涂为同一种颜色，允许覆盖此前的颜色。求得到目标颜色序列所需的最少操作次数。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `min_paint(a)`。a 可以是颜色标识列表，也可以是字符序列；颜色只需支持相等比较。空序列表示没有位置需要染色。

### 输出与约束

返回非负整数，空序列返回 0。一次操作使用一种颜色，允许覆盖，且不要求每个位置只被涂一次。公开回忆只披露了“数组染色”，以上覆盖式区间染色是本卡明确采用的重构规则。

### 示例

```text
a=["A","B","A"] -> 2
一种合法过程：先把三个位置都涂成 A，再把中间位置涂成 B。
a=["A","A","A"] -> 1
a=[] -> 0
```

## 解题思路与参考答案

我会先问清操作规则，再按区间涂色来做：假设一次可以把一段连续区间染成同一种颜色、允许覆盖，这就是 LeetCode 664 Strange Printer，压缩相邻同色段后做区间 DP。公开回忆只留下了题名，规则一换，算法也得换。

## 真题记录

淘天笔试 0403，公开回忆只记下「数组染色最少操作」。现场要先确认操作定义：是「选区间染成颜色 $c$」，还是「每次扩展一个同色块」。

## 题面

公开回忆只留下「数组染色最少操作」，没有官方完整规则。下面按笔试最常见、也和卡片提示一致的区间涂色 / 奇怪打印机来写，这是假设，并非官方原文。假设的规则是：

- 初始数组为空（或全未染色）
- 一次操作选择一段连续区间，把它染成同一种颜色（可覆盖已有颜色）
- 目标是得到给定数组 / 字符串 $a$
- 求最少操作次数

这和 LeetCode 664 Strange Printer 是同一个模型：一次打印写出一段连续相同字符，允许覆盖。

输入假设第一行是 $n$，第二行是 $n$ 个整数颜色，或者只有一行字符串；输出一个整数。$n$ 没有公开，区间 DP 按 $O(n^3)$ 写。

## 思路

我先把相邻相同的颜色压成一个。一段连续同色一次就能打出来，压缩不改变答案，压完之后相邻元素都不同。

令 `dp[l][r]` 为打出子段 $a[l\ldots r]$ 的最少次数。先花 $1$ 次打出 $a[l]$，再解决后面；如果后面某个位置 $k$ 也是颜色 $a[l]$，可以在同一次涂色里「顺便」带上它，于是 $a[l+1\ldots k-1]$ 和 $a[k\ldots r]$ 拆开做：

$$
\mathrm{dp}[l][r]=\min_k \mathrm{dp}[l+1][k]+\mathrm{dp}[k][r]
\quad (a[k]=a[l],\; l\lt k\le r)
$$

代码里用的是更常见的等价写法：初值 $\mathrm{dp}[i][i]=1$；如果 $a[i]=a[j]$，两端同色可以一次覆盖，$\mathrm{dp}[i][j]=\mathrm{dp}[i][j-1]$；否则枚举切点，$\mathrm{dp}[i][j]=\min_k(\mathrm{dp}[i][k]+\mathrm{dp}[k+1][j])$。

为什么这样是对的：最优方案里，最左边那个字符对应某一次涂色区间 $[l,r']$，这次涂的颜色是 $a[l]$，区间内部被后续覆盖的部分递归求解。区间 DP 枚举的就是这次涂色的右端。

如果现场的操作其实是「每次把整个数组里颜色 $x$ 改成 $y$」，那是另一题（全局字符替换），用并查集或映射表，别套区间 DP。所以开写前我会先举 $n\le 3$ 的例子，把操作说死。

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

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。原来负责读标准输入的 `if __name__ == "__main__": main()` 入口先注释掉，只保留函数定义，由测试调用函数或模拟输入。

从单色、连续同色和两端同色的短序列开始手算。ABA 可以先整段涂 A，再把中间涂 B，因此只要两次。

```python
assert min_paint(["A"]) == 1
assert min_paint(list("AAA")) == 1
assert min_paint(list("ABA")) == 2
assert min_paint(list("AB")) == 2
print("simple tests passed")
```

## 复杂度

时间 $O(n^3)$，空间 $O(n^2)$。压缩连续段之后，$n$ 是段数。

## 边界

空串是 $0$；单字符是 $1$；已经全部相同是 $1$；`aba` 答案是 $2$，先打三个 `a`，再覆盖中间的 `b`。

## 追问

**没确认操作就套「戳气球 / 染色房子」会怎样？**
状态对不上。这几题的操作定义不同，DP 状态没法直接搬过来。

**相邻相同段不压缩可以吗？**
可以，DP 仍然对，只是常数更大，也更容易把「一次打连续段」写漏。

**如果目标是把数组变成全同一颜色呢？**
那只要 $1$ 次涂整段，题就没了，所以本题的目标是给定数组。

**已染色的格子不能覆盖呢？**
转移更像「恰好用若干段拼接」，变成贪心数段数。

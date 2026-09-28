---
id: ali-oa-bin-compress
section: alibaba-oa
order: 18
level: S
title: 阿里春招 0401：二进制串定长压缩的最小代价？
quick: >-
  压缩段不能跨不同字符。我会先在每个连续段内做切分 DP，再把「减少量 → 代价」丢进外层背包，恰好减掉 $n-m$。
tags:
  - Alibaba
  - OA
  - DP
  - 背包
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阿里系列 2026.04.01 算法岗机试
    url: https://leetcode.cn/discuss/post/3943532/chun-zhao-bi-shi-a-li-xi-lie-ji-shi-fu-p-t91w/
    type: secondary
---

## 真题记录

- 公司 / 场次：阿里系列 2026.04.01 算法岗机试 T3
- 题意：同字符连续子串可压成一个特殊字符，段不重叠，压长度 $k$ 代价 $a_k$。要把总长恰好压到 $m$，求最小代价。

## 题面

给定一个长度为 $n$ 的 $01$ 串。你可以选择若干个互不重叠、且内部字符全部相同的连续块进行压缩；压缩一个长度为 $k$ 的块会把它替换成一个特殊字符，并付出成本 $\mathrm{cost}[k]$。已经压缩产生的字符不能再次参与压缩。要求最终字符串长度恰好变成 $m$，求最小总成本；不可能则输出 $-1$。

输入：$n,m$、$01$ 串，以及不同块长的成本数组。公开版本按 $n\le 1000$ 量级可过。

输出：最小成本或 $-1$。

## 思路

压缩块不能跨越不同字符，所以我先把串拆成若干 run（连续相同段）。不同 run 之间的决策独立，只通过「总共缩短多少」耦合。

一段长为 $L$ 的 run，只能在内部划分成若干块。长度为 $1$ 的块无法压缩，留下 $1$ 个原字符、代价 $0$；长度为 $k\ge 2$ 的块若压缩，留下 $1$ 个特殊字符、代价 $\mathrm{cost}[k]$。不压缩一段 $k\ge 2$ 等价于切成 $k$ 个单字符，代价 $0$、留下 $k$。因此只需枚举划分。

内层 DP：`best[j]` = 把这 $L$ 个字符划成 $j$ 块（每块压缩或单字符）的最小代价。块数 $j$ 对应本段最终长度 $j$，缩短量 $L-j$。

外层背包：`f[x]` = 所有 run 合计缩短恰好 $x$ 的最小代价。目标缩短量 $\mathrm{need}=n-m$。若 $m\gt n$ 或 $\mathrm{need}$ 超过 $\sum(L_i-1)$（每段最多压成 $1$ 个字符），无解。

特殊字符不能再压，所以不会出现跨段二次压缩。恰好缩短 $n-m$ 等价于最终长度 $m$。

## 参考代码

```python
import sys

INF = 10**18


def run_lengths(s):
    runs = []
    i, n = 0, len(s)
    while i < n:
        j = i
        while j < n and s[j] == s[i]:
            j += 1
        runs.append(j - i)
        i = j
    return runs


def costs_for_run(L, cost):
    # dp[used][cnt] rolled to 1D per used
    dp = [[INF] * (L + 1) for _ in range(L + 1)]
    dp[0][0] = 0
    for used in range(L):
        for cnt in range(used + 1):
            if dp[used][cnt] >= INF:
                continue
            for nxt in range(used + 1, L + 1):
                k = nxt - used
                add = 0 if k == 1 else cost[k]
                if add >= INF:
                    continue
                if dp[nxt][cnt + 1] > dp[used][cnt] + add:
                    dp[nxt][cnt + 1] = dp[used][cnt] + add
    options = []
    for cnt in range(1, L + 1):
        if dp[L][cnt] < INF:
            options.append((L - cnt, dp[L][cnt]))
    if L == 0:
        options.append((0, 0))
    return options


def min_compress_cost(s, m, cost):
    n = len(s)
    if m > n or m < 0:
        return -1
    need = n - m
    if need == 0:
        return 0
    f = [INF] * (need + 1)
    f[0] = 0
    for L in run_lengths(s):
        opts = costs_for_run(L, cost)
        nf = [INF] * (need + 1)
        for red, w in opts:
            for x in range(need + 1):
                if f[x] >= INF:
                    continue
                nx = x + red
                if nx <= need and nf[nx] > f[x] + w:
                    nf[nx] = f[x] + w
        f = nf
    return -1 if f[need] >= INF else f[need]


def main():
    data = sys.stdin.read().split()
    n, m = int(data[0]), int(data[1])
    s = data[2]
    # cost[k] for k=1..n；cost[1] 不会用到，缺省 0
    raw = list(map(int, data[3:]))
    cost = [0] * (n + 1)
    if len(raw) == n:
        for k in range(1, n + 1):
            cost[k] = raw[k - 1]
    elif len(raw) == n - 1:
        for k in range(2, n + 1):
            cost[k] = raw[k - 2]
    else:
        for i, v in enumerate(raw, start=1):
            if i <= n:
                cost[i] = v
    print(min_compress_cost(s, m, cost))


if __name__ == "__main__":
    main()
```

边界：`need=0` 直接 $0$；单字符 run 只能缩短 $0$；某段 $L=1$ 的 option 只有 $(0,0)$。成本数组按「$n$ 个数对应长度 $1\ldots n$」或「$n-1$ 个数对应 $2\ldots n$」两种读法兼容。

## 复杂度

每个 run 内层 $O(L^3)$，各段 $L$ 之和为 $n$，最坏 $O(n^3)$；外层背包 $O(\#\mathrm{runs}\cdot n\cdot n)$。公开口径 $n\le 1000$ 可过。空间 $O(n^2)$。

## 易错 / 面试追问

- 允许压缩块跨过 $0/1$ 交界，得到非法块。
- 压缩后再把特殊字符和新邻居接着压，题目禁止。
- 背包写成「至少缩短 $n-m$」而不是恰好；最终长度会短于 $m$。
- 追问「块长 $k$ 必须 $\ge 2$」：长度为 $1$ 的代价应视为 $0$ 且不能压，不要去读 `cost[1]` 当惩罚。

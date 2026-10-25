---
id: ali-oa-bin-compress
section: alibaba-oa
order: 18
level: S
title: 阿里春招 0401：二进制串定长压缩的最小代价？
quick: >-
  压缩块不能跨过不同字符，所以我先按连续段拆开，每段内部做切分 DP，算出「缩短多少 → 最小代价」，再把各段的选项放进外层背包，凑出恰好缩短 $n-m$。
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

## 题目描述

给定一个二进制字符串，选择互不重叠、内部字符全部相同的连续块进行压缩，使最终长度恰好等于目标长度，并使总成本最小。长度 k 的块会变成一个特殊字符，产生的特殊字符不能再次参与压缩。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `min_compress_cost(s, m, cost)`。s 只含 `0` 与 `1`；m 为目标长度；cost 是按块长索引的非负成本列表，`cost[k]` 是压缩 k 个同字符的成本。`cost[0]` 为占位，长度为 1 的字符可以原样保留且不付费。

### 输出与约束

返回最小总成本；若不能达到目标长度则返回 -1。不允许压缩包含不同原始字符的块，也不允许把已经生成的特殊字符作为下一轮原料。公开复盘没有统一的完整范围，本卡不补造官方上界。

### 示例

```text
s="00", m=1, cost=[0,0,5] -> 5
s="00", m=2, cost=[0,0,5] -> 0
s="01", m=1, cost=[0,0,5] -> -1
```

## 解题思路与参考答案

这题我会拆成两层 DP。压缩块只能落在同一个连续段（run）里，所以先在每段内部算「缩短多少要花多少」，再用外层背包把各段拼起来，要求总缩短量恰好是 $n-m$。

## 真题记录

阿里系列 2026.04.01 算法岗机试第 3 题。题意是同字符连续子串可以压成一个特殊字符，段之间不重叠，压长度为 $k$ 的段代价 $a_k$，要把总长恰好压到 $m$，求最小代价。

## 题面

给定一个长度为 $n$ 的 $01$ 串。你可以选择若干个互不重叠、且内部字符全部相同的连续块进行压缩；压缩一个长度为 $k$ 的块会把它替换成一个特殊字符，并付出成本 $\mathrm{cost}[k]$。已经压缩产生的字符不能再次参与压缩。要求最终字符串长度恰好变成 $m$，求最小总成本；不可能则输出 $-1$。

输入是 $n,m$、$01$ 串，以及不同块长的成本数组，公开版本按 $n\le 1000$ 量级可过。输出最小成本，或者 $-1$。

## 思路

压缩块不能跨过不同字符，我就先把串拆成若干 run。不同 run 之间的决策互相独立，唯一的联系是「总共缩短了多少」。比如 `0001100` 拆成长度 $3,2,2$ 的三段，每段自己决定怎么压，最后三段的缩短量加起来对上 $n-m$ 就行。

一段长为 $L$ 的 run，能做的就是在内部切成若干块。长度为 $1$ 的块压不了，留下 $1$ 个原字符、代价 $0$；长度 $k\ge 2$ 的块压缩后留下 $1$ 个特殊字符、代价 $\mathrm{cost}[k]$。一段 $k\ge 2$ 的块如果不压，就等于切成 $k$ 个单字符，代价 $0$、留下 $k$ 个。所以只要枚举划分就够了。

内层 DP 用 `best[j]` 表示把这 $L$ 个字符划成 $j$ 块（每块要么压缩、要么是单字符）的最小代价。块数 $j$ 就是这段最终的长度，缩短量是 $L-j$。

外层背包用 `f[x]` 表示所有 run 合计缩短恰好 $x$ 的最小代价，目标缩短量是 $\mathrm{need}=n-m$。如果 $m\gt n$，或者 $\mathrm{need}$ 超过 $\sum(L_i-1)$（每段最多压成 $1$ 个字符），就无解。

特殊字符不能再压，所以不会出现跨段的二次压缩；恰好缩短 $n-m$ 也就等价于最终长度是 $m$。

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

成本数组有两种读法，代码都兼容：「$n$ 个数对应长度 $1\ldots n$」，或者「$n-1$ 个数对应 $2\ldots n$」。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。原来负责读标准输入的 `if __name__ == "__main__": main()` 入口先注释掉，只保留函数定义，由测试调用函数或模拟输入。

取 cost[2]=5：00 压成一位花 5；目标长度不变花 0；01 没有同字符段可压成一位，应返回 -1。

```python
cost = [0, 0, 5]
assert min_compress_cost("00", 1, cost) == 5
assert min_compress_cost("00", 2, cost) == 0
assert min_compress_cost("01", 1, cost) == -1
print("simple tests passed")
```

## 复杂度

每个 run 的内层是 $O(L^3)$，各段 $L$ 之和为 $n$，最坏 $O(n^3)$；外层背包是 $O(\#\mathrm{runs}\cdot n\cdot n)$。公开口径 $n\le 1000$ 可过，空间 $O(n^2)$。

## 边界

`need=0` 直接返回 $0$。单字符的 run 只能缩短 $0$，$L=1$ 时选项只有 $(0,0)$。

## 追问

**压缩块能跨过 $0/1$ 交界吗？**
不能。跨过去的块内部字符不同，是非法块，所以第一步就按 run 拆开。

**压完的特殊字符能和新邻居接着压吗？**
题目禁止。特殊字符不再参与压缩，这也是各段可以独立计算的前提。

**背包写成「至少缩短 $n-m$」行不行？**
不行，那样最终长度可能短于 $m$。状态要按恰好缩短 $x$ 来定义。

**块长 $k$ 必须 $\ge 2$，`cost[1]` 怎么处理？**
长度为 $1$ 的块代价视为 $0$，而且不能压，别把 `cost[1]` 读进来当惩罚。

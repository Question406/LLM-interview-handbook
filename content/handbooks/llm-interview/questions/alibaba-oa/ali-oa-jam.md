---
id: ali-oa-jam
section: alibaba-oa
order: 15
level: S
title: 淘天研发 0411：果酱平衡为什么是分组 DP + 前缀差值？
quick: >-
  每行只能删一个前缀，删完后各行剩余和要尽量平衡。我会先把每行前缀和变成可选差值，再在分组 / 背包 DP 上拼最优。
tags:
  - Alibaba
  - OA
  - 分组DP
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 淘天研发 2026.04.11 改编真题
    url: https://www.nowcoder.com/discuss/872969146470887424
    type: secondary
---

## 真题记录

- 公司 / 场次：淘天研发 / AI 研发 2026.04.11 T3
- 公开完整题面： $n\times m$ 字符网格，格子为 `B` 或 `S`。每一行可以独立删除一个前缀（长度 $0\ldots m$）。删除后，所有剩余格子中 `B` 的数量等于 `S` 的数量。求最少删除多少个格子；无解按约定输出。

## 题面

给定 $n$ 行 $m$ 列的字符网格，每个格子是 `B` 或 `S`。对每一行可以独立删除一个前缀，长度可以是 $0$（不删）到 $m$（整行删光）。删除发生后，把所有行剩下的格子放在一起，要求 `B` 的个数等于 `S` 的个数。求最少需要删除的格子数。

输入：$n,m$ 和 $n$ 行字符串。公开版本未写死 $n,m$ 上界，也未写无解输出；下面无解输出 $-1$，并按分组背包 $O(n^2 m^2)$ 实现。若现场 $n,m\le 80$ 量级可通过。

输出：最少删除量，或 $-1$。

## 思路

把 `B` 映射成 $+1$，`S` 映射成 $-1$。剩余格子里两种字母数量相等，当且仅当剩余映射值之和为 $0$。（空网格 $0=0$，合法。）

第 $i$ 行若删除长度为 $j$ 的前缀，则

- 代价 $j$（删掉 $j$ 个格子）
- 贡献 $\delta_{i,j}=$ 该行后缀 $s_i[j\ldots m)$ 的映射和

每行必须选恰好一个 $j\in[0,m]$。问题变成分组背包：第 $i$ 组有 $m+1$ 个物品，每组必选一个，使总 $\delta=0$，总代价最小。

算法：`dp[i][off]` 表示前 $i$ 行、当前映射和为 `off - SHIFT` 的最小删除量，其中 `SHIFT = n\cdot m`，因为总和落在 $[-nm,nm]$。转移枚举该行的 $m+1$ 个切点。也可用滚动数组只留一层。

这样写是对的：行与行独立，唯一耦合是总和为 $0$。前缀删除限制已经被压进「每行 $m+1$ 个可选差值」，没有漏掉「只能删前缀、不能删后缀或中间」。

整行删光贡献 $\delta=0$、代价 $m$，相当于扔掉这一行；这是允许的。

## 参考代码

```python
import sys

INF = 10**18


def min_deletions(grid):
    if not grid:
        return 0
    n = len(grid)
    m = len(grid[0])
    rows = []
    for s in grid:
        mapped = [1 if ch == "B" else -1 for ch in s]
        suf = [0] * (m + 1)
        acc = 0
        for j in range(m - 1, -1, -1):
            acc += mapped[j]
            suf[j] = acc
        # suf[j] = sum of suffix starting at j; suf[m] = 0
        rows.append([(j, suf[j]) for j in range(m + 1)])

    shift = n * m
    width = 2 * shift + 1
    dp = [INF] * width
    dp[shift] = 0
    for options in rows:
        ndp = [INF] * width
        for off in range(width):
            if dp[off] >= INF:
                continue
            for cost, delta in options:
                noff = off + delta
                if 0 <= noff < width:
                    val = dp[off] + cost
                    if val < ndp[noff]:
                        ndp[noff] = val
        dp = ndp
    ans = dp[shift]
    return -1 if ans >= INF else ans


def main():
    data = sys.stdin.read().split()
    n, m = int(data[0]), int(data[1])
    grid = data[2:2 + n]
    print(min_deletions(grid))


if __name__ == "__main__":
    main()
```

边界：全删光合法，答案至多 $nm$；已经平衡且不必删时答案 $0$；只有 `B` 且 $nm$ 为奇数，即使删到只剩偶数个 `B` 也可能无法配平。DP 会自然得到 $-1$。

## 复杂度

状态 $O(n\cdot nm)$，每层转移 $O(nm\cdot m)$，总时间 $O(n^2 m^2)$，空间 $O(nm)$。若现场 $n=2$、$m$ 很大，可改成对两行枚举切点 $O(m^2)$。

## 易错 / 面试追问

- 理解成每行可删任意子串或每列也可删，模型就不是分组背包。
- 用剩余 `B` 个数做维度却忘记 `S` 也在变；差值 $\delta=B-S$ 一个维度就够。
- 无解输出 $0$ 或 $nm$ 而不写 $-1$；公开题面只说「按约定」，答卷前看清。
- 追问「每行至多删一个前缀」已经包含长度 $0$；不要再强制每行必须删。

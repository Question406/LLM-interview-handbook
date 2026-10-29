---
id: ali-oa-jam
section: alibaba-oa
order: 15
level: S
title: 淘天研发 0411：果酱平衡为什么是分组 DP + 前缀差值？
quick: >-
  每行能删一个前缀，目标是剩下的格子里 B 和 S 一样多。把 B 记为 +1、S 记为
  -1，每行枚举切点得到「剩余差值、删除代价」，再用分组背包每行选一个方案，让总差值为 0、总代价最小。
tags:
  - Alibaba
  - OA
  - 分组DP
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 淘天研发 2026.04.11 改编真题
    url: 'https://www.nowcoder.com/discuss/872969146470887424'
    type: secondary
---

## 题目描述

有一个等宽字符网格。对每一行可以独立删除一个前缀，包括不删或把整行删光；其余字符保持原顺序。希望删除后所有行剩余的两类字符数量相等，求至少需要删除多少个格子。

### 接口与练习约定

实现 `min_deletions(grid) -> int`，`grid` 是 n 个长度为 m 的字符串。公开题面把两类字符写作 `B` 和 `S`；为与本卡可运行示例统一，练习使用 `B` 和 `W`，二者只代表两种类别，计数语义相同。输入均为这两类字符。

返回最少删除量，不要求返回各行删除的前缀。允许把所有行删空，因此合法输入总能达到两类数量相等。标准输入先给 `n m`，再给 n 行字符，输出最少删除数。

### 示例

```text
min_deletions(["BW"])  -> 0
min_deletions(["BB"])  -> 2
min_deletions(["WBW"]) -> 1
```

第三个例子删除该行最左边的 W 后剩下 BW，两类各一个。公开材料没有完整给出 n、m 上界，此处不伪造原题范围。

## 解题思路与参考答案

这题是分组背包。把 `B` 记 $+1$、`S` 记 $-1$，剩下的格子平衡就等于剩余和为 $0$；每行删多长的前缀是一组选项，每组必须选一个，求总和为 $0$ 时的最小删除量。

## 真题记录

淘天研发 / AI 研发 2026.04.11 第 3 题，有公开完整题面：$n\times m$ 字符网格，格子为 `B` 或 `S`，每一行可以独立删除一个前缀（长度 $0\ldots m$），删除后所有剩余格子中 `B` 的数量等于 `S` 的数量，求最少删除多少个格子，无解按约定输出。

## 题面

给定 $n$ 行 $m$ 列的字符网格，每个格子是 `B` 或 `S`。对每一行可以独立删除一个前缀，长度可以是 $0$（不删）到 $m$（整行删光）。删除发生后，把所有行剩下的格子放在一起，要求 `B` 的个数等于 `S` 的个数。求最少需要删除的格子数。

输入是 $n,m$ 和 $n$ 行字符串。公开版本没有写死 $n,m$ 的上界，也没写无解时输出什么；下面无解输出 $-1$，按分组背包 $O(n^2 m^2)$ 实现。输出最少删除量，或者 $-1$。

## 思路

把 `B` 映射成 $+1$，`S` 映射成 $-1$。剩下的格子里两种字母一样多，当且仅当剩余映射值之和为 $0$。整个网格删空时是 $0=0$，也合法。

第 $i$ 行如果删掉长度为 $j$ 的前缀，代价就是 $j$，贡献是这一行后缀 $s_i[j\ldots m)$ 的映射和，记为 $\delta_{i,j}$。比如一行是 `BBS`，不删贡献 $+1$，删一个贡献 $0$，删两个贡献 $-1$，删光贡献 $0$、代价 $3$。

每行必须恰好选一个 $j\in[0,m]$，于是第 $i$ 组有 $m+1$ 个物品，每组必选一个，要求总 $\delta=0$、总代价最小，这就是分组背包。

状态用 `dp[i][off]`，表示前 $i$ 行、当前映射和为 `off - SHIFT` 时的最小删除量。总和落在 $[-nm,nm]$，所以 `SHIFT = n\cdot m`。转移时枚举这一行的 $m+1$ 个切点，也可以用滚动数组只留一层。

行与行之间唯一的耦合就是总和为 $0$。「只能删前缀」这个限制已经压进了每行 $m+1$ 个可选差值里，模型里没有删后缀或删中间的选项。整行删光贡献 $\delta=0$、代价 $m$，相当于扔掉这一行，这是允许的。

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
    grid = data[2 : 2 + n]
    print(min_deletions(grid))


if __name__ == "__main__":
    main()
```

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。原来负责读标准输入的 `if __name__ == "__main__": main()` 入口先注释掉，只保留函数定义，由测试调用函数或模拟输入。

单行 BW 已平衡，不删；BB 只能整行删掉；WBW 去掉第一个 W 就平衡。这样可以检查零代价和前缀删除方向。

```python
assert min_deletions(["BW"]) == 0
assert min_deletions(["BB"]) == 2
assert min_deletions(["WBW"]) == 1
print("simple tests passed")
```

## 复杂度

状态 $O(n\cdot nm)$，每层转移 $O(nm\cdot m)$，总时间 $O(n^2 m^2)$，空间 $O(nm)$。现场如果是 $n,m\le 80$ 量级，可以通过。如果现场 $n=2$、$m$ 很大，可以改成对两行枚举切点，$O(m^2)$。

## Edge Cases

全删光是合法的，所以答案至多 $nm$；已经平衡、不必删时答案是 $0$。只有 `B` 且 $nm$ 为奇数时，即使删到只剩偶数个 `B` 也可能无法配平，DP 会自然得到 $-1$。

## 追问

**如果每行能删任意子串，或者也能按列删呢？**
那模型就不是分组背包了。本题只允许每行删一个前缀。

**要不要分别记剩余 `B` 和 `S` 的个数？**
不用。只拿剩余 `B` 个数做维度，会忘了 `S` 也在变；差值 $\delta=B-S$ 一个维度就够。

**无解输出什么？**
公开题面只说「按约定」，这里输出 $-1$。答卷前看清题面，别随手写成 $0$ 或 $nm$。

**每行都必须删吗？**
不用。「每行至多删一个前缀」已经包含长度 $0$，别再强制每行必须删。

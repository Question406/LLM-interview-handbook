---
id: ali-oa-perm-subseq
section: alibaba-oa
order: 24
level: A
title: 淘天 0515：有多少子序列本身是一个排列？
quick: >-
  子序列要恰好包含 $1\ldots k$ 各一次（或题面指定的值域）。用计数 DP：已出现的集合，或「当前必须接到的下一个数」。
tags:
  - Alibaba
  - OA
  - 计数DP
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

- 公司 / 场次：淘天笔试 0515（公开回忆）
- 典型问法：数组是 $1\ldots n$ 的重排或含重复，数有多少子序列是某个 $1\ldots k$ 的排列。

## 题面

公开回忆没有完整输入格式。下面按「子序列的值集合恰好是 $\{1,2,\ldots,k\}$ 且每个值出现一次」来写，即该子序列本身是 $1\ldots k$ 的一个排列。空序列不算（不把 $k=0$ 算进去）。答案对 $10^9+7$ 取模。

给定长度为 $n$ 的正整数数组 $a$。统计有多少个非空子序列，存在整数 $k\ge 1$，使得子序列里 $1,2,\ldots,k$ 各出现恰好一次，且不含其他值。

输入假设：第一行 $n$，第二行 $a_1\ldots a_n$。输出一个整数。模数、空序列是否算「$0$ 号排列」，读题时先定；这里空序列不算。

## 思路

观察：对固定的 $k$，合法子序列就是：从 $a$ 里为每个 $v\in[1,k]$ 选一个出现位置，且不选任何 $k$ 以外的数。由于子序列只要保持相对顺序，选定位置集合后只有一种子序列。因此方案数是

$$
\prod_{v=1}^{k} \mathrm{cnt}(v)
$$

其中 $\mathrm{cnt}(v)$ 是 $v$ 在 $a$ 中的出现次数。若某个 $v\le k$ 一次都没出现，该 $k$ 贡献 $0$，更大的 $k$ 也是 $0$。

算法：扫 $k=1,2,\ldots$，维护前缀乘积，累加。遇到 $\mathrm{cnt}(k)=0$ 停止。

为什么对：排列只约束「出现哪些值、各一次」，不约束它们在子序列里的相对次序——次序由原数组位置决定。这和「必须按 $1,2,3,\ldots$ 的顺序选出」不是同一题。

若题面改成必须递增选出 $1$ 然后 $2$ 然后 $\ldots$，改用扫描 DP：遇到 $1$ 则 `dp[1]+=1`，遇到 $v\gt 1$ 则 `dp[v]+=dp[v-1]`，答案是所有 `dp[k]` 之和。值域小还可用 `dp[mask]` 表示已选集合。

## 参考代码

```python
import sys
from collections import Counter

MOD = 10**9 + 7


def count_perm_subseq(a):
    cnt = Counter(a)
    ans = 0
    prod = 1
    k = 1
    while cnt[k] > 0:
        prod = prod * cnt[k] % MOD
        ans = (ans + prod) % MOD
        k += 1
    return ans


def count_increasing_build(a):
    """若必须按 1,2,... 的顺序依次选入子序列。"""
    if not a:
        return 0
    m = max(a)
    dp = [0] * (m + 2)
    for v in a:
        if v == 1:
            dp[1] = (dp[1] + 1) % MOD
        elif v > 1:
            dp[v] = (dp[v] + dp[v - 1]) % MOD
    return sum(dp[1:]) % MOD


def main():
    data = list(map(int, sys.stdin.read().split()))
    n = data[0]
    a = data[1:1 + n]
    print(count_perm_subseq(a))


if __name__ == "__main__":
    main()
```

边界：$a=[1,2,1]$ 时 $k=1$ 有 $2$ 个单点子序列（两个位置上的 $1$），$k=2$ 有 $2\times 1=2$ 个（两个 $1$ 各自配上那个 $2$），答案 $4$。缺 $1$ 时答案 $0$。数组是 $1\ldots n$ 排列时答案是 $n$（每个前缀集合各一条，因为每个值恰好一次）。

## 复杂度

统计频次 $O(n)$，再扫 $k$ 至多到 $n$ 或 $\max a$。空间 $O(n)$。递增 DP 同样 $O(n)$。

## 易错 / 面试追问

- 把「是一个排列」理解成「去重后随便什么集合」，漏掉必须从 $1$ 连续到 $k$。
- $n$ 大时对下标子集做 $2^n$ 枚举。
- 模数、空序列是否算 $0$ 号排列没问清就开写。
- 追问值域很小、但要求子序列顺序也是指定排列 $p$：按 $p$ 的名次做同样的前缀乘积 / 扫描 DP。

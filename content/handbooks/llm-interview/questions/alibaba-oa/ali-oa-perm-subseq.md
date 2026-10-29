---
id: ali-oa-perm-subseq
section: alibaba-oa
order: 24
level: A
title: 淘天 0515：有多少子序列本身是一个排列？
quick: >-
  子序列要恰好包含 $1\ldots k$ 各一次。不限制这些值的先后顺序时，统计每个值的出现次数，固定 $k$ 的方案数就是频次乘积，再对所有 $k$
  累加；要求按递增顺序选取时，改用计数 DP。
tags:
  - Alibaba
  - OA
  - 计数DP
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 2026 校招高频题总览
    url: 'https://www.cnblogs.com/autodriver/p/19829365'
    type: secondary
---

## 题目描述

给定正整数数组，统计所有非空子序列中，哪些恰好包含从 1 到某个 k 的每个数各一次，且没有其他值。不同下标选择计为不同子序列，即使得到的数值序列相同。

下面的函数接口、input representation 和 edge-case behavior 是本卡采用的练习约定；补充题干由本手册编写。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `count_perm_subseq(a)`，返回本题主版本计数。a 为正整数列表，子序列由递增下标选择得到但不要求数值递增。本卡另提供 `count_increasing_build(a)`，其额外条件是选出值必须依次为 1、2、…、k。

### 输出与约束

两个版本都对 1000000007 取模，不计空子序列。主版本中的“排列”只限制值集合和各值出现一次，不限制值的相对大小顺序。题面中未公开的模数和空序列定义在本卡按以上约定统一。

### 示例

```text
a=[1,2,1]：主版本输出 4（两个单独的1，以及两种包含1和2的下标选择）
a=[2,1]：count_perm_subseq -> 2；count_increasing_build -> 1
a=[2,3]：两个版本均输出 0
```

## 解题思路与参考答案

固定 $k$ 时，答案是 $\mathrm{cnt}(1)\cdot\mathrm{cnt}(2)\cdots\mathrm{cnt}(k)$：每个值从它的出现位置里挑一个，位置定了，子序列也就定了。所以我统计频次，从 $k=1$ 往上维护前缀乘积并累加，碰到某个值没出现就停。

## 真题记录

淘天笔试 0515 的公开回忆。典型问法是：数组是 $1\ldots n$ 的重排或含重复，数有多少子序列是某个 $1\ldots k$ 的排列。

## 题面

公开回忆没有完整输入格式。下面按「子序列的值集合恰好是 $\{1,2,\ldots,k\}$ 且每个值出现一次」来写，即该子序列本身是 $1\ldots k$ 的一个排列。空序列不算（不把 $k=0$ 算进去）。答案对 $10^9+7$ 取模。

给定长度为 $n$ 的正整数数组 $a$。统计有多少个非空子序列，存在整数 $k\ge 1$，使得子序列里 $1,2,\ldots,k$ 各出现恰好一次，且不含其他值。

输入假设第一行是 $n$，第二行是 $a_1\ldots a_n$，输出一个整数。模数、空序列算不算「$0$ 号排列」，读题时要先定下来；这里空序列不算。

## 思路

对固定的 $k$，合法子序列就是：为每个 $v\in[1,k]$ 从 $a$ 里选一个出现位置，并且不选任何 $k$ 以外的数。子序列只需要保持原来的相对顺序，位置集合选定后只对应一个子序列，所以方案数是

$$
\prod_{v=1}^{k} \mathrm{cnt}(v)
$$

其中 $\mathrm{cnt}(v)$ 是 $v$ 在 $a$ 中的出现次数。如果某个 $v\le k$ 一次都没出现，这个 $k$ 贡献 $0$，更大的 $k$ 也都是 $0$。

拿 $a=[1,2,1]$ 看：$k=1$ 有 $2$ 个单点子序列，就是两个位置上的 $1$；$k=2$ 有 $2\times 1=2$ 个，两个 $1$ 各自配上那个 $2$；答案是 $4$。

所以做法就是扫 $k=1,2,\ldots$，维护前缀乘积并累加，遇到 $\mathrm{cnt}(k)=0$ 就停。

「是一个排列」只约束出现哪些值、各出现一次，不约束子序列里的相对次序，次序由原数组位置决定。如果题面改成必须依次选出 $1$、然后 $2$、然后 $\ldots$，那是另一题，改用扫描 DP：遇到 $1$ 则 `dp[1]+=1`，遇到 $v\gt 1$ 则 `dp[v]+=dp[v-1]`，答案是所有 `dp[k]` 之和。值域小时还可以用 `dp[mask]` 表示已选集合。代码里的 `count_increasing_build` 就是这个版本。

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
    a = data[1 : 1 + n]
    print(count_perm_subseq(a))


if __name__ == "__main__":
    main()
```

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。原来负责读标准输入的 `if __name__ == "__main__": main()` 入口先注释掉，只保留函数定义，由测试调用函数或模拟输入。

把两种题意并排测：无序选取时 [2,1] 有 {1} 和 {1,2} 两种，要求按 1、2 顺序时只有一种。重复的 1 产生不同下标选择。

```python
assert count_perm_subseq([2, 1]) == 2
assert count_increasing_build([2, 1]) == 1
assert count_perm_subseq([1, 1, 2]) == 4
assert count_perm_subseq([2, 3]) == 0
print("simple tests passed")
```

## 复杂度

统计频次 $O(n)$，再扫 $k$，至多到 $n$ 或 $\max a$。空间 $O(n)$。递增 DP 同样是 $O(n)$。

## Edge Cases

缺 $1$ 时答案为 $0$。数组是 $1\ldots n$ 的排列时答案是 $n$，因为每个值恰好出现一次，每个前缀集合各对应一条。

## 追问

**「是一个排列」能理解成去重后的任意集合吗？**
不能，值必须从 $1$ 连续到 $k$。

**$n$ 大时能枚举下标子集吗？**
$2^n$ 枚举肯定不行，按值的频次算就够了。

**开写前要问清什么？**
模数，以及空序列算不算 $0$ 号排列。这两点没问清就开写，答案定义可能对不上。

**如果值域很小，但要求子序列的顺序也是某个指定排列 $p$ 呢？**
按 $p$ 的名次做同样的前缀乘积 / 扫描 DP。

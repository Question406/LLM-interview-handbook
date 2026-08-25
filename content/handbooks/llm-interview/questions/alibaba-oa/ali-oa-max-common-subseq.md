---
id: ali-oa-max-common-subseq
section: alibaba-oa
order: 5
level: A
title: 阿里 AI 研发 0325：两排列的字典序最大公共子序列怎么贪？
quick: >-
  从大到小枚举值 $n\ldots 1$，若它在两个排列里都还在已选位置之后，就选。大的先拿走一定不亏，但本题要先保证最长。
tags:
  - Alibaba
  - OA
  - 贪心
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阿里 0325 AI 研发笔试复盘
    url: https://www.nowcoder.com/discuss/866741961221292032
    type: candidate-first-hand
---

## 真题记录

- 公司 / 场次：阿里 AI 研发 2026.03.25 · 研发 Q2
- 原始题意：两个长度为 $n$ 的排列，在所有公共子序列中先取最长，再在最长里取字典序最大的一条。

## 题面

给定两个长度均为 $n$ 的排列 $p$、$q$（都恰好包含 $1\ldots n$）。在它们的所有公共子序列中，首先要求长度最大；若有多个最长公共子序列，则输出其中**字典序最大**的一个。

输入：第一行 $n$，随后两行排列 $p$、$q$。公开复盘未写死 $n$ 上界。

输出：一行，满足要求的公共子序列（若干个整数）。

## 思路

因为 $p,q$ 都是排列，公共子序列就是一组互异的值 $v_1,v_2,\ldots$，它们在 $p$ 中的下标递增，同时在 $q$ 中的下标也递增。这是值域上的一条 DAG 链。

只追求字典序、不管长度时，从大到小扫一遍即可：能接在已选位置后面就拿走。但这条贪心可能更短。例如 $p=q=[1,3,2]$，从大到小会得到 $[3,2]$，而最长公共子序列是 $[1,3,2]$。公开题面明确要求**先最长、再字典序**，所以必须带长度信息。

算法：

1. 记下每个值在两个排列中的位置 `pos_p[v]`、`pos_q[v]`。
2. 令 $L(v)$ 为「以 $v$ 开头的最长公共子序列长度」：

$$
L(v)=1+\max\bigl\{L(w): \mathrm{pos}_p[w]\gt \mathrm{pos}_p[v],\ \mathrm{pos}_q[w]\gt \mathrm{pos}_q[v]\bigr\}
$$

没有后继时 $L(v)=1$。直接 $O(n^2)$ 从后往前算。

3. 设 $M=\max_v L(v)$。从 $n$ 扫到 $1$，维护已选在 $p,q$ 上的最后下标 `lp, lq` 和剩余长度 `need=M`：若 $v$ 落在两者之后且 $L(v)=\mathrm{need}$，就选 $v$，并令 `need\leftarrow need-1`。

这样写是对的：$L(v)$ 已经是从 $v$ 出发还能走多长。每次在可行后继里挑最大的值，字典序在第一处分歧就最优；可行性由 $L(v)=\mathrm{need}$ 保证整条链仍能凑满最长。

若现场 $n$ 到 $10^5$，计算 $L(v)$ 可改成按 $p$ 从右往左、用树状数组在 $q$ 的位置上维护 $\max L$，变成 $O(n\log n)$；重构仍可按上面从大到小扫。没有公开 $n$ 时，先写对 $O(n^2)$。

## 参考代码

```python
import sys


def lex_max_lcs(p, q):
    n = len(p)
    pos_p = [0] * (n + 1)
    pos_q = [0] * (n + 1)
    for i, v in enumerate(p):
        pos_p[v] = i
    for i, v in enumerate(q):
        pos_q[v] = i

    L = [1] * (n + 1)
    for v in range(n, 0, -1):
        best = 0
        for w in range(1, n + 1):
            if pos_p[w] > pos_p[v] and pos_q[w] > pos_q[v]:
                if L[w] > best:
                    best = L[w]
        L[v] = 1 + best

    need = max(L[1:]) if n else 0
    lp = lq = -1
    ans = []
    for v in range(n, 0, -1):
        if pos_p[v] > lp and pos_q[v] > lq and L[v] == need:
            ans.append(v)
            lp, lq = pos_p[v], pos_q[v]
            need -= 1
            if need == 0:
                break
    return ans


def main():
    data = list(map(int, sys.stdin.read().split()))
    n = data[0]
    p = data[1:1 + n]
    q = data[1 + n:1 + 2 * n]
    ans = lex_max_lcs(p, q)
    print(*ans)


if __name__ == "__main__":
    main()
```

边界：$n=1$ 只能输出那一个数；$p=q$ 时答案就是 $p$ 本身（它已是最长，且是唯一长度 $n$ 的公共子序列）。空输入不要访问 `max`。

## 复杂度

朴素 $O(n^2)$ 时间、$O(n)$ 空间。树状数组优化后求 $L$ 为 $O(n\log n)$。

## 易错 / 面试追问

- 只做「从大到小能接就拿」，得到的是字典序最大但未必最长，和公开题面不一致。
- 套 $O(n^2)$ 字符串 LCS 且按字符字典序回溯，没有利用「值是 $1\ldots n$ 排列」。
- 重构时漏掉「必须 $L(v)=\mathrm{need}$」，会提前吞掉一个大值，后面凑不齐长度。
- 追问「若不是排列、有重复」：DAG 不再是置换，要回到普通 LCS，值域去重后不能再用位置唯一性。

---
id: ali-oa-max-common-subseq
section: alibaba-oa
order: 5
level: A
title: 阿里 AI 研发 0325：两排列的字典序最大公共子序列怎么贪？
quick: >-
  先算每个值开头还能组成多长的公共子序列，再从大到小挑值，只挑能凑满剩余最长长度的那个。只按值从大到小贪心，可能字典序大但长度不够；本题要先最长，再在最长方案里比字典序。
tags:
  - Alibaba
  - OA
  - 贪心
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 阿里 0325 AI 研发笔试复盘
    url: 'https://www.nowcoder.com/discuss/866741961221292032'
    type: candidate-first-hand
---

## 题目描述

给定两个长度都为 n 的排列 p、q，它们都恰好包含整数 1 到 n 各一次。请找出一个同时是 p 与 q 的子序列的序列，先要求长度尽可能长，再在所有最长答案中选择字典序最大的一个。

子序列允许跳过元素，但保留下来的元素在各原排列中的顺序不能改变；不要求位置连续。字典序在第一处不同元素上比较大小，不能为了更大的首元素牺牲长度。

### 接口与输入输出

实现 `lex_max_lcs(p, q)`，返回满足上述两个优先级的整数列表。输入版本先给 n，再给 p、q 两行排列；输出答案元素。输入保证是合法排列，公开复盘未完整披露 n 的上界。

### 示例

```text
lex_max_lcs([1,2,3], [1,2,3]) -> [1,2,3]
lex_max_lcs([1,2,3], [3,2,1]) -> [3]
lex_max_lcs([2,1,3], [1,2,3]) -> [2,3]
```

第三个例子中 `[1,3]` 和 `[2,3]` 都长为 2，应返回后者。

## 解题思路与参考答案

题目要先保证最长、再挑字典序最大，所以我分两步：先算出每个值开头还能走多长的公共子序列 $L(v)$，再从大到小扫值，只在 $L(v)$ 正好等于剩余所需长度的候选里拿最大的。

## 真题记录

阿里 AI 研发 2026.03.25 研发第 2 题。两个长度为 $n$ 的排列，在所有公共子序列中先取最长，再在最长里取字典序最大的一条。

## 题面

给定两个长度均为 $n$ 的排列 $p$、$q$（都恰好包含 $1\ldots n$）。在它们的所有公共子序列中，首先要求长度最大；若有多个最长公共子序列，则输出其中字典序最大的一个。

输入第一行是 $n$，随后两行是排列 $p$、$q$，公开复盘没有写死 $n$ 的上界。输出一行，就是满足要求的公共子序列（若干个整数）。

## 思路

$p,q$ 都是排列，所以公共子序列就是一组互不相同的值 $v_1,v_2,\ldots$，它们在 $p$ 中的下标递增，在 $q$ 中的下标也递增，相当于值域上的一条 DAG 链。

如果只要字典序、不管长度，从大到小扫一遍、能接在已选位置后面就拿走就行，可这样可能更短。比如 $p=q=[1,3,2]$，从大到小会得到 $[3,2]$，而最长公共子序列是 $[1,3,2]$。题面明确要求先最长、再字典序，所以贪心时必须带上长度信息。

做法是先记下每个值在两个排列中的位置 `pos_p[v]`、`pos_q[v]`，再算 $L(v)$，表示以 $v$ 开头的最长公共子序列长度：

$$
L(v)=1+\max\bigl\{L(w): \mathrm{pos}_p[w]\gt \mathrm{pos}_p[v],\ \mathrm{pos}_q[w]\gt \mathrm{pos}_q[v]\bigr\}
$$

没有后继时 $L(v)=1$，按排列 $p$ 的位置从后往前直接 $O(n^2)$ 算。不能按数值大小倒序：后继关系由位置决定，与值的大小无关。

然后设 $M=\max_v L(v)$，维护已选元素在 $p,q$ 上的最后下标 `lp, lq` 和剩余长度 `need=M`。每次重新遍历所有值，在落于这两个下标之后、且 $L(v)=\mathrm{need}$ 的候选里选最大的 $v$，再令 `need\leftarrow need-1`。每选一个值都要重新搜索，下一位可以比上一位大，不能只按数值倒序扫一遍。

这样做是对的：$L(v)$ 是从 $v$ 出发还能走多长，每次在可行的后继里挑最大的值，字典序在第一处分歧就是最优的；$L(v)=\mathrm{need}$ 保证整条链仍能凑满最长。

如果现场 $n$ 到 $10^5$，求 $L(v)$ 可以按 $p$ 从右往左、用树状数组在 $q$ 的位置上维护 $\max L$，变成 $O(n\log n)$；上面的朴素重构仍是 $O(n^2)$，要让整体达到 $O(n\log n)$，还需要另行优化候选查询，不能只优化求长度这一步。没有公开 $n$ 的时候，先把 $O(n^2)$ 写对。

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
    for v in reversed(p):
        best = 0
        for w in range(1, n + 1):
            if pos_p[w] > pos_p[v] and pos_q[w] > pos_q[v]:
                if L[w] > best:
                    best = L[w]
        L[v] = 1 + best

    need = max(L[1:]) if n else 0
    lp = lq = -1
    ans = []
    while need > 0:
        v = max(v for v in p if pos_p[v] > lp and pos_q[v] > lq and L[v] == need)
        ans.append(v)
        lp, lq = pos_p[v], pos_q[v]
        need -= 1
    return ans


def main():
    data = list(map(int, sys.stdin.read().split()))
    n = data[0]
    p = data[1 : 1 + n]
    q = data[1 + n : 1 + 2 * n]
    ans = lex_max_lcs(p, q)
    print(*ans)


if __name__ == "__main__":
    main()
```

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。原来负责读标准输入的 `if __name__ == "__main__": main()` 入口先注释掉，只保留函数定义，由测试调用函数或模拟输入。

相同排列应保留全部；逆序排列的最长公共子序列长度为 1，此时字典序最大应选最大元素。再检查存在多个最优前缀的情况。

```python
assert lex_max_lcs([1, 2, 3], [1, 2, 3]) == [1, 2, 3]
assert lex_max_lcs([1, 2, 3], [3, 2, 1]) == [3]
assert lex_max_lcs([2, 1, 3], [1, 2, 3]) == [2, 3]
print("simple tests passed")
```

## 复杂度

朴素做法 $O(n^2)$ 时间、$O(n)$ 空间。用树状数组优化后，求 $L$ 是 $O(n\log n)$。

## Edge Cases

$n=1$ 只能输出那一个数；$p=q$ 时答案就是 $p$ 本身，它已经最长，而且是唯一长度为 $n$ 的公共子序列。空输入时别去访问 `max`。

## 追问

**只做「从大到小能接就拿」不行吗？**
得到的是字典序最大，但未必最长，和公开题面不一致，上面的 $[1,3,2]$ 就是反例。

**直接套字符串 LCS 行吗？**
$O(n^2)$ 的字符串 LCS 再按字符字典序回溯，没用上「值是 $1\ldots n$ 排列」这个条件。

**重构时漏掉 $L(v)=\mathrm{need}$ 会怎样？**
会提前吞掉一个大值，后面凑不齐长度。

**如果不是排列、有重复值呢？**
DAG 就不再是置换，要回到普通 LCS；值域去重后，也不能再用位置唯一性。

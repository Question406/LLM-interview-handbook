---
id: ali-oa-k-residue
section: alibaba-oa
order: 16
level: A
title: 阿里春招 0401：下标差为 $k$ 的元素可交换，如何得到字典序最大数组？
quick: >-
  模 $k$ 同余的下标构成一条可任意重排的链。每条链元素降序写回原下标。
tags:
  - Alibaba
  - OA
  - 分组
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-18
sources:
  - title: 阿里系列 2026.04.01 算法岗机试
    url: https://leetcode.cn/discuss/post/3943532/chun-zhao-bi-shi-a-li-xi-lie-ji-shi-fu-p-t91w/
    type: secondary
---

## 真题记录

- 公司 / 场次：阿里系列 2026.04.01 算法岗机试 T1
- 题意：可无限次交换下标相差恰好 $k$ 的两个位置，求能得到的字典序最大数组。

## 题面

给定数组 $a$ 和整数 $k$。你可以无限次交换下标相差恰好 $k$ 的两个位置，即交换 $i$ 与 $i+k$（下标按 $0$ 或 $1$ 编号均可，差为 $k$ 即可）。求所有可达数组中字典序最大的一个。

输入：$n,k$ 和数组 $a$。公开复盘未写死范围；每组排序后总时间 $O(n\log n)$。

输出：字典序最大数组。

## 思路

观察：$|i-j|=k$ 可传递。若能交换 $(i,i+k)$ 和 $(i+k,i+2k)$，则 $i$ 与 $i+2k$ 也能换到一起。因此每个剩余类

$$
r,\; r+k,\; r+2k,\; \ldots \qquad r=0,1,\ldots,k-1
$$

内部的值可以任意重排，不同剩余类之间完全不能交换。

算法：对每个 $r$，抽出该链上的值，**降序**排序，再按原下标从左到右写回。左边更早被字典序比较到，所以每条链都应把大的尽量放左边。

为什么对：字典序先比较最左位置。位置 $0$ 只能从剩余类 $0$ 取值，最优就是该类最大值；确定后再看位置 $1$，依此类推。类之间没有交换，这个局部最优就是全局最优。

不要对整个数组排序。$k=1$ 时只剩一类，答案是全局降序；$k\ge n$ 时每类只有一个元素，数组不能动。

## 参考代码

```python
import sys


def max_perm_by_k(a, k):
    n = len(a)
    if k <= 0:
        return a[:]
    ans = a[:]
    for r in range(k):
        idx = list(range(r, n, k))
        vals = sorted((a[i] for i in idx), reverse=True)
        for i, v in zip(idx, vals):
            ans[i] = v
    return ans


def main():
    data = list(map(int, sys.stdin.read().split()))
    n, k = data[0], data[1]
    a = data[2:2 + n]
    print(*max_perm_by_k(a, k))


if __name__ == "__main__":
    main()
```

边界：$n=0$ 输出空行；$k=1$ 全局降序；含相同元素时 `sorted` 稳定与否不影响值序列。下标从 $1$ 开始时，剩余类改成 $i\bmod k$ 即可，结论相同。

## 复杂度

时间 $O(n\log n)$（各链排序，长度之和为 $n$），空间 $O(n)$。

## 易错 / 面试追问

- 整段 `sort(reverse=True)`，破坏了不能跨越的剩余类。
- 链内升序排序，得到的是字典序最小而不是最大。
- $k=0$ 除零；题目 $k$ 为正，代码里对非正 $k$ 直接原样返回。
- 追问「最多交换 $t$ 次」：剩余类不再能任意重排，要改成每条链上有限步的选择，不是本题。

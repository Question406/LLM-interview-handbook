---
id: ali-oa-variance
section: alibaba-oa
order: 12
level: A
title: 淘天算法 0816：如何用树状数组维护区间方差？
quick: >-
  方差写成 $Q/m-(S/m)^2$。两棵树状数组分别维护区间和 $S$ 与平方和 $Q$，单点改、区间查都是 $O(\log n)$。
tags:
  - Alibaba
  - OA
  - 树状数组
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 淘天算法 2025.08.16 改编真题
    url: https://www.nowcoder.com/discuss/786279353033232384
    type: secondary
---

## 真题记录

- 公司 / 场次：淘天算法岗 2025.08.16（魔法能量波动监测）
- 公开复盘：单点修改能量，查询某段方差。
- 文档 Part III 标明该场「区间统计」公开页公式以图片存在、文本索引不完整。下面按总体方差恒等式写，并标明假设。

## 题面

（公开复盘等价转述）给定长度为 $n$ 的数组 $a$。有 $q$ 次操作，操作有两类：

1. 单点修改：把 $a_i$ 改成 $v$
2. 区间查询：问子数组 $a[l\ldots r]$ 的方差

假设（文本公式未完整公开）：

- 使用总体方差，分母是区间长度 $m=r-l+1$，不是 $m-1$
- 输出浮点数；若现场要求分数 / 取模，把 $S,Q,m$ 原样交出去即可

$$
\mathrm{Var}=\frac{1}{m}\sum x_i^2-\Big(\frac{1}{m}\sum x_i\Big)^2=\frac{Q}{m}-\Big(\frac{S}{m}\Big)^2
$$

输入假设：第一行 $n,q$，第二行初始数组，随后 $q$ 行操作。输出每个查询一行。$n,q$ 未公开精确上界，按 $O((n+q)\log n)$ 写。

## 思路

方差只依赖一阶和 $S$ 与平方和 $Q$，不需要知道每个数相对均值的偏差。因此不必维护「每个前缀的均值」。

算法：开两棵树状数组（或两棵线段树），分别支持单点加、前缀和。区间 $[l,r]$ 的 $S,Q$ 用前缀差得到。修改 $x\to y$ 时：

- $S$ 的树状数组加 $y-x$
- $Q$ 的树状数组加 $y^2-x^2$

这样写是对的：方差恒等式对任意实数成立；树状数组维护的是可加量。均值本身不能直接放进树状数组，因为不同区间的均值不能相加。

注意整数平方溢出，以及 $m=1$ 时方差为 $0$。若题目要样本方差，把第一个 $1/m$ 改成 $1/(m-1)$，并规定单点查询的输出。

## 参考代码

```python
import sys


class Fenwick:
    def __init__(self, n):
        self.n = n
        self.c = [0] * (n + 1)

    def add(self, i, delta):
        while i <= self.n:
            self.c[i] += delta
            i += i & -i

    def pre(self, i):
        s = 0
        while i > 0:
            s += self.c[i]
            i -= i & -i
        return s

    def range_sum(self, l, r):
        return self.pre(r) - self.pre(l - 1)


def main():
    it = map(int, sys.stdin.read().split())
    n, q = next(it), next(it)
    a = [0] + [next(it) for _ in range(n)]
    bit_s = Fenwick(n)
    bit_q = Fenwick(n)
    for i in range(1, n + 1):
        bit_s.add(i, a[i])
        bit_q.add(i, a[i] * a[i])

    out = []
    for _ in range(q):
        op = next(it)
        if op == 1:
            i, v = next(it), next(it)
            old = a[i]
            bit_s.add(i, v - old)
            bit_q.add(i, v * v - old * old)
            a[i] = v
        else:
            l, r = next(it), next(it)
            m = r - l + 1
            s = bit_s.range_sum(l, r)
            qsum = bit_q.range_sum(l, r)
            var = qsum / m - (s / m) ** 2
            out.append("{:.10f}".format(var))
    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
```

边界：单点区间方差为 $0$；改成相同值时 delta 为 $0$；负数能量的平方仍为正。假设操作 $1$ 是修改、$2$ 是查询。若现场编号相反，只改分支。

## 复杂度

单次修改 / 查询 $O(\log n)$，总时间 $O((n+q)\log n)$，空间 $O(n)$。

## 易错 / 面试追问

- 维护均值而不是 $(S,Q)$：区间均值不能用树状数组相减后再当子段均值用在平方里（除非同时带回 $S$）。
- 用 $32$ 位存 $x^2$；或输出时先整除再算，损失精度。
- 总体方差和样本方差搞混。公开公式未完整，答题纸上先写清分母。
- 追问线段树：每个节点存 $(S,Q)$，合并是对应相加，复杂度同阶。

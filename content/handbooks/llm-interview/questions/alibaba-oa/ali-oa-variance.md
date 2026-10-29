---
id: ali-oa-variance
section: alibaba-oa
order: 12
level: A
title: 淘天算法 0816：如何用树状数组维护区间方差？
quick: >-
  把方差写成 $Q/m-(S/m)^2$，开两棵树状数组分别维护区间和 $S$ 与平方和 $Q$。修改 $x\to y$ 时一棵加 $y-x$、一棵加
  $y^2-x^2$，单点改、区间查都是 $O(\log n)$。
tags:
  - Alibaba
  - OA
  - 树状数组
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 淘天算法 2025.08.16 改编真题
    url: 'https://www.nowcoder.com/discuss/786279353033232384'
    type: secondary
---

## 题目描述

维护一个整数数组，支持单点赋值和查询任意连续区间的总体方差。每次查询都针对此前所有修改已经生效后的数组。

下面的函数接口、input representation 和 edge-case behavior 是本卡采用的练习约定；补充题干由本手册编写。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

本卡通过 `main()` 读取：第一行 n、q；第二行 n 个初值；随后 q 行操作。`1 i v` 把第 i 个值改为 v；`2 l r` 查询闭区间 [l,r]，下标从 1 开始，且 l≤r。

### 输出与约束

每个查询输出一行浮点数，保留 10 位小数。总体方差是区间内各元素与区间均值之差的平方平均，分母为区间长度，不是长度减1；单元素区间方差为0。公开题面未完整披露操作编号和方差公式，本卡使用上述约定。

### 示例

```text
输入：
2 4
1 3
2 1 2
1 2 1
2 1 2
2 1 1
输出：
1.0000000000
0.0000000000
0.0000000000
```

## 解题思路与参考答案

我会用方差恒等式把问题拆成两个可加量：区间和 $S$ 和区间平方和 $Q$，各开一棵树状数组，单点改、区间查都是 $O(\log n)$。

$$
\mathrm{Var}=\frac{1}{m}\sum x_i^2-\Big(\frac{1}{m}\sum x_i\Big)^2=\frac{Q}{m}-\Big(\frac{S}{m}\Big)^2
$$

## 题面

（公开复盘等价转述）给定长度为 $n$ 的数组 $a$，有 $q$ 次操作，分两类：

1. 单点修改：把 $a_i$ 改成 $v$
2. 区间查询：问子数组 $a[l\ldots r]$ 的方差

公开页的文本公式不完整，所以我先写明假设：用总体方差，分母是区间长度 $m=r-l+1$，不用 $m-1$；输出浮点数，要是现场要求分数或取模，就把 $S,Q,m$ 原样交出去。输入第一行 $n,q$，第二行初始数组，随后 $q$ 行操作，每个查询输出一行。$n,q$ 没公开精确上界，按 $O((n+q)\log n)$ 写。

## 思路

方差只依赖一阶和 $S$ 与平方和 $Q$，用不着知道每个数相对均值的偏差，所以也不用维护「每个前缀的均值」。均值本身放不进树状数组，因为不同区间的均值不能相加；$S$ 和 $Q$ 都能相加，区间 $[l,r]$ 的值用前缀差就拿到了。

两棵树状数组（换成两棵线段树也行）都只要支持单点加和前缀和。比如把某个位置从 $3$ 改成 $5$，$S$ 那棵加 $5-3=2$，$Q$ 那棵加 $25-9=16$。一般地，修改 $x\to y$ 时：

- $S$ 的树状数组加 $y-x$
- $Q$ 的树状数组加 $y^2-x^2$

恒等式对任意实数成立，树状数组维护的又都是可加量，查询时代进公式就是方差。写的时候留意整数平方溢出，$m=1$ 时方差为 $0$。题目要的是样本方差的话，把第一个 $1/m$ 改成 $1/(m-1)$，并规定单点区间查询输出什么。

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

edge cases：单点区间方差为 $0$；改成相同值时 delta 为 $0$；负数能量的平方仍为正。这里假设操作 $1$ 是修改、$2$ 是查询，现场编号相反的话只改分支。

单次修改或查询 $O(\log n)$，总时间 $O((n+q)\log n)$，空间 $O(n)$。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。原来负责读标准输入的 `if __name__ == "__main__": main()` 入口先注释掉，只保留函数定义，由测试调用函数或模拟输入。

[1,3] 的总体方差为 1；把 3 改为 1 后方差为 0；单点区间的方差也为 0。 用 StringIO 模拟标准输入，redirect_stdout 捕获输出；finally 恢复 stdin，避免影响后续测试。

```python
import io
from contextlib import redirect_stdout

previous_stdin = sys.stdin
try:
    sys.stdin = io.StringIO('2 4\n1 3\n2 1 2\n1 2 1\n2 1 2\n2 1 1\n')
    output = io.StringIO()
    with redirect_stdout(output):
        main()
    assert output.getvalue().strip() == '1.0000000000\n0.0000000000\n0.0000000000'
finally:
    sys.stdin = previous_stdin
print("simple tests passed")
```

## 追问

**直接维护区间均值行不行？**
不行。区间均值不能用树状数组相减后再当子段均值用在平方里，除非同时把 $S$ 带回来，那就等于在维护 $(S,Q)$。

**精度和溢出上容易踩什么？**
用 $32$ 位存 $x^2$ 会溢出；输出时先整除再算会丢精度。

**总体方差和样本方差怎么定？**
公开公式不完整，答题纸上先写清分母。默认用 $m$，题目要样本方差就换成 $m-1$。

**换成线段树怎么写？**
每个节点存 $(S,Q)$，合并就是对应相加，复杂度同阶。

## 真题记录

- 公司 / 场次：淘天算法岗 2025.08.16（魔法能量波动监测）
- 公开复盘：单点修改能量，查询某段方差。
- 文档 Part III 标明该场「区间统计」公开页公式以图片存在、文本索引不完整。上面按总体方差恒等式写，并标明了假设。

---
id: ali-oa-rescue
section: alibaba-oa
order: 11
level: S
title: 淘天算法 0816：森林救援站最多救多少人？
quick: >-
  对角线救援站对每名探险者形成连续可选区间。按右端点排序，并用并查集每次占用区间内最左空站。
tags:
  - Alibaba
  - OA
  - 区间贪心
  - 并查集
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

- 公司 / 场次：淘天算法岗 2025.08.16
- 设定：$n\times n$ 网格，救援站在 $(i,i)$；探险者在 $(x,y)$，按曼哈顿距离选最近站，并列时可协调；每站只能救一人。
- 文档 Part III 标明该场「森林救援站」公开页公式以图片存在、文本索引不完整。下面按已有复盘写清假设，**不补造官方数据范围**。

## 题面

（公开复盘等价转述，并写明假设）

平面上有 $n\times n$ 网格。救援站建在主对角线格子 $(i,i)$，$i=1\ldots n$。另有 $m$ 名探险者，第 $j$ 名在整数格点 $(x_j,y_j)$。

假设（与复盘一致，文本公式未完整公开处按此理解）：

- 距离是曼哈顿距离 $|x-t|+|y-t|$，其中 $t$ 是救援站编号 / 坐标
- 每名探险者必须去**距离最近**的某一座站；若有多座并列最近，可以从中任选一座（可协调）
- 每座站最多救 $1$ 人
- 目标：最多救出多少人

输入假设：第一行 $n,m$，随后 $m$ 行 $x_j,y_j$。输出一个整数。$n,m$ 未公开精确上界；下面实现 $O(m\log m+n)$。

## 思路

到站 $t$ 的距离是 $|x-t|+|y-t|$。对固定 $(x,y)$，这个函数在 $t\le\min(x,y)$ 时随 $t$ 递减，在 $t\ge\max(x,y)$ 时随 $t$ 递增，在中间一段取到最小值 $|x-y|$。因此最近站集合恰好是连续整数区间

$$
\bigl[\min(x,y),\,\max(x,y)\bigr]
$$

问题变成：有 $m$ 个区间，数轴上 $1\ldots n$ 每个点容量为 $1$，最多选多少个区间使得选出的点两两不同（每个区间占其中一点）。

算法：按右端点升序排序。对每个区间，占用其中**最靠左的空闲点**。用并查集维护「$\ge i$ 的下一个空位」：`find(i)` 返回该空位，占用后把 `i` 指向 `i+1`。若空位超过右端点，这个人救不了。

这样写是对的：右端点更早的区间更紧。给当前区间一个尽量靠左的点，不会让后面更靠右的区间失去本可以留给它们的右侧空位。这是经典的「区间选点 / 任务分配」交换论证。

若某名探险者的坐标可能落到 $1\ldots n$ 之外，区间要先与 $[1,n]$ 求交；公开复盘未写这种情况，代码里做了裁剪，避免假装输入一定合法。

## 参考代码

```python
import sys


class DSU:
    def __init__(self, n):
        self.p = list(range(n + 2))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def occupy(self, x):
        self.p[x] = self.find(x + 1)


def max_rescue(n, people):
    intervals = []
    for x, y in people:
        L, R = min(x, y), max(x, y)
        L = max(L, 1)
        R = min(R, n)
        if L <= R:
            intervals.append((L, R))
    intervals.sort(key=lambda t: (t[1], t[0]))
    dsu = DSU(n)
    ans = 0
    for L, R in intervals:
        pos = dsu.find(L)
        if pos <= R:
            dsu.occupy(pos)
            ans += 1
    return ans


def main():
    data = list(map(int, sys.stdin.read().split()))
    n, m = data[0], data[1]
    people = []
    idx = 2
    for _ in range(m):
        people.append((data[idx], data[idx + 1]))
        idx += 2
    print(max_rescue(n, people))


if __name__ == "__main__":
    main()
```

边界：$m=0$ 答案 $0$；所有人挤在同一个对角站时只能救 $1$ 人；$x=y$ 时区间退化成单点。

## 复杂度

排序 $O(m\log m)$，并查集近似 $O(m\alpha(n))$。空间 $O(n+m)$。

## 易错 / 面试追问

- 把最近站理解成「只去 $\min(x,y)$ 或只去 $\max(x,y)$」，漏掉中间整段并列。
- 按左端点排序再贪心，对交叉区间不是最优。
- 占用空位时线性扫描 $[L,R]$，在 $n$ 大时超时；要用并查集或 `set`。
- 追问「每站容量为 $c$」：把每个点复制 $c$ 次，或在并查集上维护剩余容量。公开复盘是容量 $1$。

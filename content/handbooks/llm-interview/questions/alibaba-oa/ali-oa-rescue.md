---
id: ali-oa-rescue
section: alibaba-oa
order: 11
level: S
title: 淘天算法 0816：森林救援站最多救多少人？
quick: >-
  每名探险者的最近站是对角线上一段连续区间
  $[\min(x,y),\max(x,y)]$，问题就变成区间选点。按右端点排序，用并查集每次占区间里最左的空站，占不到就救不了。
tags:
  - Alibaba
  - OA
  - 区间贪心
  - 并查集
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

n×n 网格的主对角线上有 n 座救援站，第 t 座位于 (t,t)。另有若干探险者，每人只能前往距离自己最近的一座站；并列最近时可以协调选择。每座站最多救一人，求最多能救多少人。

下面的函数接口、input representation 和 edge-case behavior 是本卡采用的练习约定；补充题干由本手册编写。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `max_rescue(n, people)`；n 为正整数，people 是整数坐标对列表。距离定义为曼哈顿距离，即横、纵坐标差的绝对值之和。本题基础输入保证坐标位于 1 到 n 的网格内。

### 输出与约束

返回最大获救人数，不要求输出分配方案。探险者可放弃获救，但不能为提高人数而前往一个并非最近的站。公开复盘公式文本不完整，上述距离、并列协调及容量是本卡采用的练习约定。

### 示例

```text
n=2, people=[(1,2),(1,1)] -> 2
第一个人可去站1或站2，第二个人只能去站1，可分别安排站2和站1。
n=1, people=[(1,1),(1,1)] -> 1
```

## 解题思路与参考答案

先把几何问题化成区间：探险者到对角站 $t$ 的曼哈顿距离，在 $t\in[\min(x,y),\max(x,y)]$ 上取到最小，所以每人可选的站是一段连续区间。之后就是经典的区间分配：按右端点排序，每人占区间内最左的空站，用并查集找空站。

## 真题记录

淘天算法岗 2025.08.16。设定是 $n\times n$ 网格，救援站在 $(i,i)$；探险者在 $(x,y)$，按曼哈顿距离选最近站，并列时可以协调；每站只能救一人。

文档 Part III 标明，这场「森林救援站」公开页的公式以图片存在，文本索引不完整。下面按已有复盘写清假设，不补造官方数据范围。

## 题面

（公开复盘等价转述，并写明假设）

平面上有 $n\times n$ 网格。救援站建在主对角线格子 $(i,i)$，$i=1\ldots n$。另有 $m$ 名探险者，第 $j$ 名在整数格点 $(x_j,y_j)$。

下面的假设与复盘一致，文本公式没有完整公开的地方按此理解：

- 距离是曼哈顿距离 $|x-t|+|y-t|$，其中 $t$ 是救援站编号 / 坐标
- 每名探险者必须去距离最近的某一座站；若有多座并列最近，可以从中任选一座（可协调）
- 每座站最多救 $1$ 人
- 目标是最多救出多少人

输入假设第一行是 $n,m$，随后 $m$ 行 $x_j,y_j$，输出一个整数。$n,m$ 没有公开精确上界，下面的实现是 $O(m\log m+n)$。

## 思路

到站 $t$ 的距离是 $|x-t|+|y-t|$。固定 $(x,y)$，它在 $t\le\min(x,y)$ 时随 $t$ 递减，在 $t\ge\max(x,y)$ 时随 $t$ 递增，中间一段取到最小值 $|x-y|$。所以最近站集合正好是连续整数区间

$$
\bigl[\min(x,y),\,\max(x,y)\bigr]
$$

比如探险者在 $(2,5)$，站 $2,3,4,5$ 的距离都是 $3$，四座站都可以去。

问题就变成：有 $m$ 个区间，数轴上 $1\ldots n$ 每个点容量为 $1$，最多选多少个区间，让每个选中的区间各占其中一个点、点两两不同。

做法是按右端点升序排序，每个区间占它里面最靠左的空闲点。并查集维护「$\ge i$ 的下一个空位」，`find(i)` 返回这个空位，占用后把 `i` 指向 `i+1`；找到的空位超过右端点，这个人就救不了。

这样贪心是对的：右端点越早的区间越紧，给当前区间一个尽量靠左的点，不会让后面更靠右的区间失去本来能留给它们的右侧空位，这是区间选点 / 任务分配的交换论证。

如果探险者坐标可能落到 $1\ldots n$ 之外，区间要先和 $[1,n]$ 求交。公开复盘没写这种情况，代码里还是做了裁剪，避免假装输入一定合法。

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

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。原来负责读标准输入的 `if __name__ == "__main__": main()` 入口先注释掉，只保留函数定义，由测试调用函数或模拟输入。

两个对象争一个位置只能救一个；分别占用两个位置可以救两个。最后检查完全落在合法位置范围外的区间被忽略。

```python
assert max_rescue(1, [(1, 1), (1, 1)]) == 1
assert max_rescue(2, [(1, 2), (1, 1)]) == 2
assert max_rescue(2, [(3, 4)]) == 0
print("simple tests passed")
```

## 复杂度

排序 $O(m\log m)$，并查集近似 $O(m\alpha(n))$，空间 $O(n+m)$。

## Edge Cases

$m=0$ 时答案为 $0$；所有人挤在同一个对角站时只能救 $1$ 人；$x=y$ 时区间退化成单点。

## 追问

**最近站只算 $\min(x,y)$ 或者只算 $\max(x,y)$ 行吗？**
不行，中间一整段都是并列最近，漏掉就会少救人。

**按左端点排序再贪心行不行？**
对交叉区间不是最优，要按右端点排。

**占空位时线性扫描 $[L,R]$ 可以吗？**
$n$ 大时会超时，要用并查集或 `set`。

**每站容量是 $c$ 呢？**
把每个点复制 $c$ 次，或者在并查集上维护剩余容量。公开复盘是容量 $1$。

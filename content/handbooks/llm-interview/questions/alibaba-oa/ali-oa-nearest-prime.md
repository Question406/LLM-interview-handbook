---
id: ali-oa-nearest-prime
section: alibaba-oa
order: 17
level: B
title: 阿里春招 0401：离 $x$ 最近的质数，同距如何破？
quick: >-
  距离从 $0$ 向外扩，先测 $x-d$ 再测 $x+d$，第一次命中就是最近且同距取小。试除用 $6k\pm 1$ 到 $\sqrt{v}$。
tags:
  - Alibaba
  - OA
  - 数论
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阿里系列 2026.04.01 算法岗机试
    url: https://leetcode.cn/discuss/post/3943532/chun-zhao-bi-shi-a-li-xi-lie-ji-shi-fu-p-t91w/
    type: secondary
---

## 真题记录

- 公司 / 场次：阿里系列 2026.04.01 算法岗机试 T2
- 题意：找质数 $p$ 使 $|p-x|$ 最小；并列取更小的 $p$。

## 题面

对每个整数 $x$，找与 $x$ 距离最近的质数 $p$，使 $|p-x|$ 最小；若左右两侧存在同距离质数，取较小的那个。

输入：若干个 $x$。输出：每个 $x$ 对应的质数。公开复盘数值约在常见整型范围；未写死上界。

## 思路

最近质数的距离从 $0$ 开始向外扩。同一距离 $d$ 上最多两个候选 $x-d$ 和 $x+d$。题目要求同距取小，所以先检查左端 $x-d$（需 $\gt 1$），再检查右端。

算法：对每个询问，$d=0,1,2,\ldots$，依次测试 $x-d$、$x+d$。第一次命中质数就输出。判质用试除：$\le 1$ 不是质数；$2,3$ 特判；之后只试 $6k\pm 1$ 直到 $\sqrt{v}$。

这样写是对的：质数在整数轴上无界，循环一定会停。$d$ 从小到大保证距离最小；同距先左后右保证第二关键字。

不必线性筛，除非询问很多且 $x$ 落在固定上界内。数据范围不大时试除足够。$x\le 1$ 时左侧没有合法质数，只会向右找到 $2$。

## 参考代码

```python
import sys


def is_prime(v):
    if v <= 1:
        return False
    if v <= 3:
        return True
    if v % 2 == 0 or v % 3 == 0:
        return False
    i = 5
    while i * i <= v:
        if v % i == 0 or v % (i + 2) == 0:
            return False
        i += 6
    return True


def nearest_prime(x):
    d = 0
    while True:
        left = x - d
        if left > 1 and is_prime(left):
            return left
        right = x + d
        if d > 0 and is_prime(right):
            return right
        if d == 0 and is_prime(x):
            return x
        d += 1


def main():
    data = list(map(int, sys.stdin.read().split()))
    if not data:
        return
    i = 0
    if len(data) > 1:
        # 兼容「先 T 再 T 个 x」以及「直接若干 x」
        if data[0] == len(data) - 1:
            xs = data[1:]
        else:
            xs = data
    else:
        xs = data
    for x in xs:
        print(nearest_prime(x))


if __name__ == "__main__":
    main()
```

边界：$x=1$ 或 $x\le 0$ 得到 $2$；$x=4$ 时 $3$ 与 $5$ 同距，输出 $3$；$x=8$ 输出 $7$。$x$ 本身是质数时 $d=0$ 直接返回。

## 复杂度

单次询问最坏与「到附近质数的间隙 $\times$ 试除 $\sqrt{x}$」有关。对普通 $32$ 位整数足够。多询问且值域小：先筛到 $\mathrm{MAX}+\Delta$，再对每个 $x$ 左右各走一步。

## 易错 / 面试追问

- 同距时先看了 $x+d$，输出了较大的那个。
- `is_prime` 把 $1$ 判成质数，或对偶数只排除了 $2$ 忘了 $3$。
- 对负数取模 / 开方；左侧候选必须 $\gt 1$。
- 追问「质数密度」：可以提贝特朗-切比雪夫定理保证 $(x,2x)$ 内有质数，用来说明循环有上界，但实现仍是向外扩。

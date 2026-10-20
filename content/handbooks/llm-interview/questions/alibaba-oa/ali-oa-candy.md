---
id: ali-oa-candy
section: alibaba-oa
order: 4
level: A
title: 阿里 AI 研发 0325：分糖果的单人总分 min / max 是什么？
quick: >-
  每种糖独立均分，$k$ 人份差至多 $1$。最小值是 $\sum\lfloor c_i/k\rfloor$，最大值是 $\sum\lceil c_i/k\rceil$。
tags:
  - Alibaba
  - OA
  - 数学
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阿里 0325 AI 研发笔试复盘
    url: https://www.nowcoder.com/discuss/866741961221292032
    type: candidate-first-hand
  - title: 淘天笔试糖果/字典序讨论
    url: https://www.nowcoder.com/discuss/867439311984082944
    type: secondary
---

## 真题记录

- 公司 / 场次：阿里 AI 研发 2026.03.25 · 研发 Q1
- 原始题意：$n$ 种糖、数量 $c_i$，分给 $k$ 人；同种糖每人份数差至多 $1$。求某一个指定小朋友总分的最小可能值与最大可能值。

## 题面

有 $n$ 种糖果，第 $i$ 种有 $c_i$ 个，要把**所有糖果**分给 $k$ 个孩子。对任意一种糖果，任意两个孩子拿到的该种糖果数量之差不能超过 $1$。问在所有合法分配中，某个指定孩子最后拿到糖果总数的最小值和最大值分别是多少。

输入：$n$、$k$，以及 $c_1\ldots c_n$。公开版本允许 $k$、$c_i$ 到 $10^9$ 量级。

输出：两个整数，先最小总数，再最大总数。

## 思路

不同种类互不影响。对固定种类 $i$，把 $c_i$ 个物品分给 $k$ 人且最大最小差 $\le 1$，分配形态是唯一的：

- 每人至少 $\lfloor c_i/k\rfloor$
- 恰有 $c_i\bmod k$ 个人多拿 $1$ 个，即拿到 $\lceil c_i/k\rceil$
- 若 $c_i\bmod k=0$，则每人恰好 $c_i/k$，上下限相同

指定孩子对第 $i$ 种既可以分到下限，也可以（在仍有「多出来的 $1$ 个」时）分到上限。这两件事对每种糖独立：我们可以让他每种都拿下限，或每种都拿上限。

因此

$$
\mathrm{min}=\sum_{i=1}^{n}\Big\lfloor\frac{c_i}{k}\Big\rfloor,\qquad
\mathrm{max}=\sum_{i=1}^{n}\Big\lceil\frac{c_i}{k}\Big\rceil
$$

其中 $\lceil c_i/k\rceil=\lfloor(c_i+k-1)/k\rfloor$。

这样写是对的：下限方案存在，因为每种都可以把多出来的份分给别人；上限方案存在，因为每种只要 $c_i\bmod k\neq 0$ 就把那一份多的给他，否则上下限相同。不需要背包，也不需要枚举「他拿了多少种的上限」。

常见误区是：某一次分配里全员总分的最小最大。全员总分恒等于 $\sum c_i$。题目要的是同一个人在不同合法分配中的极值。

## 参考代码

```python
import sys


def candy_min_max(k, c):
    mn = mx = 0
    for x in c:
        mn += x // k
        mx += (x + k - 1) // k
    return mn, mx


def main():
    data = list(map(int, sys.stdin.read().split()))
    n, k = data[0], data[1]
    c = data[2:2 + n]
    mn, mx = candy_min_max(k, c)
    print(mn, mx)


if __name__ == "__main__":
    main()
```

边界：$n=0$ 时两个答案都是 $0$；$k=1$ 时 min=max=$\sum c_i$；某个 $c_i=0$ 时该项贡献 $0$；`k` 与 `c_i` 到 $10^9$ 时必须用任意精度或 64 位整数，Python 的 `int` 即可。

## 复杂度

时间 $O(n)$，空间 $O(1)$。

## 易错 / 面试追问

- 做成「把 $\sum c_i$ 均分」或 0-1 背包，忽略「每种糖单独满足份差 $\le 1$」。
- `ceil` 写成 `(x+k-1)/k` 时用了 32 位整数溢出；公开数据 $k,c_i$ 可到 $10^9$。
- 追问「指定的是第 $p$ 个孩子，和其他孩子有额外上界」：只要每种仍只能 floor/ceil，答案公式不变。
- 追问「不是分完所有糖」：那是另一种题，最小值可变成 $0$，本题必须分完。

---
id: ali-oa-candy
section: alibaba-oa
order: 4
level: A
title: 阿里 AI 研发 0325：分糖果的单人总分 min / max 是什么？
quick: >-
  每种糖单独看，$k$ 个人的份数差至多 $1$，所以指定孩子在第 $i$ 种上只可能拿 $\lfloor c_i/k\rfloor$ 或 $\lceil c_i/k\rceil$。各种糖互不牵制，最小值是 $\sum\lfloor c_i/k\rfloor$，最大值是 $\sum\lceil c_i/k\rceil$。
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

## 题目描述

有 n 种糖果，第 i 种有 `c[i]` 颗，要把所有糖果分给 k 个孩子。对每一种糖果，任意两个孩子拿到的数量之差都不能超过 1。指定其中一个孩子，求在所有满足条件的分配中，他拿到的糖果总数的最小值和最大值。

### 输入与输出

实现 `candy_min_max(k, c)`，其中 `k >= 1`，`c` 为 n 个非负整数。返回二元组 `(minimum, maximum)`，分别是指定孩子可能拿到的最少和最多总颗数。不同种糖果的分配彼此独立，必须把所有糖果分完。

笔试输入形式为：第一行 `n k`，第二行 n 个数量；输出最小值与最大值，中间用空格隔开。公开版本允许 k 和单种糖果数达到十亿量级，结果应使用足够大的整数。

### 示例

```text
k = 3, c = [4,6]
candy_min_max(k, c) -> (3,4)

标准输入：
2 3
4 6
标准输出：
3 4
```

该示例中指定孩子最少可拿 1 颗第一种、2 颗第二种；最多可拿 2 颗第一种、2 颗第二种。

## 解题思路与参考答案

答案是两个求和：指定孩子的最小总数是 $\sum\lfloor c_i/k\rfloor$，最大总数是 $\sum\lceil c_i/k\rceil$。每种糖必须单独满足份差不超过 $1$，所以这个孩子在每一种上只有下限和上限两个选择，而且各种糖之间互不牵制。

## 真题记录

阿里 AI 研发 2026.03.25 研发第 1 题。原始题意是 $n$ 种糖、数量 $c_i$，分给 $k$ 人，同种糖每人份数差至多 $1$，求某一个指定小朋友总分的最小可能值与最大可能值。

## 题面

有 $n$ 种糖果，第 $i$ 种有 $c_i$ 个，要把**所有糖果**分给 $k$ 个孩子。对任意一种糖果，任意两个孩子拿到的该种糖果数量之差不能超过 $1$。问在所有合法分配中，某个指定孩子最后拿到糖果总数的最小值和最大值分别是多少。

输入是 $n$、$k$ 和 $c_1\ldots c_n$，公开版本允许 $k$、$c_i$ 到 $10^9$ 量级。输出两个整数，先最小总数，再最大总数。

## 思路

先只看一种糖。把 $c_i$ 个分给 $k$ 人、最多最少差不超过 $1$，分法的形态是唯一的：每人至少 $\lfloor c_i/k\rfloor$，恰好有 $c_i\bmod k$ 个人多拿 $1$ 个，拿到 $\lceil c_i/k\rceil$；如果 $c_i\bmod k=0$，每人正好 $c_i/k$，上下限相同。比如 $c_i=7$、$k=3$，分出来就是 $2,2,3$，指定孩子拿 $2$ 还是拿 $3$ 都可以。

指定孩子在第 $i$ 种上可以拿下限，也可以在还有「多出来的 $1$ 个」时拿上限。这件事对每种糖是独立的，所以可以让他每种都拿下限，或者每种都拿上限：

$$
\mathrm{min}=\sum_{i=1}^{n}\Big\lfloor\frac{c_i}{k}\Big\rfloor,\qquad
\mathrm{max}=\sum_{i=1}^{n}\Big\lceil\frac{c_i}{k}\Big\rceil
$$

其中 $\lceil c_i/k\rceil=\lfloor(c_i+k-1)/k\rfloor$。

这两种方案都确实存在。下限方案里，每种糖多出来的份都分给别人；上限方案里，只要 $c_i\bmod k\neq 0$ 就把多的那份给他，否则上下限本来就一样。所以不需要背包，也不用枚举「他拿了多少种的上限」。

有人会理解成某一次分配里全员总分的最小和最大，可全员总分恒等于 $\sum c_i$。题目问的是同一个人在不同合法分配中的极值。

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

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。原来负责读标准输入的 `if __name__ == "__main__": main()` 入口先注释掉，只保留函数定义，由测试调用函数或模拟输入。

用整除和带余数两类输入比较向下取整与向上取整。k=3 时 4 颗与 6 颗分别贡献最少 1、2，最多 2、2。

```python
assert candy_min_max(3, [4, 6]) == (3, 4)
assert candy_min_max(3, [3, 6]) == (3, 3)
assert candy_min_max(1, [2, 3]) == (5, 5)
print("simple tests passed")
```

## 复杂度

时间 $O(n)$，空间 $O(1)$。

## 边界

$n=0$ 时两个答案都是 $0$；$k=1$ 时 min=max=$\sum c_i$；某个 $c_i=0$ 时这一项贡献 $0$。`k` 与 `c_i` 到 $10^9$ 时要用任意精度或 64 位整数，Python 的 `int` 就够。

## 追问

**能不能把 $\sum c_i$ 均分，或者做成 0-1 背包？**
不行。约束是每种糖单独满足份差 $\le 1$，按总数均分忽略了这一点，背包也用不上。

**C++ 里 ceil 怎么写才安全？**
`(x+k-1)/k` 用 32 位整数会溢出，公开数据 $k,c_i$ 可到 $10^9$，要用 64 位。

**如果指定的是第 $p$ 个孩子，而且其他孩子有额外上界呢？**
只要每种糖仍然只能拿 floor 或 ceil，答案公式不变。

**如果不要求分完所有糖呢？**
那是另一种题，最小值可以变成 $0$。本题必须分完。

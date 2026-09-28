---
id: ali-oa-nonadj-even
section: alibaba-oa
order: 2
level: A
title: 淘天/阿里国际实习笔试：不相邻偶数对怎么数？
quick: >-
  偶数对只能是奇+奇或偶+偶。先算 $C(\mathrm{odd},2)+C(\mathrm{even},2)$，再减去相邻同奇偶对。不要枚举 $O(n^2)$。
tags:
  - Alibaba
  - OA
  - 组合计数
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 淘天/阿里国际 2025 实习笔试解析
    url: http://www.jsqmd.com/news/1167387/
    type: secondary
---

## 真题记录

- 公司 / 场次：淘天 / 阿里国际 2025 实习笔试
- 原始题意：数组 $a$，统计满足 $i\neq j$、$|i-j|\gt 1$ 且 $a_i+a_j$ 为偶数的无序对。
- 示例：$[1,2,3,4,6]$ 答案为 $3$（$1+3$，$2+4$，$2+6$）。相邻的 $4+6$ 虽然也是偶数，但不计入。

## 题面

给定长度为 $n$ 的整数数组 $a$。统计无序对 $(i,j)$ 的个数，满足：

1. $1\le i\lt j\le n$
2. $j-i\gt 1$（下标不相邻）
3. $a_i+a_j$ 为偶数

公开复盘未给出精确数据范围。按笔试常见规模，实现应做到 $O(n)$，避免 $O(n^2)$ 双循环。

输入可以是：第一行 $n$，第二行 $n$ 个整数。输出一个整数。

## 思路

两个整数之和为偶数，当且仅当它们奇偶性相同。因此合法对只能是「奇+奇」或「偶+偶」。

算法：先忽略「不相邻」约束，同奇偶无序对总数为

$$
\binom{\mathrm{odd}}{2}+\binom{\mathrm{even}}{2}=\frac{\mathrm{odd}\,(\mathrm{odd}-1)}{2}+\frac{\mathrm{even}\,(\mathrm{even}-1)}{2}
$$

再扫一遍相邻位置。若 $a_i$ 与 $a_{i+1}$ 同奇偶，说明这对被多算了，答案减 $1$。

组合数已经保证 $i\neq j$ 且每对只计一次；相邻同奇偶对是唯一需要剔除的部分。$\binom{k}{2}$ 不含自己和自己。

样例核对：奇数 $\{1,3\}$ 共 $1$ 对，偶数 $\{2,4,6\}$ 共 $3$ 对，合计 $4$；相邻里只有 $(4,6)$ 同偶，减 $1$，得到 $3$。

## 参考代码

```python
import sys


def count_nonadj_even_pairs(a):
    odd = even = 0
    for x in a:
        if x & 1:
            odd += 1
        else:
            even += 1
    ans = odd * (odd - 1) // 2 + even * (even - 1) // 2
    for i in range(1, len(a)):
        if (a[i] & 1) == (a[i - 1] & 1):
            ans -= 1
    return ans


def main():
    data = list(map(int, sys.stdin.read().split()))
    if not data:
        return
    n = data[0]
    a = data[1:1 + n]
    print(count_nonadj_even_pairs(a))


if __name__ == "__main__":
    main()
```

边界：`n=0/1` 时组合数为 $0$，没有相邻对，答案 $0$；`n=2` 时若两数同奇偶则组合数是 $1$、相邻再减掉，答案仍为 $0$；全奇或全偶也能走同一公式。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$（不计输入数组）。

## 易错 / 面试追问

- 把无序对写成 $i\lt j$ 之后又对每对乘 $2$，或把 $\binom{k}{2}$ 写成 $k(k-1)$ 忘了除以 $2$。
- 误减「自己和自己」：组合数不含 $i=j$。
- 追问「改成有序对 / 改成子数组相邻差」时，先重申奇偶条件，再改计数，不要重写暴力。
- 负数奇偶：用 `x & 1` 或 `x % 2` 时，Python 的 `%` 对负数仍按数学模，但其他语言里建议 `x % 2 == 0` 判断偶数，或先看绝对值。

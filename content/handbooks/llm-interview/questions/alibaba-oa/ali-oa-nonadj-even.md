---
id: ali-oa-nonadj-even
section: alibaba-oa
order: 2
level: A
title: 淘天/阿里国际实习笔试：不相邻偶数对怎么数？
quick: >-
  和为偶数只能是奇+奇或偶+偶，所以先算 $C(\mathrm{odd},2)+C(\mathrm{even},2)$，再扫一遍减掉相邻的同奇偶对。整体
  $O(n)$，不用枚举 $O(n^2)$ 对。
tags:
  - Alibaba
  - OA
  - 组合计数
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 淘天/阿里国际 2025 实习笔试解析
    url: 'http://www.jsqmd.com/news/1167387/'
    type: secondary
---

## 题目描述

给定整数数组 a，统计满足以下条件的无序下标对：两个下标不同且不相邻，对应两个元素之和为偶数。按从 0 开始的下标表示，条件为 `i < j` 且 `j - i > 1`。

相同数值出现在不同下标时仍是不同候选位置，每个无序下标对只计一次。返回的是对数，不是数值之和。

### 接口与输入输出

实现 `count_nonadj_even_pairs(a) -> int`。输入为整数列表；合法的小长度数组不足以构成一对时返回 0。标准输入先给 n，再给 n 个整数，输出计数。原公开材料没有可靠给出精确上界。

### 示例

```text
count_nonadj_even_pairs([1,2,3,4,6]) -> 3
count_nonadj_even_pairs([1,3,5])     -> 1
count_nonadj_even_pairs([2,4])       -> 0
```

第一个例子计入的数值对为 1+3、2+4、2+6；末尾 4 与 6 相邻，不计入。

## 解题思路与参考答案

和为偶数等价于两个数同奇偶。所以我先不管「不相邻」，按奇数个数、偶数个数各算一个组合数，再扫一遍相邻位置，把同奇偶的相邻对减掉，整体 $O(n)$。

## 真题记录

淘天 / 阿里国际 2025 实习笔试。原始题意是给定数组 $a$，统计满足 $i\neq j$、$|i-j|\gt 1$ 且 $a_i+a_j$ 为偶数的无序对。示例 $[1,2,3,4,6]$ 答案为 $3$（$1+3$，$2+4$，$2+6$）；相邻的 $4+6$ 虽然也是偶数，但不计入。

## 题面

给定长度为 $n$ 的整数数组 $a$。统计无序对 $(i,j)$ 的个数，满足：

1. $1\le i\lt j\le n$
2. $j-i\gt 1$（下标不相邻）
3. $a_i+a_j$ 为偶数

公开复盘没有给出精确数据范围。按笔试常见规模，实现应做到 $O(n)$，避免 $O(n^2)$ 双循环。

输入可以是第一行 $n$、第二行 $n$ 个整数，输出一个整数。

## 思路

两个整数之和为偶数，当且仅当它们奇偶性相同，所以合法对只能是「奇+奇」或「偶+偶」。

先忽略不相邻约束，同奇偶的无序对总数是

$$
\binom{\mathrm{odd}}{2}+\binom{\mathrm{even}}{2}=\frac{\mathrm{odd}\,(\mathrm{odd}-1)}{2}+\frac{\mathrm{even}\,(\mathrm{even}-1)}{2}
$$

组合数已经保证 $i\neq j$、每对只计一次，$\binom{k}{2}$ 里不含自己和自己。剩下要剔除的只有相邻的同奇偶对：再扫一遍，$a_i$ 和 $a_{i+1}$ 同奇偶，说明这对被多算了，答案减 $1$。

用样例核对一下：奇数 $\{1,3\}$ 共 $1$ 对，偶数 $\{2,4,6\}$ 共 $3$ 对，合计 $4$；相邻对里只有 $(4,6)$ 同偶，减 $1$，得到 $3$。

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
    a = data[1 : 1 + n]
    print(count_nonadj_even_pairs(a))


if __name__ == "__main__":
    main()
```

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。原来负责读标准输入的 `if __name__ == "__main__": main()` 入口先注释掉，只保留函数定义，由测试调用函数或模拟输入。

三个奇数只有首尾一对不相邻；两个相邻偶数必须排除。再用不同奇偶组合确认只统计和为偶数的配对。

```python
assert count_nonadj_even_pairs([1, 3, 5]) == 1
assert count_nonadj_even_pairs([2, 4]) == 0
assert count_nonadj_even_pairs([1, 2, 3, 4]) == 2
print("simple tests passed")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$（不计输入数组）。

## Edge Cases

`n=0/1` 时组合数为 $0$，也没有相邻对，答案 $0$；`n=2` 时如果两数同奇偶，组合数是 $1$，相邻再减掉，答案仍为 $0$；全奇或全偶也走同一个公式。

## 追问

**无序对怎么算才不会翻倍？**
用 $\binom{k}{2}=k(k-1)/2$。写成 $i\lt j$ 之后又对每对乘 $2$，或者写成 $k(k-1)$ 忘了除以 $2$，都会算成两倍。

**要不要再减掉「自己和自己」？**
不用，组合数本来就不含 $i=j$。

**改成有序对，或者改成子数组相邻差呢？**
先重申奇偶条件，再改计数方式，没必要重写暴力。

**负数的奇偶怎么判？**
Python 里 `x & 1` 或 `x % 2` 对负数都按数学模来；其他语言里建议用 `x % 2 == 0` 判断偶数，或者先看绝对值。

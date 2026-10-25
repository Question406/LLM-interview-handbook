---
id: ali-oa-k-residue
section: alibaba-oa
order: 16
level: A
title: 阿里春招 0401：下标差为 $k$ 的元素可交换，如何得到字典序最大数组？
quick: >-
  下标模 $k$ 同余的位置连成一条链，链内可以任意重排，链之间换不了。每条链的值降序排好，再按原下标从左到右写回，就是字典序最大。
tags:
  - Alibaba
  - OA
  - 分组
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阿里系列 2026.04.01 算法岗机试
    url: https://leetcode.cn/discuss/post/3943532/chun-zhao-bi-shi-a-li-xi-lie-ji-shi-fu-p-t91w/
    type: secondary
---

## 题目描述

给定整数数组 a 和正整数 k。一次操作可以交换下标相差恰好 k 的两个元素；操作次数不限。求从 a 出发可得到的字典序最大的数组。

字典序比较从左向右进行：第一处不同的位置，元素较大的数组更大。只能进行指定距离的交换，不能任意交换两个位置。

### 接口与输入输出

实现 `max_perm_by_k(a, k)`，返回一个长度和元素多重集合都与 a 相同的新数组。`k >= 1`；k 大于或等于数组长度时也属于合法情况。标准输入第一行 `n k`，第二行给 n 个整数，输出最终数组。

### 示例

```text
max_perm_by_k([1,4,3,2], 2) -> [3,4,1,2]
max_perm_by_k([1,3,2], 1)   -> [3,2,1]
max_perm_by_k([1,3,2], 5)   -> [1,3,2]
```

公开复盘未完整披露数值范围，这里不另设未经证实的原题上界。

## 解题思路与参考答案

下标模 $k$ 余数相同的位置可以任意互换，余数不同的位置之间换不了。所以每个剩余类内部降序排列、写回原下标，得到的就是字典序最大的数组。

## 真题记录

阿里系列 2026.04.01 算法岗机试第 1 题：可以无限次交换下标相差恰好 $k$ 的两个位置，求能得到的字典序最大数组。

## 题面

给定数组 $a$ 和整数 $k$。你可以无限次交换下标相差恰好 $k$ 的两个位置，即交换 $i$ 与 $i+k$（下标按 $0$ 或 $1$ 编号均可，差为 $k$ 即可）。求所有可达数组中字典序最大的一个。

输入是 $n,k$ 和数组 $a$。公开复盘没有写死范围；每组排序后总时间 $O(n\log n)$。输出字典序最大的数组。

## 思路

相差 $k$ 的交换可以传递：能换 $(i,i+k)$ 和 $(i+k,i+2k)$，$i$ 和 $i+2k$ 也就能换到一起。所以每个剩余类

$$
r,\; r+k,\; r+2k,\; \ldots \qquad r=0,1,\ldots,k-1
$$

内部的值可以任意重排，不同剩余类之间完全换不了。比如 $k=2$，下标 $0,2,4,\ldots$ 是一组，$1,3,5,\ldots$ 是另一组。

做法是对每个 $r$ 抽出这条链上的值，降序排序，再按原下标从左到右写回。字典序先比最左边的位置，位置 $0$ 只能从剩余类 $0$ 里取值，最好就是这一类的最大值；定下来再看位置 $1$，依此类推。类之间换不了，每类各自最优就是全局最优。

整段 `sort` 会打乱剩余类。$k=1$ 时只有一类，答案是全局降序；$k\ge n$ 时每类只有一个元素，数组动不了。

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

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。原来负责读标准输入的 `if __name__ == "__main__": main()` 入口先注释掉，只保留函数定义，由测试调用函数或模拟输入。

k=2 时偶数下标与奇数下标各自降序；k=1 可以全局重排；k 大于长度时各组只有一个元素。

```python
assert max_perm_by_k([1, 4, 3, 2], 2) == [3, 4, 1, 2]
assert max_perm_by_k([1, 3, 2], 1) == [3, 2, 1]
assert max_perm_by_k([1, 3, 2], 5) == [1, 3, 2]
print("simple tests passed")
```

## 复杂度

时间 $O(n\log n)$（各链分别排序，长度之和为 $n$），空间 $O(n)$。

## 边界

$n=0$ 输出空行；含相同元素时，`sorted` 稳不稳定都不影响值序列。下标从 $1$ 开始时，剩余类改成 $i\bmod k$ 即可，结论相同。

## 追问

**直接整段 `sort(reverse=True)` 行吗？**
不行，那会跨过剩余类交换，排出来的数组不一定可达。

**链内升序排会怎样？**
得到的是字典序最小，方向反了。

**$k=0$ 怎么办？**
会除零。题目里 $k$ 是正数，代码对非正的 $k$ 直接原样返回。

**如果最多只能交换 $t$ 次呢？**
剩余类就不能任意重排了，要改成每条链上有限步的选择，那是另一题。

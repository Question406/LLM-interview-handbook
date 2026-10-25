---
id: lc-4-median-of-two-sorted-arrays
section: binary-search
order: 7
level: S
title: LC 4 · 寻找两个正序数组的中位数
quick: "在较短的数组上二分切点，让两个数组左侧合起来有 $(m+n+1)//2$ 个元素，并满足 $\\max(A_L,B_L)\\le \\min(A_R,B_R)$。总长度为奇数时取左侧最大值，偶数时取它和右侧最小值的平均。时间 $O(\\log(\\min(m,n)))$。"
tags:
  - Binary Search
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 4. 寻找两个正序数组的中位数
    url: https://leetcode.cn/problems/median-of-two-sorted-arrays/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定两个分别按非递减顺序排列的整数数组 nums1 和 nums2，长度分别为 m、n。求把两者的全部元素合在一起并排序后的中位数。总元素数为奇数时，中位数是中间那个值；为偶数时，是中间两个值的平均数。

### 接口与输出

实现 `findMedianSortedArrays(nums1: List[int], nums2: List[int]) -> float`。返回数值中位数，不需要构造或返回合并数组；目标时间复杂度为 `O(log(m+n))`。

### 合法输入与约束

`0 <= m,n <= 1000`，`1 <= m+n <= 2000`，元素范围为 `[-10^6,10^6]`。一个数组可以为空，但两个数组不会同时为空。

### 示例

```text
输入：nums1 = [1,3], nums2 = [2]
输出：2.00000
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/median-of-two-sorted-arrays/description/)。

## 解题思路与参考答案

## 题意

两个升序数组 `nums1`、`nums2`，长度 $m,n$。返回合并后的中位数。要求 $O(\log(m+n))$。

## 思路

我会在短数组上二分切点。中位数把全体切成左右两半，左半的个数是 $(m+n+1)//2$，而且左边最大值不超过右边最小值。所以只要在短数组上枚举切点 $i$，另一个数组的切点就跟着定了，$j = \mathrm{half}-i$。

往哪边收看交叉比较。$A_L > B_R$ 说明 $i$ 太大，往左收；$B_L > A_R$ 就往右收。某一侧切空了，用 $\pm\infty$ 补。奇数长度时中位数就是左半最大；偶数时再和右半最小取平均。

拿 `[1,3]` 和 `[2]` 走一遍。代码先交换，短数组是 `[2]`，长数组是 `[1,3]`，`half=2`。先试 $i=0$、$j=2$，短数组左边是空的，长数组左边是 1 和 3，$B_L=3$ 大于 $A_R=2$，往右收。再试 $i=1$、$j=1$，左边是 2 和 1，右边是 $+\infty$ 和 3，切法合法。总长是奇数，答案是左边最大值 2。

归并到中点也能做，但那是 $O(m+n)$，过不了 follow-up 的对数要求。

## 参考代码

```python
from typing import List


def findMedianSortedArrays(nums1: List[int], nums2: List[int]) -> float:
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    m, n = len(nums1), len(nums2)
    lo, hi = 0, m
    half = (m + n + 1) // 2
    while lo <= hi:
        i = (lo + hi) // 2
        j = half - i
        a_left = nums1[i - 1] if i else float("-inf")
        a_right = nums1[i] if i < m else float("inf")
        b_left = nums2[j - 1] if j else float("-inf")
        b_right = nums2[j] if j < n else float("inf")
        if a_left <= b_right and b_left <= a_right:
            if (m + n) % 2:
                return float(max(a_left, b_left))
            return (max(a_left, b_left) + min(a_right, b_right)) / 2.0
        if a_left > b_right:
            hi = i - 1
        else:
            lo = i + 1
    raise ValueError("empty input")


if __name__ == "__main__":
    assert findMedianSortedArrays([1, 3], [2]) == 2.0
    assert findMedianSortedArrays([1, 2], [3, 4]) == 2.5
    assert findMedianSortedArrays([], [1]) == 1.0
    assert findMedianSortedArrays([2], []) == 2.0
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
assert findMedianSortedArrays([1, 3], [2]) == 2.0
assert findMedianSortedArrays([1, 2], [3, 4]) == 2.5
assert findMedianSortedArrays([], [1]) == 1.0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(\log(\min(m,n)))$，额外空间 $O(1)$，满足 $O(\log(m+n))$ 的要求。

## 边界

一侧为空时，短数组的切点只能是 $0$，另一侧切在 `half`，中位数就是非空数组自己的中位数，代码用 $\pm\infty$ 补空侧。总长奇数时左半多一个，答案是 $\max(A_L, B_L)$；偶数再和 $\min(A_R, B_R)$ 平均。短数组的切点顶到 $0$ 或 $m$，表示中位数完全由长数组贡献，切空的那侧同样用 $\pm\infty$ 补。

## 追问

**两个有序数组的第 $k$ 小怎么求？**
每次比较两个数组各自的第 $k//2$ 个，较小那边的前缀不可能包含第 $k$ 小，整段丢掉，$k$ 减去丢掉的个数（$k$ 从 $1$ 计）。某一侧空了，直接取另一侧第 $k$ 个。时间 $O(\log(m+n))$。中位数就是第 $(m+n+1)//2$ 小，偶数时再和下一个平均。也可以用本题的划分做，把左半大小改成 $k$，切法合法时 $\max(A_L,B_L)$ 就是答案。

```python
def findKth(a, b, k):
    if len(a) > len(b):
        a, b = b, a
    if not a:
        return b[k - 1]
    if k == 1:
        return min(a[0], b[0])
    i = min(len(a), k // 2)
    j = k - i
    if a[i - 1] <= b[j - 1]:
        return findKth(a[i:], b, k - i)
    return findKth(a, b[j:], k - j)


def median_via_kth(a, b):
    n = len(a) + len(b)
    if n % 2:
        return float(findKth(a, b, n // 2 + 1))
    return (findKth(a, b, n // 2) + findKth(a, b, n // 2 + 1)) / 2.0
```

**数组没排序呢？**
最直接是先各自排序，$O(m\log m)$、$O(n\log n)$，再走本题，总时间被排序主导。如果只要中位数、又允许改原数组，可以把两个数组合成一块做快选，期望 $O(m+n)$ 选出第 $k$ 小，最坏 $O((m+n)^2)$。在线、不能改原数组、又要严格 $\log$ 的话，必须先有序。

```python
import random

def median_unsorted(a, b):
    nums = a + b
    k = (len(nums) - 1) // 2

    def select(lo, hi, kth):
        pivot = nums[random.randint(lo, hi)]
        i, j = lo, hi
        while i <= j:
            while nums[i] < pivot:
                i += 1
            while nums[j] > pivot:
                j -= 1
            if i <= j:
                nums[i], nums[j] = nums[j], nums[i]
                i, j = i + 1, j - 1
        if kth <= j:
            return select(lo, j, kth)
        if kth >= i:
            return select(i, hi, kth)
        return nums[kth]

    n = len(nums)
    if n % 2:
        return float(select(0, n - 1, k))
    return (select(0, n - 1, n // 2 - 1) + select(0, n - 1, n // 2)) / 2.0
```

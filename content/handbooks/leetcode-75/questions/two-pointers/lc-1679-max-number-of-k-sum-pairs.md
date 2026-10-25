---
id: lc-1679-max-number-of-k-sum-pairs
section: two-pointers
order: 4
level: A
title: LC 1679 · K 和数对的最大数目
quick: >-
  先排序，再用双指针从两端往中间收：和小了 `l` 右移，大了 `r` 左移，等于 `k` 就配一对、两边同时内收。这样是 $O(n\log n)$；换成计数哈希扫一遍，可以做到 $O(n)$ 时间、$O(n)$ 空间。
tags:
  - Array
  - Two Pointers
  - Hash
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1679. Max Number of K-Sum Pairs
    url: https://leetcode.com/problems/max-number-of-k-sum-pairs/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题目描述

给定整数数组 `nums` 和整数 k。一次操作可以选出数组中两个不同位置，要求这两个位置的数之和等于 k，然后把这两个元素都删除。每个原数组位置最多参与一次操作，即使数值相同也要按不同位置分别计算。求最多能够执行多少次操作。

### 输入与输出

实现 `maxOperations(nums, k) -> int`，返回最大操作次数，不需要返回所有数对或真的改写传入数组。两个被选元素不要求原本相邻；剩下无法配对的元素可以不使用。

### 约束

- `1 <= len(nums) <= 10^5`。
- `1 <= nums[i] <= 10^9`。
- `1 <= k <= 10^9`。

### 示例

```text
输入：nums = [1,2,3,4], k = 5
输出：2
```

[LeetCode 原题](https://leetcode.com/problems/max-number-of-k-sum-pairs/description/)

## 解题思路与参考答案

## 题意

一次操作从 `nums` 里删掉两个和为 `k` 的数。求最多能做多少次操作。每个元素只能用一次。$n \le 10^5$，$1 \le nums[i], k \le 10^9$。

## 思路

我会先排序再用双指针，因为排好序后每一步都能确定该丢掉哪个数，正确性好讲。这一节放在双指针下面，所以面试里我先写排序版，再补一个 $O(n)$ 的计数哈希版。

排序后 `l`、`r` 从两端出发。和小于 `k`，说明 `nums[l]` 配上当前最大的数都凑不够，和谁都配不上，丢掉 `l`。和大于 `k`，说明 `nums[r]` 配上最小的数都超了，丢掉 `r`。和等于 `k` 就直接配对，两边一起内收。直接配为什么不亏，可以用交换论证：如果最优方案里 `nums[l]` 配了别人，把它换成和 `nums[r]` 配，对数不会变少。

拿 `[3, 1, 3, 4, 3]`、$k=6$ 走一遍。排序后是 `[1, 3, 3, 3, 4]`。$1+4=5$ 小了，`l` 右移；$3+4=7$ 大了，`r` 左移；$3+3=6$ 配上一对，两边内收后 `l == r`，停下，答案是 $1$。

计数哈希版更快，放在追问里讲。

## 参考代码

```python
from typing import List


def maxOperations(nums: List[int], k: int) -> int:
    a = sorted(nums)
    l, r = 0, len(a) - 1
    ops = 0
    while l < r:
        s = a[l] + a[r]
        if s == k:
            ops += 1
            l += 1
            r -= 1
        elif s < k:
            l += 1
        else:
            r -= 1
    return ops


if __name__ == "__main__":
    assert maxOperations([1, 2, 3, 4], 5) == 2
    assert maxOperations([3, 1, 3, 4, 3], 6) == 1
    assert maxOperations([2, 2, 2, 2], 4) == 2
    assert maxOperations([1], 2) == 0
    assert maxOperations([5, 5, 5], 10) == 1
    assert maxOperations([1, 1, 1], 5) == 0
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert maxOperations([1, 2, 3, 4], 5) == 2
assert maxOperations([3, 1, 3, 4, 3], 6) == 1
assert maxOperations([2, 2, 2, 2], 4) == 2
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

排序版时间 $O(n\log n)$，额外空间 $O(n)$，花在 `sorted` 拷贝上；原地排序的话就是排序的栈空间。

## 边界

`k` 是偶数且有多个 `k/2` 时，比如 `[3,3,3]`、$k=6$，只能配一对，指针相遇就停下。

所有数都大于等于 `k` 时，正整数范围内两数之和必然超过 `k`，答案是 $0$。

只有一个元素时 `l == r`，根本不进循环。

## 追问

**能做到 $O(n)$ 吗？**
能，用计数哈希扫一遍。扫到 `x` 先查 `cnt[k - x]` 还有没有剩，有就配一对并减一，没有就 `cnt[x] += 1`。先查后记，同一个元素就不会和自己配。时间 $O(n)$，额外空间 $O(n)$。

```python
from collections import Counter


def maxOperations_hash(nums, k):
    cnt = Counter()
    ops = 0
    for x in nums:
        if cnt[k - x] > 0:
            cnt[k - x] -= 1
            ops += 1
        else:
            cnt[x] += 1
    return ops
```

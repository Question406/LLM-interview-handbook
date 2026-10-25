---
id: lc-219-contains-duplicate-ii
section: hashmap
order: 8
level: A
title: LC 219 · 存在重复元素 II
quick: >-
  用哈希记下每个值最近一次出现的下标。再遇到同一个值且 $i-j\le k$ 就返回真，不管命中与否都把下标更新成当前位置。时间 $O(n)$。
tags:
  - Hash
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 219. 存在重复元素 II
    url: https://leetcode.cn/problems/contains-duplicate-ii/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定整数数组 nums 和非负整数 k，判断是否存在两个不同的下标 i、j，使 `nums[i] == nums[j]`，并且它们在数组中的下标距离 `abs(i-j)` 不大于 k。

### 接口与输出

实现 `containsNearbyDuplicate(nums: List[int], k: int) -> bool`。存在任意一对就返回 True，否则返回 False；距离按位置差计算，不按两值之差计算。

### 合法输入与约束

`1 <= len(nums) <= 100000`，`-10^9 <= nums[i] <= 10^9`，`0 <= k <= 100000`。因为要求两个不同位置，k=0 时结果为 False。

### 示例

```text
输入：nums = [1,2,3,1], k = 3
输出：true
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/contains-duplicate-ii/description/)。

## 解题思路与参考答案

## 题意

判断是否存在一对下标 $i$、$j$，满足 `nums[i] == nums[j]` 且 $|i-j|\le k$。

## 思路

我会用哈希存「值 -> 最近一次的下标」。每个值只有最近那次出现有用，更早的同值离当前位置只会更远，不用保留全部历史。扫到 $x$ 时，如果表里有它并且 $i - last[x] \le k$，就返回真；不管有没有命中，都把 `last[x]` 更新成 $i$。

用 `[1,2,3,1]`、$k=3$ 走一遍：前三个数都是第一次出现，记下下标；扫到下标 3 的 1，上次出现在下标 0，距离 $3\le 3$，返回真。换成 `[1,2,3,1,2,3]`、$k=2$，每次重复的距离都是 3，一直不命中，返回假。

也可以维护一个长度为 $k+1$ 的滑动窗口集合，滑出窗口的值删掉。

## 参考代码

```python
from typing import List


def containsNearbyDuplicate(nums: List[int], k: int) -> bool:
    last = {}
    for i, x in enumerate(nums):
        if x in last and i - last[x] <= k:
            return True
        last[x] = i
    return False


if __name__ == "__main__":
    assert containsNearbyDuplicate([1, 2, 3, 1], 3) is True
    assert containsNearbyDuplicate([1, 0, 1, 1], 1) is True
    assert containsNearbyDuplicate([1, 2, 3, 1, 2, 3], 2) is False
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert containsNearbyDuplicate([1, 2, 3, 1], 3) is True
assert containsNearbyDuplicate([1, 0, 1, 1], 1) is True
assert containsNearbyDuplicate([1, 2, 3, 1, 2, 3], 2) is False
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(\min(n,k))$。最坏要记下全部不同的值。

## 边界

$k=0$ 恒为假，下标必须不同，而 $|i-j|\le 0$ 只能是同一个位置。数组没有重复直接返回假。重复刚好卡在 $i-j=k$ 时要返回真，所以用 $\le$，别写成 $\lt$。

## 追问

**不限距离，只问有没有重复（LC 217）呢？**
一遍放进 `set`，插入前已经在集合里就返回真；或者直接比较 `len(nums)` 和 `len(set(nums))`。时间 $O(n)$，空间 $O(n)$。本题的「最近下标哈希」也能做，只是多存了用不上的距离。如果白板强调 $O(1)$ 额外空间，就只能排序后扫相邻元素，时间变成 $O(n\log n)$，还会打乱原数组。

```python
def containsDuplicate(nums):
    return len(nums) != len(set(nums))
```

**改成值差不超过 $t$、下标差不超过 $k$（LC 220）呢？**
用桶。窗口里要找的变成了 $|nums[i]-nums[j]| \le t$ 且 $|i-j| \le k$。桶宽取 $w=t+1$，把 $x$ 放进桶号 $x//w$，同一个桶里任意两数的差一定 $\le t$；不在同一个桶的话，只需要看左右两个邻桶，差值 $\le t$ 才算命中。窗口大小保持 $k$，下标滑出时删掉对应的桶。时间 $O(n)$，空间 $O(\min(n,k))$。$t\lt 0$ 或 $k=0$ 直接返回假；Python 对负数的 `//` 是向下取整，桶号依然一致。对每个数暴力扫窗口是 $O(nk)$，太慢。

```python
def containsNearbyAlmostDuplicate(nums, k, t):
    if t < 0 or k <= 0:
        return False
    buckets = {}
    w = t + 1
    for i, x in enumerate(nums):
        bid = x // w
        if bid in buckets:
            return True
        if bid - 1 in buckets and abs(x - buckets[bid - 1]) < w:
            return True
        if bid + 1 in buckets and abs(x - buckets[bid + 1]) < w:
            return True
        buckets[bid] = x
        if i >= k:
            del buckets[nums[i - k] // w]
    return False
```

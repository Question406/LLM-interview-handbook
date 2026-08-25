---
id: lc-219-contains-duplicate-ii
section: hashmap
order: 8
level: A
title: LC 219 · 存在重复元素 II
quick: >-
  哈希记下每个值最近一次下标。再遇到同一值且 $i-j\le k$ 即真，并更新下标。时间
  $O(n)$。
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

## 题意

判断是否存在一对下标 $i$、$j$ 满足 `nums[i] == nums[j]` 且 $|i-j|\le k$。

## 思路

不需要记下全部历史下标：只要最近一次。哈希 `值 -> 最近下标`。扫到 $x$ 时，若表里已有且 $i - last[x] \le k$，返回真；无论是否命中都把 `last[x]` 更新为 $i$。更早的同值距离只会更大，不必保留。

等价写法：长度为 $k+1$ 的滑动窗口集合，窗口外的值删掉。

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

## 复杂度

时间 $O(n)$，额外空间 $O(\min(n,k))$。最坏记下全部不同值。

## 边界

- $k=0$ 恒假：下标必须不同，$|i-j|\le 0$ 只能是同一位置。
- 数组无重复直接假；重复刚好卡在 $i-j=k$ 时要返回真，用 $\le$ 不要写成 $\lt$。

## 追问

- **任意距离重复（LC 217）？** 丢掉 $k$ 限制，只问数组里有没有重复值。一遍放进 `set`，插入前已在集合里就真；或直接比较 `len(nums)` 与 `len(set(nums))`。时间 $O(n)$，空间 $O(n)$。本题的「最近下标哈希」也能做，只是多存了用不上的距离。白板若强调 $O(1)$ 额外空间，只能排序后扫相邻，时间变成 $O(n\log n)$，会打乱原数组。

```python
def containsDuplicate(nums):
    return len(nums) != len(set(nums))
```

- **值差不超过 $t$、下标差不超过 $k$（LC 220）？** 窗口里不再找「相等」，而找 $|nums[i]-nums[j]| \le t$ 且 $|i-j| \le k$。桶排序思想：桶宽 $w=t+1$，把 $x$ 放进桶号 $x//w$。同一桶内任意两数差一定 $\le t$；否则只需看左右邻桶，差值 $\le t$ 才算命中。窗口大小保持 $k$，下标滑出时删掉对应桶。时间 $O(n)$，空间 $O(\min(n,k))$。易错：$t\lt 0$ 或 $k=0$ 直接假；Python 负数 `//` 是向下取整，桶号仍然一致。不要对每个数暴力扫窗口，那是 $O(nk)$。

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

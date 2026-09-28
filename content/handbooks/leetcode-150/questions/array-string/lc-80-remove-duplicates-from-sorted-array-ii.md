---
id: lc-80-remove-duplicates-from-sorted-array-ii
section: array-string
order: 4
level: A
title: LC 80 · 删除有序数组中的重复项 II
quick: >-
  有序数组，每个值最多留两次。慢指针写入：`slow < 2` 或 `nums[slow-2] !=` 当前才写。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Array
  - Two Pointers
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 80. 删除有序数组中的重复项 II
    url: https://leetcode.cn/problems/remove-duplicates-from-sorted-array-ii/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

非递减数组 `nums`，原地删除，使每个元素最多出现两次。返回新长度 $k$，`nums[:k]` 仍非递减。

## 思路

LC 26 的推广：慢指针写保留段。当前值可以写入，当且仅当还没写满两个，或它与已写入的倒数第二个不同（`nums[slow-2] != nums[fast]`）。这样同一值最多连写两次。

不要边扫边计数当前重复次数再特判，容易写错边界。看已经写下的倒数第 $2$ 个就够。

## 参考代码

```python
from typing import List


def removeDuplicates(nums: List[int]) -> int:
    slow = 0
    for x in nums:
        if slow < 2 or nums[slow - 2] != x:
            nums[slow] = x
            slow += 1
    return slow


if __name__ == "__main__":
    a = [1, 1, 1, 2, 2, 3]
    k = removeDuplicates(a)
    assert k == 5 and a[:k] == [1, 1, 2, 2, 3]
    b = [0, 0, 1, 1, 1, 1, 2, 3, 3]
    k = removeDuplicates(b)
    assert k == 7 and b[:k] == [0, 0, 1, 1, 2, 3, 3]
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- 长度 $\lt 3$：`slow < 2` 始终成立，原样返回。
- 某值恰好两次：两次都能写；超过两次时 `nums[slow-2] == x`，多余的跳过。
- 全相同：前两个留下，后面全部丢弃，返回 $2$（长度 $1$ 则返回 $1$）。

## 追问

- **最多允许 $k$ 次？** 把阈值 $2$ 换成 $k$：`slow < k` 或 `nums[slow-k] != x` 才写入。含义是：已写下的倒数第 $k$ 个若仍等于当前值，再写就会出现 $k+1$ 次。有序保证相同值连在一起，所以只看 `slow-k` 就够。时间 $O(n)$，额外空间 $O(1)$。$k=1$ 就是 LC 26，独立卡见 `lc-26-remove-duplicates-from-sorted-array`。这块容易栽：写成 `slow-k+1` 或拿 `fast-k` 比较，以及 $k=0$ 要先定义（通常直接返回 $0$）。$k$ 大于数组长度时答案就是 $n$。

```python
def removeDuplicatesAtMostK(nums, k):
    slow = 0
    for x in nums:
        if slow < k or nums[slow - k] != x:
            nums[slow] = x
            slow += 1
    return slow
```

- **数组无序呢？** 不能再看 `slow-k`，因为相同值不一定相邻。若只要求每个值最多 $k$ 次、不在乎相对顺序：先排序再套上面写法，时间 $O(n\log n)$，额外空间取决于排序。若要保持第一次出现的相对顺序：用哈希计已写次数，`count[x] < k` 才写到 `slow`，时间 $O(n)$，额外空间 $O(U)$（$U$ 为不同值个数）。不要无序直接套 `nums[slow-2]`，会漏删不相邻的重复。原地覆盖时同样只认前缀 $k$ 个位置之后的新长度。

```python
def removeDuplicatesUnsorted(nums, k=2):
    seen = {}
    slow = 0
    for x in nums:
        c = seen.get(x, 0)
        if c < k:
            nums[slow] = x
            slow += 1
            seen[x] = c + 1
    return slow
```

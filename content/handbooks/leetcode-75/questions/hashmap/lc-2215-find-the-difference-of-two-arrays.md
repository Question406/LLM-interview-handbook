---
id: lc-2215-find-the-difference-of-two-arrays
section: hashmap
order: 1
level: A
title: LC 2215 · 找出两数组的不同
quick: >-
  两个数组各转成集合，`s1 - s2` 和 `s2 - s1` 就是答案，集合顺带完成去重。时间 $O(n+m)$，额外空间
  $O(n+m)$。
tags:
  - Array
  - Hash
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 2215. Find the Difference of Two Arrays
    url: https://leetcode.com/problems/find-the-difference-of-two-arrays/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

给两个整数数组 `nums1`、`nums2`，返回长度为 $2$ 的列表：`answer[0]` 是在 `nums1` 中出现、但不在 `nums2` 中出现的所有不同整数；`answer[1]` 反过来。每个列表内顺序任意。长度 $\le 1000$，值在 $[-1000, 1000]$。

## 思路

「不在另一个数组里」是成员查询，集合查询 $O(1)$。两边各建一个 `set`，做两次差集。集合同时处理了「不同整数」这个去重要求，`[1,2,3,3]` 里的 $3$ 只会输出一次。

暴力对每个元素扫另一个数组是 $O(nm)$，还要自己去重。

## 参考代码

```python
from typing import List


def findDifference(nums1: List[int], nums2: List[int]) -> List[List[int]]:
    s1, s2 = set(nums1), set(nums2)
    return [list(s1 - s2), list(s2 - s1)]


if __name__ == "__main__":
    def norm(ans):
        return [sorted(ans[0]), sorted(ans[1])]

    assert norm(findDifference([1, 2, 3], [2, 4, 6])) == [[1, 3], [4, 6]]
    assert norm(findDifference([1, 2, 3, 3], [1, 1, 2, 2])) == [[3], []]
    assert norm(findDifference([1, 2], [1, 2])) == [[], []]
    assert norm(findDifference([-1, 0], [0, 5])) == [[-1], [5]]
    print("ok")
```

## 复杂度

时间 $O(n+m)$，额外空间 $O(n+m)$。

## 边界

- 两数组元素集合相同：返回 `[[], []]`。
- 数组内部有重复：输出里只出现一次，集合天然去重。
- 负数和 $0$ 都合法，哈希不关心正负。

## 追问

- **两个数组都已排序，要求 $O(1)$ 额外空间（不计输出）？** 双指针归并：值小的一侧就是另一侧没有的，记下后跳过所有相同值；相等则两边一起跳过。时间 $O(n+m)$。

```python
def sortedDifference(a, b):
    i = j = 0
    only_a, only_b = [], []
    while i < len(a) or j < len(b):
        if j == len(b) or (i < len(a) and a[i] < b[j]):
            v = a[i]
            only_a.append(v)
            while i < len(a) and a[i] == v:
                i += 1
        elif i == len(a) or b[j] < a[i]:
            v = b[j]
            only_b.append(v)
            while j < len(b) and b[j] == v:
                j += 1
        else:
            v = a[i]
            while i < len(a) and a[i] == v:
                i += 1
            while j < len(b) and b[j] == v:
                j += 1
    return [only_a, only_b]
```

- **值域很小（本题 $[-1000, 1000]$）？** 可以用长度 $2001$ 的布尔数组代替哈希集合，下标偏移 $1000$，常数更小。

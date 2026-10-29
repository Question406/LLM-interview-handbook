---
id: lc-88-merge-sorted-array
section: array-string
order: 1
level: S
title: LC 88 · 合并两个有序数组
quick: >-
  从右往左填。`nums1` 尾部预留了 $n$ 个空位，用三个指针比较两边的末尾，谁大就写到最后，这样不会覆盖还没读的元素。时间 $O(m+n)$，额外空间
  $O(1)$。
tags:
  - Array
  - Two Pointers
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 88. 合并两个有序数组
    url: 'https://leetcode.cn/problems/merge-sorted-array/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定两个非递减整数序列，将它们合并为一个非递减序列，并把结果写回第一个数组。第一个数组已经预留了足够空间：它的前 m 个位置是有效元素，后 n 个位置只是占位。

### 输入与输出

实现 `merge(nums1, m, nums2, n) -> None`。`len(nums1)=m+n`，`nums2` 中的 n 个元素全部有效。函数不返回新数组，调用后的 `nums1` 应包含两个有效序列的全部元素及其重复次数。占位的零不能当成额外输入值。

### 约束

- `0 <= m,n <= 200`，`1 <= m+n <= 200`。
- 两个有效序列均非递减，元素范围为 `[-10^9,10^9]`。

### 示例

```text
输入：nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3
输出：[1,2,2,3,5,6]
```

最终结果是修改后的 nums1；其余占位空间不再单独保留。

## 解题思路与参考答案

## 题意

`nums1` 长度 $m+n$，前 $m$ 个有序，后 $n$ 个空位；`nums2` 长度 $n$ 且有序。把两者合并进 `nums1`，仍非递减。

## 思路

我会从尾巴往前填。`nums1` 的空位都在尾部，从右往左写不会盖掉还没比较的数；从左往右写就会覆盖 `nums1` 里还没比较的元素。三个指针 `i=m-1`、`j=n-1`、`k=m+n-1`，比较 `nums1[i]` 和 `nums2[j]`，较大的写进 `nums1[k]`，对应指针减一。

拿 `nums1=[1,2,3,0,0,0]`、`nums2=[2,5,6]` 走一遍。先比 3 和 6，6 写到末位；再比 3 和 5，写 5；3 和 2 比，3 大，写 3；然后 2 和 2 相等，取 `nums2` 的 2。这时 `nums2` 用完，循环停，前面的 `[1,2]` 本来就在原位，结果是 `[1,2,2,3,5,6]`。

所以循环只看 `j`。`j` 耗尽就可以停，`nums1` 前缀已经就位；`i` 先耗尽的话，循环会继续把 `nums2` 剩下那段拷进去。

## 参考代码

```python
from typing import List


def merge(nums1: List[int], m: int, nums2: List[int], n: int) -> None:
    i, j, k = m - 1, n - 1, m + n - 1
    while j >= 0:
        if i >= 0 and nums1[i] > nums2[j]:
            nums1[k] = nums1[i]
            i -= 1
        else:
            nums1[k] = nums2[j]
            j -= 1
        k -= 1


if __name__ == "__main__":
    a = [1, 2, 3, 0, 0, 0]
    merge(a, 3, [2, 5, 6], 3)
    assert a == [1, 2, 2, 3, 5, 6]
    b = [1]
    merge(b, 1, [], 0)
    assert b == [1]
    c = [0]
    merge(c, 0, [1], 1)
    assert c == [1]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
a = [1, 2, 3, 0, 0, 0]
merge(a, 3, [2, 5, 6], 3)
assert a == [1, 2, 2, 3, 5, 6]
b = [1]
merge(b, 1, [], 0)
assert b == [1]
c = [0]
merge(c, 0, [1], 1)
assert c == [1]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(m+n)$，额外空间 $O(1)$，每个元素最多被写一次。

## Edge Cases

$m=0$ 时 `nums1` 全是空位，循环会把 `nums2` 整段拷进去。$n=0$ 时 `j` 一开始就 $<0$，循环不进，前缀已经是答案。`nums2` 全小于或全大于 `nums1` 时，从右填会先耗尽一侧，另一侧要么原位不动，要么整段搬入。

## 追问

**不能原地改 `nums1` 呢？**
先把 `nums1[:m]` 拷到缓冲 `left`，再从左用双指针合并写回，时间仍是 $O(m+n)$，额外空间 $O(m)$。也可以新开一个 $m+n$ 的数组，最后整体赋回。从左直接往 `nums1` 写会覆盖还没比较的元素，所以要么像本题这样从右填，要么先把有效段拷走。

```python
def merge_with_buffer(nums1, m, nums2, n):
    left = nums1[:m]
    i = j = k = 0
    while i < m and j < n:
        if left[i] <= nums2[j]:
            nums1[k] = left[i]
            i += 1
        else:
            nums1[k] = nums2[j]
            j += 1
        k += 1
    nums1[k : k + (m - i)] = left[i:]
    nums1[k : k + (n - j)] = nums2[j:]
```

**链表版（LC 21）怎么做？**
链表没有尾部空位，没法从右填。用哨兵 `dummy` 和尾指针 `tail`，每次把较小的头结点接到 `tail` 后面，某条耗尽后把另一条整段接上。时间 $O(m+n)$，额外空间 $O(1)$。独立卡见 `lc-21-merge-two-sorted-lists`。

```python
def mergeTwoLists(l1, l2):
    dummy = ListNode(0)
    tail = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            tail.next, l1 = l1, l1.next
        else:
            tail.next, l2 = l2, l2.next
        tail = tail.next
    tail.next = l1 or l2
    return dummy.next
```

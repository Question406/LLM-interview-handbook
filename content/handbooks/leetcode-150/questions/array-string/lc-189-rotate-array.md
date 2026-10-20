---
id: lc-189-rotate-array
section: array-string
order: 6
level: A
title: LC 189 · 轮转数组
quick: >-
  先把 $k$ 对 $n$ 取模。三次反转：整体反转，再反转前 $k$，再反转后 $n-k$。时间 $O(n)$，额外空间
  $O(1)$。
tags:
  - Array
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 189. 轮转数组
    url: https://leetcode.cn/problems/rotate-array/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

把数组 `nums` 向右轮转 $k$ 步：每个元素右移 $k$ 位，超出尾部的回到开头。原地完成。

## 思路

先将步数化为 $k \bmod n$。右旋就是把最后 $k$ 个元素移到前面，其余元素接在后面。整体反转后两部分交换位置，但各自顺序也反了；再分别反转区间 $[0,k)$ 和 $[k,n)$，就恢复两部分内部的原顺序。

另开数组按 `(i+k)%n` 搬运再拷回，空间 $O(n)$，备选。环状替换也能 $O(1)$，但要处理环的个数，更容易写错。

## 参考代码

```python
from typing import List


def rotate(nums: List[int], k: int) -> None:
    n = len(nums)
    k %= n

    def reverse(lo: int, hi: int) -> None:
        while lo < hi:
            nums[lo], nums[hi] = nums[hi], nums[lo]
            lo += 1
            hi -= 1

    reverse(0, n - 1)
    reverse(0, k - 1)
    reverse(k, n - 1)


if __name__ == "__main__":
    a = [1, 2, 3, 4, 5, 6, 7]
    rotate(a, 3)
    assert a == [5, 6, 7, 1, 2, 3, 4]
    b = [-1, -100, 3, 99]
    rotate(b, 2)
    assert b == [3, 99, -1, -100]
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。每个元素被交换常数次。

## 边界

- $k=0$ 或 $k$ 是 $n$ 的倍数：取模后为 $0$，三次反转后回到原数组。
- $k \gt n$：必须先 $k \bmod n$，否则下标越界。
- $n=1$：怎么转都不变。

## 追问

- **向左轮转 $k$ 步？** 左旋 $k$ 等于右旋 $n-k$，可以直接复用本题三次反转。若按左旋自己写：先反转前 $k$ 个，再反转后 $n-k$ 个，最后整体反转。时间 $O(n)$，额外空间 $O(1)$。这块容易栽：还是要先取模；$k=0$ 时直接返回，避免 `reverse(0, -1)` 写崩。

```python
def rotate_left(nums, k):
    n = len(nums)
    k %= n
    if k == 0:
        return

    def reverse(lo, hi):
        while lo < hi:
            nums[lo], nums[hi] = nums[hi], nums[lo]
            lo += 1
            hi -= 1

    reverse(0, k - 1)
    reverse(k, n - 1)
    reverse(0, n - 1)
```

- **链表怎么转（LC 61）？** 链表不能按下标反转三次。先扫一遍得长度 $n$ 和尾指针，$k \bmod n$，若为 $0$ 直接返回。把尾接到头成环，再从原头走 $n-k-1$ 步到新尾，新头是它的后继，把新尾 `next` 置空。时间 $O(n)$，额外空间 $O(1)$。空表、单节点、以及成环后忘记断环，这块容易栽。独立卡见 `lc-61-rotate-list`。

```python
def rotateRight(head, k):
    if head is None or head.next is None or k == 0:
        return head
    n = 1
    tail = head
    while tail.next:
        tail = tail.next
        n += 1
    k %= n
    if k == 0:
        return head
    tail.next = head
    new_tail = head
    for _ in range(n - k - 1):
        new_tail = new_tail.next
    new_head = new_tail.next
    new_tail.next = None
    return new_head
```

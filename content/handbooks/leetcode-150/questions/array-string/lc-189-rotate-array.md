---
id: lc-189-rotate-array
section: array-string
order: 6
level: A
title: LC 189 · 轮转数组
quick: "先把 $k$ 对 $n$ 取模，再三次反转：整体反转，然后分别反转前 $k$ 个和后 $n-k$ 个。整体反转让两段换了位置，再各自反转一次就恢复内部顺序。时间 $O(n)$，额外空间 $O(1)$。"
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

## 题目描述

把整数数组向右轮转 k 步。每轮转一步，最后一个元素移动到最前面，其余元素右移一位；轮转后元素的循环顺序不变。

### 输入与输出

实现 `rotate(nums, k) -> None`，直接修改传入的 `nums`。答案是修改后的数组，不是函数返回的新数组。

### 约束与约定

- `1 <= len(nums) <= 100000`，元素在 32 位有符号整数范围内。
- `0 <= k <= 100000`；k 可以为 0，也可以大于数组长度。
- 要求原地修改；进阶要求只使用常数额外空间。

### 示例

```text
输入：nums = [1,2,3,4,5,6,7], k = 3
输出：[5,6,7,1,2,3,4]
```

示例的输出表示调用后 nums 的内容；函数本身返回 None。

[官方原题与完整题面](https://leetcode.com/problems/rotate-array/description/)。

## 解题思路与参考答案

## 题意

把数组 `nums` 向右轮转 $k$ 步：每个元素右移 $k$ 位，超出尾部的回到开头。原地完成。

## 思路

我会用三次反转，它是原地的，写起来也不容易错。先把步数化成 $k \bmod n$。右旋就是把最后 $k$ 个元素挪到前面、其余接在后面；整体反转之后两部分正好换了位置，只是各自顺序也反了，再分别反转区间 $[0,k)$ 和 $[k,n)$，内部顺序就恢复了。

拿 `[1, 2, 3, 4, 5, 6, 7]`、$k=3$ 走一遍：整体反转得 `[7, 6, 5, 4, 3, 2, 1]`，反转前三个得 `[5, 6, 7, 4, 3, 2, 1]`，再反转后四个得 `[5, 6, 7, 1, 2, 3, 4]`。

另开数组按 `(i+k)%n` 搬运再拷回，空间是 $O(n)$，可以当备选。环状替换也能做到 $O(1)$，但要处理环的个数，更容易写错。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
a = [1, 2, 3, 4, 5, 6, 7]
rotate(a, 3)
assert a == [5, 6, 7, 1, 2, 3, 4]
b = [-1, -100, 3, 99]
rotate(b, 2)
assert b == [3, 99, -1, -100]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。每个元素被交换常数次。

## 边界

$k=0$ 或 $k$ 是 $n$ 的倍数时，取模后为 $0$，三次反转后回到原数组。$k \gt n$ 时一定要先 $k \bmod n$，否则下标越界。$n=1$ 怎么转都不变。

## 追问

**向左轮转 $k$ 步呢？**
左旋 $k$ 等于右旋 $n-k$，可以直接复用本题。要自己写的话，先反转前 $k$ 个，再反转后 $n-k$ 个，最后整体反转。时间 $O(n)$，额外空间 $O(1)$。同样要先取模，$k=0$ 时直接返回，免得 `reverse(0, -1)` 写崩。

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

**链表怎么转（LC 61）？**
链表没法按下标反转三次，我会先成环再断开。先扫一遍拿到长度 $n$ 和尾指针，$k \bmod n$ 为 $0$ 就直接返回；否则把尾接到头成环，从原头走 $n-k-1$ 步到新尾，新头是它的后继，再把新尾的 `next` 置空。时间 $O(n)$，额外空间 $O(1)$。空表、单节点、成环后忘了断环，这三处最容易出错。独立卡见 `lc-61-rotate-list`。

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

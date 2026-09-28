---
id: lc-283-move-zeroes
section: two-pointers
order: 1
level: S
title: LC 283 · 移动零
quick: >-
  写指针 `w` 指向下一个非零该放的位置，读指针遇到非零就和 `w` 交换并前移。非零相对顺序不变，零被挤到末尾。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Array
  - Two Pointers
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 283. Move Zeroes
    url: https://leetcode.com/problems/move-zeroes/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

原地把数组里所有 $0$ 移到末尾，非零元素保持原有相对顺序。不能拷贝数组，函数无返回值。长度到 $10^4$。

## 思路

快慢指针：`w` 左边全是已处理好的非零数，`[w, i)` 全是 $0$。读指针 `i` 扫到非零时，和 `nums[w]` 交换，`w += 1`。交换把一个 $0$ 换到 `i` 的位置，区间不变式保持，扫完后 $0$ 都在尾部。

另一种写法是先把非零依次覆盖到前面，最后把 `[w, n)` 填 $0$，写操作次数相近。每遇到一个 $0$ 就把后面整体左移是 $O(n^2)$，面试会被追问。

## 参考代码

```python
from typing import List


def moveZeroes(nums: List[int]) -> None:
    w = 0
    for i in range(len(nums)):
        if nums[i] != 0:
            nums[w], nums[i] = nums[i], nums[w]
            w += 1


if __name__ == "__main__":
    def run(a):
        moveZeroes(a)
        return a

    assert run([0, 1, 0, 3, 12]) == [1, 3, 12, 0, 0]
    assert run([0]) == [0]
    assert run([1, 2, 3]) == [1, 2, 3]
    assert run([0, 0, 1]) == [1, 0, 0]
    assert run([4, 0, -2, 0, 0, 5]) == [4, -2, 5, 0, 0, 0]
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。

## 边界

- 没有 $0$：每次都是 `w == i` 的自交换，数组不变。
- 全是 $0$：`w` 一直是 $0$，不做任何交换。
- 负数不是 $0$：判断用 `!= 0`，别写成 `> 0`。

## 追问

- **尽量减少写操作？** `w == i` 时跳过交换，前缀全非零的数组就零写入。总写次数不超过非零个数的两倍。

```python
def moveZeroes_fewer_writes(nums):
    w = 0
    for i, x in enumerate(nums):
        if x != 0:
            if i != w:
                nums[w], nums[i] = x, 0
            w += 1
```

- **把「移动零」换成「移除等于 `val` 的元素并返回新长度」（LC 27）？** 同一个写指针模板：不等于 `val` 就写到 `w`，返回 `w`。不需要保留尾部内容，所以直接覆盖，不必交换。

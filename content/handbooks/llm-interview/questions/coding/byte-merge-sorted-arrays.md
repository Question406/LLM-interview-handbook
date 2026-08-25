---
id: byte-merge-sorted-arrays
section: coding
order: 210
level: A
title: 字节实习一面：合并两个有序数组（原地 / 双指针）
quick: >-
  从尾部双指针填，避免覆盖未读元素；复杂度 O(m+n)、额外空间 O(1)。先说清 nums1
  预留尾部空间，再写边界：某一侧耗尽时只拷另一侧。
tags:
  - ByteDance
  - Coding
  - Two Pointers
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 字节实习 agent开发一面
    url: https://www.nowcoder.com/feed/main/detail/931a8a935a5e4b4f8d0b71cd4e818604
    type: candidate-first-hand
---

## 真题 / 考点说明

- 公司：字节跳动
- 岗位：Agent 开发实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“手撕：合并两个有序数组”**（同场还有 ReAct 选工具、Recall@5）

标准 LeetCode 88：`nums1` 长度 $m+n$，后 $n$ 格是空位。从后往前比，才能原地且不覆盖未读元素。若不能改 `nums1`，新开数组再拷回。和 Agent 题连着考时，别只写代码不讲复杂度。

## 思路

三指针：`i=m-1` 扫 `nums1` 有效段，`j=n-1` 扫 `nums2`，`k=m+n-1` 从尾巴填。谁大填谁，填完该侧指针减一。`j` 耗尽即可停，`nums1` 前缀已经在正确位置。`i` 先耗尽则把 `nums2` 剩下的拷进去。

从前往后会覆盖 `nums1` 里还没比较的数，除非先另开缓冲。

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

## 复杂度

时间 $O(m+n)$，额外空间 $O(1)$。从前往后 + 新数组也是 $O(m+n)$ 时间，但多 $O(m+n)$ 空间。

## 边界与追问

1. `n=0` 原数组不动；`m=0` 整段拷 `nums2`；一侧整体更小/更大。
2. 追问链表版（21）：还是双指针，但要哑头；不必从后往前。追问 $k$ 路归并用堆，$O(N\log k)$。
3. 同场 Recall@5 / ReAct：合并写完补一句复杂度，再切工具题，避免在 $O(1)$ 空间上卡太久。

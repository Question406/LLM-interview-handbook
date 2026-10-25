---
id: byte-merge-sorted-arrays
section: coding
order: 210
level: A
title: 字节实习一面：合并两个有序数组（原地 / 双指针）
quick: "从尾部用双指针往前填：nums1 后面预留了 n 个空位，谁大就把谁放到最后，这样不会覆盖还没读的元素。nums2 用完就可以停，nums1 先用完就把 nums2 剩下的拷过去。时间 O(m+n)，额外空间 O(1)。"
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

## 题目描述

给定两个非递减整数数组的有效部分，把第二个数组合并进第一个数组预留的空间，合并后仍按非递减顺序排列。

### 接口与约束

实现 `merge(nums1, m, nums2, n) -> None`。`nums1` 的长度为 `m+n`，前 m 项才是有效数据，后 n 项只是可写空间，不能把其中的占位零当成待合并数据；`nums2` 的长度为 n，全部有效。m 或 n 可以为 0，两个有效部分均已排序，允许重复值。

必须直接修改 nums1，使它包含两段输入的所有元素及其重复次数；不返回新数组，也不要求改变 nums2。练习要求使用常数级辅助空间。

### 示例

```text
nums1 = [1,2,3,0,0,0], m = 3
nums2 = [2,5,6], n = 3
merge(nums1,m,nums2,n) -> None
调用后 nums1 = [1,2,2,3,5,6]

nums1 = [0], m = 0, nums2 = [1], n = 1
调用后 nums1 = [1]
```

本卡把相应算法考点统一为上述 Python 原地接口。

## 解题思路与参考答案

我会从尾部往前填：`nums1` 总长 $m+n$，后 $n$ 格是空位，两个指针分别从两个数组的有效末尾往前比，谁大就把谁放进 `nums1` 的最后一个空位。从后往前填，写入的位置永远在还没读的元素后面，所以能原地合并，也不会覆盖。

比如 `nums1 = [1,2,3,0,0,0]`、`nums2 = [2,5,6]`。从前往后填的话，填到第三格时要写入 `nums2` 的 2，正好盖掉 `nums1` 里还没比较的 3，除非先开一块缓冲；从后往前，先放 6，再放 5，再比 3 和 2，空位一直够用。

## 思路

用三个指针：`i=m-1` 扫 `nums1` 的有效段，`j=n-1` 扫 `nums2`，`k=m+n-1` 从尾巴开始填。谁大填谁，填完那一侧的指针减一。`j` 用完就可以停，`nums1` 剩下的前缀本来就在正确位置；`i` 先用完，就把 `nums2` 剩下的拷进去。如果题目不让改 `nums1`，就新开一个数组合并完再拷回。

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

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert a == [1, 2, 2, 3, 5, 6]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 复杂度

时间 $O(m+n)$，额外空间 $O(1)$。从前往后加一个新数组也是 $O(m+n)$ 的时间，但多花 $O(m+n)$ 空间。

## 边界与追问

**要测哪些边界？**
`n=0` 时原数组不动；`m=0` 时整段拷 `nums2`；还有一侧整体比另一侧小或者大的情况。

**换成链表版（21）呢？**
还是双指针，加一个哑头，不用从后往前。追问 $k$ 路归并的话用堆，复杂度 $O(N\log k)$。

**和 Agent 题一起考怎么安排时间？**
这一场后面还有 Recall@5 和 ReAct 选工具。合并写完补一句复杂度就切到工具题，别在 $O(1)$ 空间上卡太久。

## 真题 / 考点说明

这题来自字节跳动 Agent 开发实习一面的牛客候选人原帖，可信度 A，原话是 **“手撕：合并两个有序数组”**（同一场还有 ReAct 选工具、Recall@5）。就是标准的 LeetCode 88。

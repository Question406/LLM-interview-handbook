---
id: lc-26-remove-duplicates-from-sorted-array
section: array-string
order: 3
level: S
title: LC 26 · 删除有序数组中的重复项
quick: >-
  数组有序，相同元素一定相邻，所以用快慢指针原地写：当前值和已写入的最后一个不同才写入，最后返回慢指针，就是新长度。时间 $O(n)$，额外空间
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
  - title: 26. 删除有序数组中的重复项
    url: 'https://leetcode.cn/problems/remove-duplicates-from-sorted-array/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定一个已经按非递减顺序排列的整数数组，在原数组中去除重复值，使每个不同的值只保留一次，并维持非递减顺序。不要创建另一个数组作为最终结果。

### 输入与输出

实现 `removeDuplicates(nums: List[int]) -> int`。返回不同值的个数 `k`，并使调用后的 `nums[:k]` 恰好是去重结果；下标 `k` 之后的内容不参与判定。

### 约束

- `1 <= len(nums) <= 3 * 10^4`，`-100 <= nums[i] <= 100`。
- 输入已经非递减排序；要求使用常数额外空间。

### 示例

```text
输入：nums = [1,1,2]
输出：2, nums = [1,2,_]
```

返回值 2 表示只检查前两个位置 `[1,2]`；示例中的 `_` 表示该位置的值无关紧要，不是要写入数组的字符。

## 解题思路与参考答案

## 题意

非递减数组 `nums`，原地删掉重复项，每个值只留一次。返回新长度 $k$，并保证 `nums[:k]` 仍非递减且无重复。

## 思路

我用快慢指针。有序保证了重复段是连续的，只要和已写入的最后一个值比，就知道是不是重复。`slow` 指向下一个可写位置，`fast` 扫全数组，`nums[fast] != nums[slow-1]` 时写入并推进 `slow`。第一个元素一定保留，从下标 $1$ 开始比就行。

拿 `[1, 1, 2]` 走一遍：`slow` 从 $1$ 开始；第二个 $1$ 和 `nums[0]` 相同，跳过；$2$ 不同，写到下标 $1$，`slow` 变成 $2$，返回 $2$，前缀是 `[1, 2]`。

用哈希去重要 $O(n)$ 空间，还会打乱顺序；有序才能 $O(1)$ 原地。

## 参考代码

```python
from typing import List


def removeDuplicates(nums: List[int]) -> int:
    if not nums:
        return 0
    slow = 1
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow - 1]:
            nums[slow] = nums[fast]
            slow += 1
    return slow


if __name__ == "__main__":
    a = [1, 1, 2]
    k = removeDuplicates(a)
    assert k == 2 and a[:k] == [1, 2]
    b = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
    k = removeDuplicates(b)
    assert k == 5 and b[:k] == [0, 1, 2, 3, 4]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
a = [1, 1, 2]
k = removeDuplicates(a)
assert k == 2 and a[:k] == [1, 2]
b = [0, 0, 1, 1, 1, 2, 2, 3, 3, 4]
k = removeDuplicates(b)
assert k == 5 and b[:k] == [0, 1, 2, 3, 4]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。一次扫描。

## Edge Cases

长度为 $1$ 没有重复可删，返回 $1$。全部相同只留一个，返回 $1$。全部不同时 `slow` 每次都写，返回 $n$。

## 追问

**每个值最多保留两次呢（LC 80）？**
还是慢指针原地写，只是改成和 `nums[slow - 2]` 比：不同才写入，前两个名额还没占满（`slow < 2`）时也写。有序保证相同值相邻，所以和倒数第 $2$ 个已写入的比，就知道这个值已经留了几次。时间 $O(n)$，额外空间 $O(1)$。写成 `slow - 1` 就退化成本题的只留一次。独立卡见 `lc-80-remove-duplicates-from-sorted-array-ii`。

```python
def removeDuplicates_at_most_two(nums):
    slow = 0
    for x in nums:
        if slow < 2 or x != nums[slow - 2]:
            nums[slow] = x
            slow += 1
    return slow
```

**数组无序呢？**
有序是 $O(1)$ 原地的前提。无序又要去重、保持相对顺序的话，就用哈希记录出现过的值，慢指针只写第一次出现的，时间 $O(n)$，额外空间 $O(n)$。允许打乱顺序时，可以先排序再走本题的指针，时间 $O(n\log n)$，额外空间 $O(1)$。无序还硬套 `nums[slow - 1]` 的话，不相邻的重复会漏掉。

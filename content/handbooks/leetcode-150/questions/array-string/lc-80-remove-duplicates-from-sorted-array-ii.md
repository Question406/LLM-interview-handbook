---
id: lc-80-remove-duplicates-from-sorted-array-ii
section: array-string
order: 4
level: A
title: LC 80 · 删除有序数组中的重复项 II
quick: >-
  用快慢指针，慢指针指向下一个写入位置。前两个直接写，之后只有当前值和 `nums[slow-2]` 不同才写，这样每个值最多留两次。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Array
  - Two Pointers
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 80. 删除有序数组中的重复项 II
    url: 'https://leetcode.cn/problems/remove-duplicates-from-sorted-array-ii/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定已经按非递减顺序排列的整数数组 `nums`，原地删除多余的重复项，使每个不同的整数最多保留两次，并保持保留元素的相对顺序。若某个数原本只出现一次，则保留一次。

### 输入与输出

实现 `removeDuplicates(nums) -> int`，返回有效长度 k。调用后，`nums[:k]` 必须恰好是要求的结果；下标 k 之后的内容不作要求。不能另建一个与输入同规模的结果数组替代原地修改，额外空间要求 O(1)。

### 约束

- `1 <= len(nums) <= 3 * 10^4`。
- `-10^4 <= nums[i] <= 10^4`。
- 输入保证已经非递减排序。

### 示例

```text
输入：nums = [1,1,1,2,2,3]
输出：5, nums = [1,1,2,2,3,_]
```

[LeetCode 原题](https://leetcode.com/problems/remove-duplicates-from-sorted-array-ii/description/)

## 解题思路与参考答案

## 题意

非递减数组 `nums`，原地删除，使每个元素最多出现两次。返回新长度 $k$，`nums[:k]` 仍非递减。

## 思路

我会用快慢指针，这题就是 LC 26 的推广。慢指针 `slow` 指向保留段的下一个写入位置，快指针往后扫。当前值能不能写，只看已经写下的倒数第二个：还没写满两个，或者它和倒数第二个不同（`nums[slow-2] != nums[fast]`），就写进去。同一个值因此最多连写两次。

拿 `[1,1,1,2,2,3]` 走一遍。前两个 1 直接写，`slow` 到 2。第三个 1 和 `nums[0]` 相同，跳过。接着 2 和 `nums[0]=1` 不同，写到下标 2；第二个 2 和 `nums[1]=1` 不同，也写；3 和 `nums[2]=2` 不同，写。最后 `slow=5`，前缀是 `[1,1,2,2,3]`。

边扫边数当前值重复了几次再特判也能做，但 edge cases 容易写错，看已经写下的倒数第 $2$ 个就够了。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
a = [1, 1, 1, 2, 2, 3]
k = removeDuplicates(a)
assert k == 5 and a[:k] == [1, 1, 2, 2, 3]
b = [0, 0, 1, 1, 1, 1, 2, 3, 3]
k = removeDuplicates(b)
assert k == 7 and b[:k] == [0, 0, 1, 1, 2, 3, 3]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

每个元素看一次，时间 $O(n)$，额外空间 $O(1)$。

## Edge Cases

长度 $\lt 3$ 时 `slow < 2` 始终成立，数组原样返回。某个值恰好出现两次，两次都能写；超过两次时 `nums[slow-2] == x`，多出来的会被跳过。全相同的数组只留前两个，返回 $2$，长度为 $1$ 时返回 $1$。

## 追问

**如果最多允许 $k$ 次呢？**
把阈值 $2$ 换成 $k$ 就行，`slow < k` 或 `nums[slow-k] != x` 才写入。道理是已写下的倒数第 $k$ 个如果还等于当前值，再写就会出现 $k+1$ 次；数组有序，相同值连在一起，所以只看 `slow-k` 就够。时间 $O(n)$，额外空间 $O(1)$。$k=1$ 就是 LC 26，独立卡见 `lc-26-remove-duplicates-from-sorted-array`。这里容易写错的是写成 `slow-k+1`，或者拿 `fast-k` 去比；$k=0$ 也要先定义，通常直接返回 $0$。$k$ 大于数组长度时，答案就是 $n$。

```python
def removeDuplicatesAtMostK(nums, k):
    slow = 0
    for x in nums:
        if slow < k or nums[slow - k] != x:
            nums[slow] = x
            slow += 1
    return slow
```

**数组无序怎么办？**
那就不能再看 `slow-k` 了，相同值不一定相邻，直接套 `nums[slow-2]` 会漏删不相邻的重复。如果只要求每个值最多 $k$ 次、不在乎相对顺序，先排序再套上面的写法，时间 $O(n\log n)$，额外空间取决于排序。要保持第一次出现的相对顺序，就用哈希记每个值已经写了几次，`count[x] < k` 才写到 `slow`，时间 $O(n)$，额外空间 $O(U)$，$U$ 是不同值的个数。原地覆盖时，和原题一样只认返回的新长度之前那段前缀。

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

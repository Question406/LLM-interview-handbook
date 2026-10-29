---
id: lc-2215-find-the-difference-of-two-arrays
section: hashmap
order: 1
level: A
title: LC 2215 · 找出两数组的不同
quick: 两个数组各转成集合，`s1 - s2` 和 `s2 - s1` 就是答案，集合顺带完成去重。时间 $O(n+m)$，额外空间 $O(n+m)$。
tags:
  - Array
  - Hash
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 2215. Find the Difference of Two Arrays
    url: 'https://leetcode.com/problems/find-the-difference-of-two-arrays/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定两个整数数组 `nums1` 和 `nums2`，找出各自独有的不同整数。第一组包含在 nums1 中出现、但在 nums2 中完全没有出现的值；第二组反过来。输入中的重复值，在所属结果列表中也只保留一次。

### 输入与输出

实现 `findDifference(nums1, nums2) -> List[List[int]]`，返回恰有两个列表的结果：第0组对应 nums1 独有值，第1组对应 nums2 独有值。每组内部的元素顺序可以任意，外层两组的含义不能交换。

### 约束

- `1 <= len(nums1), len(nums2) <= 1000`。
- 两个数组中的元素值均在 -1000 到 1000 之间。

### 示例

```text
输入：nums1 = [1,2,3], nums2 = [2,4,6]
输出：[[1,3],[4,6]]
```

[LeetCode 原题](https://leetcode.com/problems/find-the-difference-of-two-arrays/description/)

## 解题思路与参考答案

## 题意

给两个整数数组 `nums1`、`nums2`，返回长度为 $2$ 的列表：`answer[0]` 是在 `nums1` 中出现、但不在 `nums2` 中出现的所有不同整数；`answer[1]` 反过来。每个列表内顺序任意。长度 $\le 1000$，值在 $[-1000, 1000]$。

## 思路

「不在另一个数组里」是成员查询，我用集合，查询 $O(1)$。两边各建一个 `set`，做两次差集。集合同时满足了「不同整数」这个去重要求，`[1,2,3,3]` 里的 $3$ 只会输出一次。

拿 `[1,2,3]` 和 `[2,4,6]` 看：`s1 - s2` 是 $\{1,3\}$，`s2 - s1` 是 $\{4,6\}$，答案 `[[1,3],[4,6]]`。

暴力做法是对每个元素扫一遍另一个数组，$O(nm)$，还得自己去重。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

如果题目允许答案以任意顺序返回，先排序或转成集合再比较；只有题目保证没有重复结果时才适合直接用集合，否则还要检查重复次数。

```python
def norm(ans):
    return [sorted(ans[0]), sorted(ans[1])]


assert norm(findDifference([1, 2, 3], [2, 4, 6])) == [[1, 3], [4, 6]]
assert norm(findDifference([1, 2, 3, 3], [1, 1, 2, 2])) == [[3], []]
assert norm(findDifference([1, 2], [1, 2])) == [[], []]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n+m)$，额外空间 $O(n+m)$。

## Edge Cases

两个数组的元素集合相同时，返回 `[[], []]`。

数组内部有重复，输出里也只出现一次，集合天然去重。

负数和 $0$ 都合法，哈希不关心正负。

## 追问

**两个数组都已排序，要求 $O(1)$ 额外空间（不计输出）呢？**
用双指针归并：值小的一侧就是另一侧没有的，记下来后跳过所有相同值；两边相等就一起跳过。时间 $O(n+m)$。

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

**值域很小怎么优化（本题 $[-1000, 1000]$）？**
可以用长度 $2001$ 的布尔数组代替哈希集合，下标偏移 $1000$，常数更小。

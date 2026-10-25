---
id: lc-128-longest-consecutive-sequence
section: hashmap
order: 9
level: S
title: LC 128 · 最长连续序列
quick: >-
  先把所有数放进集合，只从每段的左端点开始数：$x-1$ 不在集合里，才向右数 $x,x+1,\ldots$。非起点直接跳过，每个数最多被数一次，时间 $O(n)$。
tags:
  - Hash
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 128. 最长连续序列
    url: https://leetcode.cn/problems/longest-consecutive-sequence/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定一个没有排序的整数数组，找出其中能够组成的最长连续整数序列，返回该序列的长度。连续要求数值依次相差 1，不要求这些数在原数组中相邻或按顺序出现；重复的值不能增加连续序列长度。

### 输入与输出

实现 `longestConsecutive(nums) -> int`。只返回长度，不需要返回数列；空数组返回 0。

### 约束与约定

- `0 <= len(nums) <= 100000`。
- 每个数在 `[-1000000000,1000000000]`。
- 原题要求 `O(n)` 时间复杂度。

### 示例

```text
输入：nums = [100,4,200,1,3,2]
输出：4
```

示例可组成连续数列 [1,2,3,4]，长度为 4。

[官方原题与完整题面](https://leetcode.com/problems/longest-consecutive-sequence/description/)。

## 解题思路与参考答案

## 题意

在未排序数组里找最长连续整数序列的长度。这些数在数组里不用相邻，值连续就行。要求 $O(n)$。

## 思路

排序再扫是 $O(n\log n)$。要做到 $O(n)$，我会用哈希集合，只从每段的左端点往右数。先把所有数丢进 `set`，枚举 $x$ 时，只有 $x-1$ 不在集合里，$x$ 才是一段的起点，这时 `while x+len in set` 向右延伸；不是起点就跳过。

以 `[100,4,200,1,3,2]` 为例：4、3、2 都有前一个数，跳过；1 前面没有 0，是起点，向右数到 1、2、3、4，长度是 $4$；100 和 200 各自是长度 $1$ 的段。答案是 $4$。

非起点不进内层循环，所以每个数最多在内层被访问一次。重复数字进集合时就去掉了，不影响长度。

## 参考代码

```python
from typing import List


def longestConsecutive(nums: List[int]) -> int:
    s = set(nums)
    best = 0
    for x in s:
        if x - 1 not in s:
            y = x
            while y in s:
                y += 1
            best = max(best, y - x)
    return best


if __name__ == "__main__":
    assert longestConsecutive([100, 4, 200, 1, 3, 2]) == 4
    assert longestConsecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9
    assert longestConsecutive([]) == 0
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert longestConsecutive([100, 4, 200, 1, 3, 2]) == 4
assert longestConsecutive([0, 3, 7, 2, 5, 8, 4, 6, 0, 1]) == 9
assert longestConsecutive([]) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(n)$。外层跳过非起点，内层每个元素最多访问一次。

## 边界

空数组答案是 $0$，$[1]$ 答案是 $1$。全部相同时集合去重后只剩一个起点，长度是 $1$。有负数和 $0$ 也没关系，连续看的是值，和下标无关。

## 追问

**要输出具体的序列，长度不够用，怎么改？**
扫描时除了长度 `best`，再记下这段的起点 `best_start`。还是只在 $x-1$ 不在集合时才向右延伸，和求长度同一套 $O(n)$。最后用 `range(best_start, best_start + best_len)` 展开就行。如果有好几段一样长，题面没要求就返回任意一段。重复数字已经被 `set` 去掉，展开时不会出现重复值。

```python
def longestConsecutiveSeq(nums):
    s = set(nums)
    best_start = best_len = 0
    for x in s:
        if x - 1 not in s:
            y = x
            while y in s:
                y += 1
            if y - x > best_len:
                best_start, best_len = x, y - x
    return list(range(best_start, best_start + best_len))
```

**并查集怎么做？**
每个数先自成一个连通块，如果 $x-1$ 或 $x+1$ 已经出现过，就把相邻的值 `union` 起来，根上维护块的大小，答案取最大的 `size`。时间仍是摊还 $O(n)$，但要写 `find`/`union`，常数和代码量都更大。最容易错的是重复数字别二次 `union`，否则 size 会翻倍。白板上我优先讲哈希集合从左端点延伸，并查集当作「换一种连通块建模」的加分项。

```python
def longestConsecutiveUF(nums):
    parent, size = {}, {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        parent[rb] = ra
        size[ra] += size[rb]

    for x in nums:
        if x in parent:
            continue
        parent[x] = x
        size[x] = 1
        if x - 1 in parent:
            union(x, x - 1)
        if x + 1 in parent:
            union(x, x + 1)
    return max(size.values(), default=0)
```

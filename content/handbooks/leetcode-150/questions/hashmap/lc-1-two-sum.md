---
id: lc-1-two-sum
section: hashmap
order: 6
level: S
title: LC 1 · 两数之和
quick: >-
  一遍哈希：边扫边把「值 $\to$ 下标」存进表，扫到 $x$ 时先查 complement $= target - x$
  在不在表里，在就直接返回两个下标。先查再写，同一个元素不会被用两次，时间 $O(n)$。
tags:
  - Hash
  - Easy
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 1. 两数之和
    url: 'https://leetcode.cn/problems/two-sum/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定整数数组 nums 和目标整数 target，找出两个不同位置，使这两个位置上的值之和恰好等于 target。输入保证恰好有一组满足要求的位置对。

### 接口与输出

实现 `twoSum(nums: List[int], target: int) -> List[int]`，返回两个 0-based 下标，顺序不限。不能重复使用同一个位置；相同数值出现在两个不同位置时，可以分别使用。

### 合法输入与约束

`2 <= len(nums) <= 10000`，`-10^9 <= nums[i], target <= 10^9`。返回的是下标，不是两个元素值。

### 示例

```text
输入：nums = [2,7,11,15], target = 9
输出：[0,1]
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/two-sum/description/)。

## 解题思路与参考答案

## 题意

在数组里找两个不同下标 $i$、$j$，使 `nums[i] + nums[j] = target`。保证恰好有一组解，返回的是下标，不是值。

## 思路

我会用一遍哈希，要返回的是下标，排序会把下标打乱。扫到 $x$ 时先查 $target - x$ 是否已经在表里，在就返回「旧下标、当前下标」；不在就把 $x$ 的下标写进去。

拿 `[2,7,11,15]`、$target=9$ 走一遍：扫到 2，要找 7，表里没有，记下 `2 -> 0`；扫到 7，要找 2，表里有，返回 `[0,1]`。

顺序一定是先查再写，这样同一个元素不会和自己配对。`[3,3]`、$target=6$ 照样合法，因为是两个不同位置：扫到第二个 3 时，第一个 3 已经在表里了。

排序双指针也能找出这两个值，但会打乱下标，还得再映射回去，所以白板上我默认讲哈希。

## 参考代码

```python
from typing import List


def twoSum(nums: List[int], target: int) -> List[int]:
    seen = {}
    for i, x in enumerate(nums):
        need = target - x
        if need in seen:
            return [seen[need], i]
        seen[x] = i
    return []


if __name__ == "__main__":
    assert twoSum([2, 7, 11, 15], 9) == [0, 1]
    assert twoSum([3, 2, 4], 6) == [1, 2]
    assert twoSum([3, 3], 6) == [0, 1]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
assert twoSum([2, 7, 11, 15], 9) == [0, 1]
assert twoSum([3, 2, 4], 6) == [1, 2]
assert twoSum([3, 3], 6) == [0, 1]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(n)$，每个元素只入表一次。

## Edge Cases

负数和零都合法，哈希只看「这个值出现过没有」，和正负无关。两个相同值的情况（`[3,3]`、$target=6$）靠先查再写处理。答案可能在开头也可能在结尾，从左到右扫一遍都能覆盖。

## 追问

**如果有多组解，要找出所有不重复的值对呢？**
本题保证只有一组，返回任意一组就行。要是改成找「所有和为 `target` 的不重复值对」，就先排序再左右对撞：和小了 `l` 右移，和大了 `r` 左移，命中后两边同时跳过相同的值。时间 $O(n\log n)$，额外空间 $O(1)$（不计答案）。最容易错的是命中后忘了去重，`[1,1,1,2]`、$target=3$ 会输出好几组一样的对。要下标的版本不能排序，还是用哈希；只要值对时才排序。

```python
def twoSumAllPairs(nums, target):
    nums = sorted(nums)
    l, r = 0, len(nums) - 1
    ans = []
    while l < r:
        s = nums[l] + nums[r]
        if s == target:
            ans.append([nums[l], nums[r]])
            l += 1
            r -= 1
            while l < r and nums[l] == nums[l - 1]:
                l += 1
            while l < r and nums[r] == nums[r + 1]:
                r -= 1
        elif s < target:
            l += 1
        else:
            r -= 1
    return ans
```

**三数之和（LC 15）怎么做？**
排序后枚举 `i`，在它右边用对撞指针找和为 $-nums[i]$ 的两个数：和偏小 `l` 右移，偏大 `r` 左移。三重哈希难去重也更慢，不用它。`i`、`l`、`r` 都要跳过和前一个相同的值，三元组才不重复。$nums[i] \gt 0$ 时可以提前停，后面全是正数，加不出 $0$。时间 $O(n^2)$，额外空间 $O(1)$。单独一张卡 `lc-15-3sum`。

```python
def threeSum(nums):
    nums.sort()
    n, ans = len(nums), []
    for i in range(n - 2):
        if nums[i] > 0:
            break
        if i and nums[i] == nums[i - 1]:
            continue
        l, r = i + 1, n - 1
        while l < r:
            s = nums[i] + nums[l] + nums[r]
            if s < 0:
                l += 1
            elif s > 0:
                r -= 1
            else:
                ans.append([nums[i], nums[l], nums[r]])
                l += 1
                r -= 1
                while l < r and nums[l] == nums[l - 1]:
                    l += 1
                while l < r and nums[r] == nums[r + 1]:
                    r -= 1
    return ans
```

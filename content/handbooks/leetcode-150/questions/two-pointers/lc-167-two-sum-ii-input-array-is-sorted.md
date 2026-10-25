---
id: lc-167-two-sum-ii-input-array-is-sorted
section: two-pointers
order: 3
level: S
title: LC 167 · 两数之和 II - 输入有序数组
quick: "数组有序，所以用左右指针从两端往中间走：两数和偏小，左指针右移；偏大，右指针左移。找到后返回从 $1$ 开始的下标。时间 $O(n)$，额外空间 $O(1)$。"
tags:
  - Two Pointers
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 167. 两数之和 II - 输入有序数组
    url: https://leetcode.cn/problems/two-sum-ii-input-array-is-sorted/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定按非递减顺序排列的整数数组 numbers 和目标 target，找到两个不同位置，使两处数值之和等于 target。输入保证恰好有一组解。

### 接口与输出

实现 `twoSum(numbers: List[int], target: int) -> List[int]`。返回 `[index1,index2]`，其中 `1 <= index1 < index2 <= n`；这里的下标从 1 开始，与通常的 Python 下标不同。同一位置不能使用两次，目标额外空间为常数。

### 合法输入与约束

`2 <= len(numbers) <= 30000`，`-1000 <= numbers[i], target <= 1000`。数组可以包含重复值，但仍保证唯一的位置对。

### 示例

```text
输入：numbers = [2,7,11,15], target = 9
输出：[1,2]
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/description/)。

## 解题思路与参考答案

## 题意

非递减数组 `numbers`，找两个下标使对应值之和等于 `target`。恰好一组解，按下标从 $1$ 开始返回。

## 思路

数组有序，我会用左右指针对撞，额外空间是常数，题目正好要求这个。`l`、`r` 放在两端，和等于 `target` 就返回 `[l+1, r+1]`；和偏小，说明需要更大的数，`l` 右移；偏大就 `r` 左移。有序保证每次丢掉的那一端不可能再参与答案，所以不会漏解。

拿 `[2,7,11,15]`、`target=9` 看。$2+15$ 太大，`r` 左移；$2+11$ 还是太大，再左移；$2+7=9$，返回 `[1, 2]`。

哈希也能做，但要 $O(n)$ 额外空间，这里用不着。

## 参考代码

```python
from typing import List


def twoSum(numbers: List[int], target: int) -> List[int]:
    l, r = 0, len(numbers) - 1
    while l < r:
        s = numbers[l] + numbers[r]
        if s == target:
            return [l + 1, r + 1]
        if s < target:
            l += 1
        else:
            r -= 1
    return []


if __name__ == "__main__":
    assert twoSum([2, 7, 11, 15], 9) == [1, 2]
    assert twoSum([2, 3, 4], 6) == [1, 3]
    assert twoSum([-1, 0], -1) == [1, 2]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
assert twoSum([2, 7, 11, 15], 9) == [1, 2]
assert twoSum([2, 3, 4], 6) == [1, 3]
assert twoSum([-1, 0], -1) == [1, 2]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。每步丢掉一端，两端互斥地收缩。

## 边界

有负数也照样能对撞，有序就够了，不要求全正。

两个相同的值相加时，`l`、`r` 停在两个不同位置就行。

答案在最两端时，第一次比较就命中。

## 追问

**数组无序（LC 1）怎么办？**
对撞依赖有序，无序会漏解，改成扫一遍哈希。扫到 $x$ 时先查 $target-x$ 有没有出现过，再把自己的下标写进去。时间 $O(n)$，额外空间升到 $O(n)$。本题要求常数空间、返回 $1$-index，有序所以用对撞。也别先排序、对撞、再映射回原下标，排序就已经 $O(n\log n)$，还得处理重复值。独立卡见 `lc-1-two-sum`。

```python
def twoSum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i
    return []
```

**三数之和（LC 15）呢？**
无序数组里找所有不重复、和为 $0$ 的三元组。先排序，枚举 `i`，在右侧对撞找 $-nums[i]$；`i`、`l`、`r` 都跳过重复值，$nums[i] \gt 0$ 时提前停。时间 $O(n^2)$，空间 $O(1)$。别对每个 `i` 再套一遍两数之和的哈希，去重会很难写。独立卡见 `lc-15-3sum`。

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

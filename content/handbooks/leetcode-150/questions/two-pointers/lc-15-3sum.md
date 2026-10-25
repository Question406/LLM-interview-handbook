---
id: lc-15-3sum
section: two-pointers
order: 5
level: S
title: LC 15 · 三数之和
quick: "先排序，固定 `i`，在右边区间用对撞双指针找和为 $0-nums[i]$ 的两个数。`i`、`l`、`r` 都要跳过重复值，三元组才唯一。时间 $O(n^2)$，额外空间 $O(1)$。"
tags:
  - Two Pointers
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 15. 三数之和
    url: https://leetcode.cn/problems/3sum/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定一个整数数组，找出所有和为零的三元组。每个三元组必须来自三个互不相同的数组位置；数组可以含重复值，但最终结果不能重复列出同一个值三元组。

### 输入与输出

实现 `threeSum(nums: List[int]) -> List[List[int]]`。返回三元组的值，而不是下标。三元组内元素顺序和外层列表顺序均不限；无解时返回 `[]`。

### 约束

- `3 <= len(nums) <= 3000`。
- 每个元素在 `[-10^5,10^5]`。

### 示例

```text
输入：nums = [-1,0,1,2,-1,-4]
输出：[[-1,-1,2],[-1,0,1]]
```

值 -1 在示例中出现两次，允许选这两个不同位置与 2 组成 `[-1,-1,2]`，但该值组合只输出一次。

## 解题思路与参考答案

## 题意

整数数组 `nums`，找出所有不重复的三元组，使三者之和为 $0$。三元组内顺序不限。

## 思路

我会先排序，然后固定一个数 `i`，在它右边的区间用 `l`、`r` 从两端往中间走，把三数之和变成两数之和。三数和小于 $0$，需要更大的值，`l` 右移；大于 $0$，需要更小的值，`r` 左移；等于 $0$ 就保存结果，两端一起收缩。

去重最容易写错，我会先讲清楚再写循环。`nums[i] == nums[i-1]` 时跳过这个 `i`；命中一组以后，`l`、`r` 也要跳过和刚才相同的值。另外 `nums[i]` $\gt 0$ 时可以提前停，后面全是正数，加不出 $0$。用哈希去重难写，也更慢。

拿 `[-1,0,1,2,-1,-4]` 看，排序后是 `[-4,-1,-1,0,1,2]`。`i` 指向 $-4$ 时，右边最大也只能凑出 $3$，找不到。`i` 指向第一个 $-1$，对撞找到 `[-1,-1,2]` 和 `[-1,0,1]`。第二个 $-1$ 和前一个相同，跳过，所以不会再产出重复的 `[-1,0,1]`。

## 参考代码

```python
from typing import List


def threeSum(nums: List[int]) -> List[List[int]]:
    nums.sort()
    n = len(nums)
    ans: List[List[int]] = []
    for i in range(n - 2):
        if nums[i] > 0:
            break
        if i > 0 and nums[i] == nums[i - 1]:
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


if __name__ == "__main__":
    assert threeSum([-1, 0, 1, 2, -1, -4]) == [[-1, -1, 2], [-1, 0, 1]]
    assert threeSum([0, 1, 1]) == []
    assert threeSum([0, 0, 0]) == [[0, 0, 0]]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

调用可能改动输入时，每个用例新建列表或逐行复制矩阵。原地修改题要检查修改后的内容；返回有效长度的题还要比较这个长度以内的前缀，不能只检查函数有没有报错。

```python
assert threeSum([-1, 0, 1, 2, -1, -4]) == [[-1, -1, 2], [-1, 0, 1]]
assert threeSum([0, 1, 1]) == []
assert threeSum([0, 0, 0]) == [[0, 0, 0]]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n^2)$，排序的 $O(n\log n)$ 被盖住。额外空间 $O(1)$（不计答案与排序开销）。

## 边界

不足三个数时答案为空。

全正或全负都加不出 $0$；`[0,0,0]` 要收一组。

重复值很多时，`i`、`l`、`r` 三处都得跳过，漏掉任何一处都会产出重复的三元组。

## 追问

**最接近 `target` 的三数之和（LC 16）？**
同样是排序、枚举 `i`、对撞，只是不收集三元组，只维护一个 `best`，每次用当前和与 `target` 的绝对差去更新。和偏小 `l` 右移，偏大 `r` 左移，相等直接返回 `target`。时间 $O(n^2)$，空间 $O(1)$。这题只关心值，不跳过重复也能过，跳过只是少几次循环。容易栽的地方是比较时写成 `s - target` 忘了加绝对值，或者把 `best` 初始化成 $0$，应该用前三个数的和。

```python
def threeSumClosest(nums, target):
    nums.sort()
    best = nums[0] + nums[1] + nums[2]
    n = len(nums)
    for i in range(n - 2):
        l, r = i + 1, n - 1
        while l < r:
            s = nums[i] + nums[l] + nums[r]
            if abs(s - target) < abs(best - target):
                best = s
            if s < target:
                l += 1
            elif s > target:
                r -= 1
            else:
                return s
    return best
```

**四数之和（LC 18）呢？**
再套一层：排序后枚举 `i`、`j`，在 $j$ 右侧对撞找 `target - nums[i] - nums[j]`，`i`、`j`、`l`、`r` 都要跳过和前一个相同的值。时间 $O(n^3)$，空间 $O(1)$。可以加剪枝：当前最小的四数之和已经 $\gt$ `target` 就 `break`，最大的四数之和 $\lt$ `target` 就 `continue`。别写成四重循环 $O(n^4)$。推广到 $k$ 数之和，就是外层 $k-2$ 重枚举加最内层对撞，复杂度 $O(n^{k-1})$。

```python
def fourSum(nums, target):
    nums.sort()
    n, ans = len(nums), []
    for i in range(n - 3):
        if i and nums[i] == nums[i - 1]:
            continue
        for j in range(i + 1, n - 2):
            if j > i + 1 and nums[j] == nums[j - 1]:
                continue
            l, r = j + 1, n - 1
            while l < r:
                s = nums[i] + nums[j] + nums[l] + nums[r]
                if s < target:
                    l += 1
                elif s > target:
                    r -= 1
                else:
                    ans.append([nums[i], nums[j], nums[l], nums[r]])
                    l += 1
                    r -= 1
                    while l < r and nums[l] == nums[l - 1]:
                        l += 1
                    while l < r and nums[r] == nums[r + 1]:
                        r -= 1
    return ans
```

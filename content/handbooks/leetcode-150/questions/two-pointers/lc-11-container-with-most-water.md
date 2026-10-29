---
id: lc-11-container-with-most-water
section: two-pointers
order: 4
level: S
title: LC 11 · 盛最多水的容器
quick: >-
  两端对撞，面积是 $\min(h[l],h[r])\cdot(r-l)$。每次把较矮的一侧往里移，因为高度被矮边卡住，换掉它才可能变高。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Two Pointers
  - Greedy
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 11. 盛最多水的容器
    url: 'https://leetcode.cn/problems/container-with-most-water/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

在坐标平面上，数组 height 的第 i 个元素表示位于横坐标 i、从横轴向上延伸的竖线高度。任选两条线，与横轴共同围成一个不能倾斜的容器，求最多能容纳的水量。容量由两条线的间距与较短线的高度决定。

### 输入与输出

实现 `maxArea(height) -> int`，返回最大容量而不是两条线的下标。横坐标取数组的从 0 开始下标。

### 约束与约定

- `2 <= len(height) <= 100000`。
- 每条竖线高度在 `[0,10000]`。

### 示例

```text
输入：height = [1,8,6,2,5,4,8,3,7]
输出：49
```

示例选择下标 1 与 8 的两条线，间距为 7，可用高度为 7，因此容量为 49。

[官方原题与完整题面](https://leetcode.com/problems/container-with-most-water/description/)。

## 解题思路与参考答案

## 题意

`height[i]` 是竖线高度。选两条线与 $x$ 轴围成容器，求能盛的最大水量。底边长度为下标差，高度取较短边。

## 思路

我会用左右指针对撞，每次丢掉较矮的那条边。宽度从最大开始，`l=0`、`r=n-1`，当前面积是 $\min(h[l],h[r])\cdot(r-l)$。高度被较矮的那条卡住，把它往里移才有机会变高；移较高的那条，宽度变小，高度也不会增加，面积只会更小。两边一样高时随便移一侧。

拿 `[1,8,6,2,5,4,8,3,7]` 看。一开始两端是 $1$ 和 $7$，面积 $1\cdot 8=8$，矮的是左边的 $1$，左指针右移到 $8$。这时两端是 $8$ 和 $7$，面积 $7\cdot 7=49$，后面再也超不过它，答案就是 $49$。

暴力枚举是 $O(n^2)$，过不了。面试时我会先写面积公式，再论证为什么丢矮留高是安全的。

## 参考代码

```python
from typing import List


def maxArea(height: List[int]) -> int:
    l, r = 0, len(height) - 1
    ans = 0
    while l < r:
        ans = max(ans, min(height[l], height[r]) * (r - l))
        if height[l] <= height[r]:
            l += 1
        else:
            r -= 1
    return ans


if __name__ == "__main__":
    assert maxArea([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
    assert maxArea([1, 1]) == 1
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert maxArea([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
assert maxArea([1, 1]) == 1
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。每步丢一条边。

## Edge Cases

只有两条线时，答案就是 $\min(h[0],h[1])\cdot 1$。

高度单调升或单调降时，最优往往出在「最矮的远端」和「最高柱」之间。

中间有一根特别高的柱子，它会一直被留下，较矮的一侧继续往里移。

## 追问

**要输出左右下标呢？**
刷新最大面积时记下当时的 `l`、`r` 就行。算法不变，还是丢矮留高，时间 $O(n)$。下标从 $0$ 还是从 $1$ 开始要问清。两边一样高时移哪一侧都不影响最优面积，但可能影响最后是哪一对下标；如果要字典序最小的一对，相等时得两边都试，或者额外比较，所以我会先确认并列规则。别为了下标退回 $O(n^2)$ 枚举。

```python
def maxAreaIndex(height):
    l, r = 0, len(height) - 1
    ans = best = (0, 0)
    while l < r:
        area = min(height[l], height[r]) * (r - l)
        if area > ans:
            ans, best = area, (l, r)
        if height[l] <= height[r]:
            l += 1
        else:
            r -= 1
    return best
```

**接雨水（LC 42）跟这题有什么不同？**
接雨水算的是每个位置上方能积多少水，和两条边围一个桶是两回事。每个位置的水量由「左右最高柱里较小的那个减去自身高度」决定。双指针版维护 `left_max`、`right_max`，哪侧的最大高度更矮就先结算哪侧，因为较矮那侧的上界已经确定，多出来的就是积水。时间 $O(n)$，额外空间 $O(1)$。也可以预先开左右最大值数组，空间 $O(n)$。别和这题「丢矮留高求最大面积」混成一套公式。独立卡见 `lc-42-trapping-rain-water`。

```python
def trap(height):
    l, r = 0, len(height) - 1
    left_max = right_max = ans = 0
    while l < r:
        if height[l] < height[r]:
            left_max = max(left_max, height[l])
            ans += left_max - height[l]
            l += 1
        else:
            right_max = max(right_max, height[r])
            ans += right_max - height[r]
            r -= 1
    return ans
```

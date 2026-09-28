---
id: lc-11-container-with-most-water
section: two-pointers
order: 4
level: S
title: LC 11 · 盛最多水的容器
quick: >-
  两端对撞，面积 $\min(h[l],h[r])\cdot(r-l)$。每次把较矮一侧内移，才可能换来更高的边。时间
  $O(n)$，额外空间 $O(1)$。
tags:
  - Two Pointers
  - Greedy
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 11. 盛最多水的容器
    url: https://leetcode.cn/problems/container-with-most-water/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

`height[i]` 是竖线高度。选两条线与 $x$ 轴围成容器，求能盛的最大水量。底边长度为下标差，高度取较短边。

## 思路

宽度从最大开始：`l=0`、`r=n-1`。当前面积是 $\min(h[l],h[r])\cdot(r-l)$。较矮的那条限制了高度，把它内移才可能变高；移动较高边，宽度变小而高度不会增加。两边一样高时任移一侧。

暴力 $O(n^2)$ 过不了。我会先写面积公式，再论证「弃矮留高」。

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

## 复杂度

时间 $O(n)$，额外空间 $O(1)$。每步丢一条边。

## 边界

- 只有两条线：答案就是 $\min(h[0],h[1])\cdot 1$。
- 单调升 / 单调降：最优往往在「最矮的远端」与「最高柱」之间。
- 中间有极高柱：高柱会留下，较矮一侧继续内移。

## 追问

- **必须输出左右下标？** 刷新最大面积时记下当时的 `l`、`r`。算法不变：仍是弃矮留高，时间 $O(n)$。下标从 $0$ 还是从 $1$ 开始要问清。两边一样高时任移一侧不影响最优面积，但可能改变「哪一对下标」；若要字典序最小的一对，相等时要两边都试或额外比较，我会先确认并列规则。别为了下标改回 $O(n^2)$ 枚举。

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

- **接雨水（LC 42）？** 算的是每个位置上方能积多少，不是两条边围桶。水量由「左右最高柱的较小值减去自身」决定。双指针版：维护 `left_max`、`right_max`，哪侧最大高度更矮就先结算哪侧。较矮侧的上界已经确定，多出来的就是积水。时间 $O(n)$，额外空间 $O(1)$。也可以预开左右最大值数组，空间 $O(n)$。别和这题的「弃矮留高求最大面积」混成一套公式。独立卡见 `lc-42-trapping-rain-water`。

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

---
id: lc-739-daily-temperatures
section: monotonic-stack
order: 1
level: S
title: LC 739 · 每日温度
quick: >-
  单调递减栈存下标。新温度比栈顶高，就弹出栈顶 `j` 并写 `ans[j] = i - j`；每个下标入栈、出栈各一次。时间 $O(n)$，额外空间
  $O(n)$。
tags:
  - Array
  - Monotonic Stack
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 739. Daily Temperatures
    url: https://leetcode.com/problems/daily-temperatures/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

给每日温度数组 `temperatures`，对每一天 $i$，求还要等几天才会出现严格更高的温度；之后都不会更高则为 $0$。$1 \le n \le 10^5$，温度在 $[30, 100]$。

## 思路

这是「下一个更大元素」。栈里放还没找到答案的下标，对应温度从栈底到栈顶非递增。扫到第 $i$ 天时，只要 `T[i]` 严格大于栈顶那天的温度，栈顶那天的答案就是 $i - j$，弹掉；比不过就停，把 $i$ 压进去。

为什么弹掉不会漏：被弹的 $j$ 已经拿到了最近的更高温度。没被弹的都比 `T[i]` 高或相等，它们等的是比自己更高的那天，`T[i]` 帮不上。暴力对每天往后找是 $O(n^2)$。

## 参考代码

```python
from typing import List


def dailyTemperatures(temperatures: List[int]) -> List[int]:
    ans = [0] * len(temperatures)
    stack: List[int] = []
    for i, t in enumerate(temperatures):
        while stack and temperatures[stack[-1]] < t:
            j = stack.pop()
            ans[j] = i - j
        stack.append(i)
    return ans


if __name__ == "__main__":
    assert dailyTemperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]
    assert dailyTemperatures([30, 40, 50, 60]) == [1, 1, 1, 0]
    assert dailyTemperatures([30, 60, 90]) == [1, 1, 0]
    assert dailyTemperatures([50, 50]) == [0, 0]
    assert dailyTemperatures([90, 80, 70]) == [0, 0, 0]
    assert dailyTemperatures([1]) == [0]
    print("ok")
```

## 复杂度

时间 $O(n)$，每个下标最多入栈、出栈各一次；额外空间 $O(n)$。

## 边界

- 相等温度不算更高：比较用严格大于，`[50, 50]` 都是 $0$。
- 单调递减：没有任何弹栈，全部为 $0$。
- 扫完仍在栈里的下标：答案保持初值 $0$。

## 追问

- **不用栈、$O(1)$ 额外空间（不计答案）？** 从右往左算，利用已经算好的 `ans` 跳着找：从 $j = i+1$ 开始，若 `T[j]` 不比 `T[i]` 高，就跳到 $j + ans[j]$；`ans[j]` 为 $0$ 说明后面没有更高，直接停。

```python
def dailyTemperaturesJump(T):
    n = len(T)
    ans = [0] * n
    for i in range(n - 2, -1, -1):
        j = i + 1
        while j < n and T[j] <= T[i]:
            if ans[j] == 0:
                j = n
                break
            j += ans[j]
        if j < n:
            ans[i] = j - i
    return ans
```

- **循环数组的下一个更大元素（LC 503）？** 下标扫 $0 \ldots 2n-1$，用 `i % n` 取值，只在第一圈入栈。求「上一个更大」则换方向或看弹栈后的栈顶，见 `lc-901-online-stock-span`。

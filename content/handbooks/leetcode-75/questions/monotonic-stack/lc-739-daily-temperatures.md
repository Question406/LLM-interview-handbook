---
id: lc-739-daily-temperatures
section: monotonic-stack
order: 1
level: S
title: LC 739 · 每日温度
quick: >-
  这是「下一个更大元素」，用单调递减栈存还没找到答案的下标。新温度比栈顶高，就弹出栈顶 `j` 并写 `ans[j] = i -
  j`；每个下标入栈、出栈各一次。时间 $O(n)$，额外空间 $O(n)$。
tags:
  - Array
  - Monotonic Stack
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 739. Daily Temperatures
    url: 'https://leetcode.com/problems/daily-temperatures/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

给定按日期顺序排列的温度数组 `temperatures`。对于每一天 i，找出它之后第一次出现严格更高温度的日期，计算需要等待的天数；温度相等不算更暖。若之后再没有更高温度，这一天的等待天数为0。

### 输入与输出

实现 `dailyTemperatures(temperatures) -> List[int]`，返回与输入同长度的列表。第 i 个结果是日期下标之差，不是未来温度，也不是所有更暖天数的总量。

### 约束

- `1 <= len(temperatures) <= 10^5`。
- `30 <= temperatures[i] <= 100`。

### 示例

```text
输入：temperatures = [73,74,75,71,69,72,76,73]
输出：[1,1,4,2,1,1,0,0]
```

[LeetCode 原题](https://leetcode.com/problems/daily-temperatures/description/)

## 解题思路与参考答案

## 题意

给每日温度数组 `temperatures`，对每一天 $i$，求还要等几天才会出现严格更高的温度；之后都不会更高则为 $0$。$1 \le n \le 10^5$，温度在 $[30, 100]$。

## 思路

这是「下一个更大元素」，我会用单调栈。栈里放还没找到答案的下标，对应温度从栈底到栈顶非递增。扫到第 $i$ 天时，只要 `T[i]` 严格大于栈顶那天 $j$ 的温度，$j$ 的答案就是 $i - j$，弹掉；比不过就停，把 $i$ 压进去。暴力对每天往后找是 $O(n^2)$。

拿 `[73, 74, 75, 71, 69, 72, 76, 73]` 走一遍。74 把 73 弹掉，75 把 74 弹掉，答案都是 1。接着 71、69 依次入栈，栈里是 75、71、69。72 来了，先弹 69（等 1 天），再弹 71（等 2 天），碰到 75 停下。76 再弹掉 72 和 75，75 等了 $6-2=4$ 天。最后 76、73 留在栈里，答案保持 0。

弹栈不会漏答案。被弹的 $j$ 已经拿到了最近的更高温度；没被弹的都比 `T[i]` 高或相等，它们等的是比自己更高的那天，`T[i]` 帮不上。

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
    assert dailyTemperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [
        1,
        1,
        4,
        2,
        1,
        1,
        0,
        0,
    ]
    assert dailyTemperatures([30, 40, 50, 60]) == [1, 1, 1, 0]
    assert dailyTemperatures([30, 60, 90]) == [1, 1, 0]
    assert dailyTemperatures([50, 50]) == [0, 0]
    assert dailyTemperatures([90, 80, 70]) == [0, 0, 0]
    assert dailyTemperatures([1]) == [0]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert dailyTemperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]
assert dailyTemperatures([30, 40, 50, 60]) == [1, 1, 1, 0]
assert dailyTemperatures([30, 60, 90]) == [1, 1, 0]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，每个下标最多入栈、出栈各一次；额外空间 $O(n)$。

## Edge Cases

相等温度不算更高，比较用严格大于，`[50, 50]` 都是 $0$。

单调递减时没有任何弹栈，全部为 $0$。

扫完仍在栈里的下标，答案保持初值 $0$。

## 追问

**不用栈、$O(1)$ 额外空间（不计答案）能做吗？**
能。从右往左算，利用已经算好的 `ans` 跳着找：从 $j = i+1$ 开始，若 `T[j]` 不比 `T[i]` 高，就跳到 $j + ans[j]$；`ans[j]` 为 $0$ 说明后面没有更高的，直接停。

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

**循环数组的下一个更大元素（LC 503）怎么改？**
下标扫 $0 \ldots 2n-1$，用 `i % n` 取值，只在第一圈入栈。

**求「上一个更大」呢？**
换个方向扫，或者看弹栈后的栈顶，见 `lc-901-online-stock-span`。

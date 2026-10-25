---
id: lc-209-minimum-size-subarray-sum
section: sliding-window
order: 1
level: A
title: LC 209 · 长度最小的子数组
quick: "元素全是正数，所以能用滑动窗口：右指针一直扩、累加和，和 $\\ge$ `target` 时更新最短长度并左缩。找不到返回 $0$。时间 $O(n)$，额外空间 $O(1)$。"
tags:
  - Sliding Window
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 209. 长度最小的子数组
    url: https://leetcode.cn/problems/minimum-size-subarray-sum/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定正整数数组 nums 和正整数 target，找出元素总和至少为 target 的最短非空连续子数组。返回它的长度；如果任何连续子数组都达不到 target，则返回 0。

### 输入与输出

实现 `minSubArrayLen(target, nums) -> int`。子数组必须来自连续下标，答案是元素个数，不是总和或区间本身。

### 约束与约定

- `1 <= target <= 1000000000`。
- `1 <= len(nums) <= 100000`。
- 每个 nums 元素都在 `[1,10000]`，不包含零或负数。

### 示例

```text
输入：target = 7, nums = [2,3,1,2,4,3]
输出：2
```

示例的连续子数组 [4,3] 已达到 7，长度为 2；没有单个元素达到 7。

[官方原题与完整题面](https://leetcode.com/problems/minimum-size-subarray-sum/description/)。

## 解题思路与参考答案

## 题意

正整数数组 `nums` 和 `target`，找最短连续子数组使和 $\ge$ `target`。不存在返回 $0$。

## 思路

数组全是正数，我会用滑动窗口。全正意味着窗口往右扩，和只会变大；往左缩，和只会变小。这个单调性是滑窗成立的前提，所以写之前我会先跟面试官确认「全是正数」。

做法是 `right` 一直往右走，把数加进 `acc`。一旦 `acc >= target`，就用 `right-left+1` 更新答案，然后减掉 `nums[left]`、左指针右移，一直缩到和不够为止。

拿 `target=7`、`nums=[2,3,1,2,4,3]` 走一下。右指针走到第四个数时，窗口 `[2,3,1,2]` 和是 $8$，先记下长度 $4$，左缩掉 $2$ 以后和不够了。吃进 $4$ 以后，窗口能一路缩到 `[1,2,4]`，长度 $3$。最后吃进 $3$，窗口缩到 `[4,3]`，和正好是 $7$，长度 $2$，这就是答案。

另一种做法是前缀和加二分，复杂度 $O(n\log n)$。

## 参考代码

```python
from typing import List


def minSubArrayLen(target: int, nums: List[int]) -> int:
    n = len(nums)
    left = acc = 0
    ans = n + 1
    for right, x in enumerate(nums):
        acc += x
        while acc >= target:
            ans = min(ans, right - left + 1)
            acc -= nums[left]
            left += 1
    return 0 if ans == n + 1 else ans


if __name__ == "__main__":
    assert minSubArrayLen(7, [2, 3, 1, 2, 4, 3]) == 2
    assert minSubArrayLen(4, [1, 4, 4]) == 1
    assert minSubArrayLen(11, [1, 1, 1, 1, 1, 1, 1, 1]) == 0
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert minSubArrayLen(7, [2, 3, 1, 2, 4, 3]) == 2
assert minSubArrayLen(4, [1, 4, 4]) == 1
assert minSubArrayLen(11, [1, 1, 1, 1, 1, 1, 1, 1]) == 0
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，每个下标最多进、出窗口各一次。额外空间 $O(1)$。

## 边界

单个元素就 $\ge$ `target` 时，第一次进 `while` 记下的长度就是 $1$。

整段加起来都不够，`ans` 会停在 $n+1$，返回 $0$。

`target` 恰好等于某段和也没问题，左缩到刚好不够之前，最短长度已经更新过了。

## 追问

**数组里有负数怎么办？**
滑窗就不能用了。有负数时「右扩变大、左缩变小」不再成立，滑窗会漏解。改用前缀和，要找满足 `pref[j] - pref[i] \ge target` 且 $j-i$ 最短的一对。用单调队列维护「前缀递增」的下标：队头一旦满足差值 $\ge$ `target`，就弹出并更新答案；队尾把不小于当前前缀的旧值丢掉。时间 $O(n)$，空间 $O(n)$。这是 LC 862 的模板，找不到时返回 $-1$ 还是 $0$ 要跟题面走。也别再对每个右端做二分，有负数时前缀不单调，普通二分会错。

```python
from collections import deque

def shortestSubarray(nums, target):
    n = len(nums)
    pref = [0] * (n + 1)
    for i, x in enumerate(nums):
        pref[i + 1] = pref[i] + x
    dq = deque()
    ans = n + 1
    for j, p in enumerate(pref):
        while dq and p - pref[dq[0]] >= target:
            ans = min(ans, j - dq.popleft())
        while dq and pref[dq[-1]] >= p:
            dq.pop()
        dq.append(j)
    return 0 if ans == n + 1 else ans
```

**换成乘积小于 $k$ 的子数组个数（LC 713）呢？**
还是滑窗。元素同样为正，窗口乘积随右扩变大、随左缩变小。`right` 乘上当前数，`prod \ge k` 时除以左端并左移。这时以 `right` 结尾、起点在 $[left, right]$ 里的子数组乘积都 $\lt k$，答案加上 $right-left+1$。$k \le 1$ 时正整数乘积不可能小于 $k$，直接返回 $0$。时间 $O(n)$，空间 $O(1)$。容易栽的地方是写成 `+= 1`，那样每个右端只数了一个窗口，以 `right` 结尾的其他子数组都漏了。

```python
def numSubarrayProductLessThanK(nums, k):
    if k <= 1:
        return 0
    prod = 1
    left = ans = 0
    for right, x in enumerate(nums):
        prod *= x
        while prod >= k:
            prod //= nums[left]
            left += 1
        ans += right - left + 1
    return ans
```

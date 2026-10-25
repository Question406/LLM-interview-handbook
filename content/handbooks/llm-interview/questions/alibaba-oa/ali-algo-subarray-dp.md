---
id: ali-algo-subarray-dp
section: alibaba-oa
order: 36
level: A
title: 阿里手撕：最大子数组、买卖股票、接雨水、最长回文怎么收口？
quick: >-
  四道题都先定义「以 $i$ 结尾 / 经过 $i$」再写转移。最大子数组（53）用 Kadane，比较从当前元素重新开始和接在前一段后面；买卖股票（121）维护此前最低价；接雨水（42）取左右最高柱的较小值再减当前高度；最长回文（5）用中心扩展或 DP。
tags:
  - Alibaba
  - DP
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 最大子数组和
    url: https://leetcode.cn/problems/maximum-subarray/
    type: primary
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
---

## 题目描述

本卡有四个独立的数组或字符串接口。请分别实现它们，不能把“子数组”和“子序列”混为一谈：这里的子数组、子串都要求在原输入中连续。

### 输入与输出

- `max_sub_array(nums)`：输入非空整数数组，返回任一非空连续子数组的最大元素和。全负数时也必须选至少一个元素。
- `max_profit(prices)`：输入非空每日价格数组，只能先买入一次、在更晚的一天卖出一次；也可以不交易。返回最大非负利润。
- `trap(height)`：数组表示宽度均为 1 的非负柱高，返回下雨后可在柱子之间存住的总水量，不能在最左、最右边界之外存水。
- `longest_palindrome(s)`：返回字符串中最长的连续回文子串；有多个同长度答案时任意一个均可。空字符串返回空字符串。

### 示例

```text
max_sub_array([-2,1,-3,4,-1,2,1,-5,4]) -> 6
max_sub_array([-1,-2,-3])            -> -1
max_profit([7,1,5,3,6,4])            -> 5
max_profit([7,6,4,3,1])              -> 0
trap([0,1,0,2,1,0,1,3,2,1,2,1])    -> 6
longest_palindrome("babad")         -> "bab" 或 "aba"
```

接口和示例为手册统一的练习版本，分别对应相关算法题的基本语义。

## 解题思路与参考答案

这四道我都会先定义「以 $i$ 结尾」或「经过 $i$」的量，再写转移，不去枚举区间。Kadane、一次买卖、接雨水、中心扩展回文，是阿里手撕里最常串着问的一维 DP 和双指针（LeetCode 53 / 121 / 42 / 5）。

53 的状态是以 $i$ 结尾的最大和：`dp[i]=\max(a[i],\,dp[i-1]+a[i])`。前面那段的和已经在拖后腿，就从当前元素重新开始，同时更新全局最大。全是负数时答案是最大的那个元素，因为必须选一段非空的。

121 只交易一次。从左往右扫，维护历史最低买价，`ans=\max(ans,\,\mathrm{price}-\mathrm{min\_price})`。价格单调递减时利润是 $0$。

42 里位置 $i$ 能接的水是 $\max(0,\,\min(L_{\max}[i],R_{\max}[i])-h[i])$，左右最高柱里矮的那根决定水位。可以预计算左右最高数组，空间 $O(n)$；也可以双指针从两端往中间收，哪边矮先结算哪边，时间 $O(n)$、空间 $O(1)$。两端的位置接不住水。

5 对每个中心分别按奇数和偶数长度往外扩，记录最长的起止位置，时间 $O(n^2)$、空间 $O(1)$；用 DP 表的话空间是 $O(n^2)$。能写 Manacher 更好，不写也行。边界测单字符和全相同的串。

```python
from typing import List


def max_sub_array(nums: List[int]) -> int:
    best = cur = nums[0]
    for x in nums[1:]:
        cur = x if cur + x < x else cur + x
        if cur > best:
            best = cur
    return best


def max_profit(prices: List[int]) -> int:
    min_price = prices[0]
    ans = 0
    for p in prices:
        if p < min_price:
            min_price = p
        elif p - min_price > ans:
            ans = p - min_price
    return ans


def trap(height: List[int]) -> int:
    left, right = 0, len(height) - 1
    left_max = right_max = 0
    water = 0
    while left < right:
        if height[left] < height[right]:
            if height[left] >= left_max:
                left_max = height[left]
            else:
                water += left_max - height[left]
            left += 1
        else:
            if height[right] >= right_max:
                right_max = height[right]
            else:
                water += right_max - height[right]
            right -= 1
    return water


def longest_palindrome(s: str) -> str:
    def expand(l: int, r: int) -> tuple[int, int]:
        while l >= 0 and r < len(s) and s[l] == s[r]:
            l -= 1
            r += 1
        return l + 1, r - 1

    start = end = 0
    for i in range(len(s)):
        l1, r1 = expand(i, i)
        l2, r2 = expand(i, i + 1)
        if r1 - l1 > end - start:
            start, end = l1, r1
        if r2 - l2 > end - start:
            start, end = l2, r2
    return s[start : end + 1]


if __name__ == "__main__":
    assert max_sub_array([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
    assert max_sub_array([-1, -2, -3]) == -1
    assert max_profit([7, 1, 5, 3, 6, 4]) == 5
    assert max_profit([7, 6, 4, 3, 1]) == 0
    assert trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
    assert longest_palindrome("babad") in {"bab", "aba"}
    assert longest_palindrome("cbbd") == "bb"
    print("ok")
```

53 和 121 都是时间 $O(n)$、空间 $O(1)$。

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert max_sub_array([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 追问

**股票加手续费，或者最多两次交易呢？**
在 121 的状态上加持仓和交易次数两个维度，别去枚举切分点写暴力。

**122 可以多次买卖呢？**
把相邻的上升差全部累加起来。

**子数组换成子序列呢？**
53 要求连续。换成最长递增子序列就是另一道题了，做法是 $O(n\log n)$。

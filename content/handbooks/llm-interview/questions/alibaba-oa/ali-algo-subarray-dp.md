---
id: ali-algo-subarray-dp
section: alibaba-oa
order: 36
level: A
title: 阿里手撕：最大子数组、买卖股票、接雨水、最长回文怎么收口？
quick: >-
  53 是 Kadane。121 是最低前缀买。42 是左右最高矮的那边减高度。5 是中心扩展或 DP。先定义「以 i 结尾」再转移。
tags:
  - Alibaba
  - DP
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-18
sources:
  - title: 最大子数组和
    url: https://leetcode.cn/problems/maximum-subarray/
    type: primary
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
---

## 真题 / 考点说明

- 对应：LeetCode 53 / 121 / 42 / 5

四道题都先定义「以 $i$ 结尾 / 经过 $i$」再转移，不要一上来枚举区间。Kadane、一次买卖、接雨水、中心扩展回文，是阿里手撕里最常串着问的一维 DP / 双指针族。

## 思路

53：`dp[i]=\max(a[i],\,dp[i-1]+a[i])`，同步更新全局 max。全负则取最大元素，因为必须选一段非空。

121：只交易一次。扫的时候维护历史最低买价，`ans=\max(ans,\,\mathrm{price}-\mathrm{min\_price})`。

42：位置 $i$ 能接的水是 $\max(0,\,\min(L_{\max}[i],R_{\max}[i])-h[i])$。可预计算左右最高，或双指针从两端收，矮的一侧先结算。

5：每个中心扩奇数、偶数两种；记录最长的起止。Manacher 是加分不是必须。

追问手续费 / 两次交易：在 121 的状态上加持仓维度，不要重写暴力。

## 参考代码

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

## 复杂度

- 53 / 121：时间 $O(n)$，空间 $O(1)$。
- 42 双指针：时间 $O(n)$，空间 $O(1)$；左右最高数组是 $O(n)$ 空间。
- 5 中心扩展：时间 $O(n^2)$，空间 $O(1)$。DP 表是 $O(n^2)$ 空间。

## 边界与追问

1. 53 全负取最大元素；121 单调递减利润为 $0$；42 两端接不住水；5 单字符、全相同。
2. 追问 122 可多次买卖：相邻上升差累加。追问手续费 / 两次交易：状态加持仓与交易次数，不要枚举切分点暴力。
3. 追问「子数组 vs 子序列」：53 必须连续；若改最长递增子序列则是 $O(n\log n)$ 的另一道题。

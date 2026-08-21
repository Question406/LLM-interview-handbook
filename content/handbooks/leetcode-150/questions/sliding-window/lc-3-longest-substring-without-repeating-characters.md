---
id: lc-3-longest-substring-without-repeating-characters
section: sliding-window
order: 2
level: S
title: LC 3 · 无重复字符的最长子串
quick: >-
  哈希记下每个字符上次下标。右扫时若窗口内撞车，左指针跳到重复字符的下一位。时间
  $O(n)$，空间 $O(\Sigma)$。
tags:
  - Sliding Window
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 3. 无重复字符的最长子串
    url: https://leetcode.cn/problems/longest-substring-without-repeating-characters/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

字符串 `s`，求不含重复字符的最长连续子串长度。

## 思路

`last[ch]` 记 `ch` 最近一次出现的下标。右指针 `i` 扫到 `ch` 时，若 `last[ch]` 仍在窗口内（$\ge$ `left`），把 `left` 跳到 `last[ch]+1`。再更新 `last[ch]=i`，用 `i-left+1` 刷新最长。

集合 + 一步步左移也对，但哈希直接跳更快讲。面试说清「窗口永远无重复」。

## 参考代码

```python
def lengthOfLongestSubstring(s: str) -> int:
    last = {}
    left = ans = 0
    for i, ch in enumerate(s):
        if ch in last and last[ch] >= left:
            left = last[ch] + 1
        last[ch] = i
        ans = max(ans, i - left + 1)
    return ans


if __name__ == "__main__":
    assert lengthOfLongestSubstring("abcabcbb") == 3
    assert lengthOfLongestSubstring("bbbbb") == 1
    assert lengthOfLongestSubstring("pwwkew") == 3
    assert lengthOfLongestSubstring("") == 0
    print("ok")
```

## 复杂度

时间 $O(n)$，每个字符进窗口一次。空间 $O(\Sigma)$，$\Sigma$ 为字符集大小。

## 边界

- 空串长度 $0$；全相同长度 $1$；全不同长度就是 $n$。
- 重复字符出现在窗口左侧之外：`last[ch] \lt left`，不能把 `left` 往回跳。

## 追问

- **要返回子串本身而不是长度？** 刷新 `ans` 的同时记下当时的 `best_left`。最后切片 `s[best_left : best_left + ans]`。时间仍 $O(n)$。多个同样长的无重复子串，题面没要求就返回第一次取到最大长度的那段。不要在循环里每次 `s[left:i+1]` 拷贝，那会把时间抬到 $O(n^2)$。

```python
def longestSubstring(s):
    last, left, ans, best_left = {}, 0, 0, 0
    for i, ch in enumerate(s):
        if ch in last and last[ch] >= left:
            left = last[ch] + 1
        last[ch] = i
        if i - left + 1 > ans:
            ans = i - left + 1
            best_left = left
    return s[best_left : best_left + ans]
```

- **最多含 $k$ 个不同字符（LC 340）？** 窗口改成「种类数 $\le k$」。哈希计数：右端吃进字符，`len(cnt) \gt k` 时减左端，减到 $0$ 就删掉这个 key。每次窗口合法后用 $right-left+1$ 更新最长。$k=0$ 对非空串答案是 $0$；$k=1$ 退化成最长相同字符段。时间 $O(n)$，空间 $O(\min(|\Sigma|,k))$。本题是 $k=|\Sigma|$ 且还要求窗口内无重复，相当于每种字符次数 $\le 1$，用「上次下标」比计数更直接。

```python
from collections import Counter

def lengthOfLongestSubstringKDistinct(s, k):
    cnt = Counter()
    left = ans = 0
    for right, ch in enumerate(s):
        cnt[ch] += 1
        while len(cnt) > k:
            cnt[s[left]] -= 1
            if cnt[s[left]] == 0:
                del cnt[s[left]]
            left += 1
        ans = max(ans, right - left + 1)
    return ans
```

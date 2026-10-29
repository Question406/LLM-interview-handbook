---
id: lc-3-longest-substring-without-repeating-characters
section: sliding-window
order: 2
level: S
title: LC 3 · 无重复字符的最长子串
quick: >-
  滑动窗口加一个哈希表，记每个字符上次出现的下标。右指针遇到窗口内已有的字符，就把左指针直接跳到它上次位置的下一位，窗口始终没有重复。时间 $O(n)$，空间
  $O(\Sigma)$。
tags:
  - Sliding Window
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 3. 无重复字符的最长子串
    url: >-
      https://leetcode.cn/problems/longest-substring-without-repeating-characters/
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定字符串 `s`，找出其中不包含重复字符的最长连续子串，并返回它的长度。子串必须连续，不能通过跳过中间字符拼接；字母、数字、标点与空格都作为普通字符参与重复判断。

### 输入与输出

实现 `lengthOfLongestSubstring(s) -> int`。返回长度，不要求返回子串内容；空字符串返回 0。不同大小写字符按不同字符处理。

### 约束

- `0 <= len(s) <= 10^5`。
- 字符串可包含英文字母、数字、符号和空格。

### 示例

```text
输入：s = "abcabcbb"
输出：3
```

[LeetCode 原题](https://leetcode.com/problems/longest-substring-without-repeating-characters/description/)

## 解题思路与参考答案

## 题意

字符串 `s`，求不含重复字符的最长连续子串长度。

## 思路

我会用滑动窗口，再配一个哈希表 `last`，`last[ch]` 记 `ch` 最近一次出现的下标。窗口始终保持没有重复字符；有了位置信息，左指针遇到重复时能一步跳到位。

右指针 `i` 扫到 `ch` 时，如果 `last[ch]` 还在窗口里（$\ge$ `left`），就把 `left` 跳到 `last[ch]+1`。然后更新 `last[ch]=i`，用 `i-left+1` 刷新最长长度。

拿 `"abcabcbb"` 走一下。前三个字符 `abc` 没有重复，长度到 $3$。`i=3` 又遇到 `a`，它上次在下标 $0$，`left` 跳到 $1$，窗口变成 `bca`，长度还是 $3$。后面每遇到一个重复字符，`left` 都跳到它上次位置的下一位，窗口再也没超过 $3$，答案是 $3$。

用集合、一步一步左移也对，只是哈希表记下位置以后，左指针能直接跳过去。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert lengthOfLongestSubstring("abcabcbb") == 3
assert lengthOfLongestSubstring("bbbbb") == 1
assert lengthOfLongestSubstring("pwwkew") == 3
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，每个字符进窗口一次。空间 $O(\Sigma)$，$\Sigma$ 为字符集大小。

## Edge Cases

空串长度是 $0$，全相同是 $1$，全不同就是 $n$。

重复字符如果出现在 window 的 left bound 之外，也就是 `last[ch] \lt left`，就不用管它，`left` 不能往回跳。

## 追问

**要返回子串本身，不只是长度呢？**
刷新 `ans` 的同时记下当时的 `best_left`，最后切片 `s[best_left : best_left + ans]`，时间仍是 $O(n)$。有多个一样长的无重复子串时，题面没要求就返回第一次取到最大长度的那段。别在循环里每次拷贝 `s[left:i+1]`，那会把时间抬到 $O(n^2)$。

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

**改成最多含 $k$ 个不同字符（LC 340）呢？**
窗口条件换成「种类数 $\le k$」，用哈希计数。右端吃进字符，`len(cnt) \gt k` 时减左端，计数减到 $0$ 就删掉这个 key。窗口每次合法后用 $right-left+1$ 更新最长。$k=0$ 时非空串答案是 $0$；$k=1$ 退化成最长相同字符段。时间 $O(n)$，空间 $O(\min(|\Sigma|,k))$。本题相当于 $k=|\Sigma|$ 再加上窗口内无重复，也就是每种字符次数 $\le 1$，所以用「上次下标」比计数更直接。

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

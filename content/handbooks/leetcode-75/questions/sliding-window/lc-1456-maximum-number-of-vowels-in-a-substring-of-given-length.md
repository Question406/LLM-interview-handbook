---
id: lc-1456-maximum-number-of-vowels-in-a-substring-of-given-length
section: sliding-window
order: 2
level: A
title: LC 1456 · 定长子串中元音的最大数目
quick: >-
  定长滑窗计元音数：右边进来一个元音就加一，左边出去一个元音就减一，维护最大值；达到 $k$ 可以提前返回。时间 $O(n)$，额外空间
  $O(1)$。
tags:
  - String
  - Sliding Window
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 1456. Maximum Number of Vowels in a Substring of Given Length
    url: https://leetcode.com/problems/maximum-number-of-vowels-in-a-substring-of-given-length/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

给小写字母串 `s` 和整数 $k$，在所有长度为 $k$ 的子串里，返回元音（`a e i o u`）个数的最大值。$1 \le k \le |s| \le 10^5$。

## 思路

和 `lc-643-maximum-average-subarray-i` 同一个定长窗口骨架，只是把「和」换成「元音计数」。下标 `i` 进窗口时看 `s[i]` 是不是元音，`s[i-k]` 出窗口时同样判断，计数一步更新。

暴力每个窗口重数一遍是 $O(nk)$。计数到 $k$ 已经是上限，可以直接返回。

## 参考代码

```python
def maxVowels(s: str, k: int) -> int:
    vowels = set("aeiou")
    cnt = sum(1 for c in s[:k] if c in vowels)
    best = cnt
    for i in range(k, len(s)):
        if best == k:
            break
        cnt += (s[i] in vowels) - (s[i - k] in vowels)
        best = max(best, cnt)
    return best


if __name__ == "__main__":
    assert maxVowels("abciiidef", 3) == 3
    assert maxVowels("aeiou", 2) == 2
    assert maxVowels("leetcode", 3) == 2
    assert maxVowels("rhythms", 4) == 0
    assert maxVowels("tryhard", 4) == 1
    assert maxVowels("a", 1) == 1
    print("ok")
```

## 复杂度

时间 $O(n)$，额外空间 $O(1)$（元音集合大小固定）。

## 边界

- 没有元音：答案 $0$。
- $k = |s|$：只有一个窗口，等于全串元音数。
- 窗口进出是同一类字符时计数不变，用布尔相减写法不必分情况。

## 追问

- **多次询问任意区间 `[l, r]` 的元音数？** 预处理前缀和 `pre[i+1] = pre[i] + isVowel(s[i])`，每次询问 `pre[r+1] - pre[l]`，$O(1)$ 回答。本题所有窗口的答案也可以这样算，只是多用 $O(n)$ 空间。

```python
def vowelPrefix(s):
    pre = [0]
    for c in s:
        pre.append(pre[-1] + (c in "aeiou"))
    return pre


def countVowels(pre, l, r):
    return pre[r + 1] - pre[l]
```

- **改成「元音不超过 $k$ 个的最长子串」？** 窗口长度不再固定，换成可变窗口：右端扩张，元音超过 $k$ 就收左端，写法同 `lc-1004-max-consecutive-ones-iii`。

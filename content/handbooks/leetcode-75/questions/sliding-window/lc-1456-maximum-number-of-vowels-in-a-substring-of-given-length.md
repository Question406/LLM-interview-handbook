---
id: lc-1456-maximum-number-of-vowels-in-a-substring-of-given-length
section: sliding-window
order: 2
level: A
title: LC 1456 · 定长子串中元音的最大数目
quick: >-
  定长滑窗计元音数，右边进来一个元音就加一，左边出去一个元音就减一，维护最大值；计数达到 $k$ 已是上限，可以提前返回。时间 $O(n)$，额外空间 $O(1)$。
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

## 题目描述

给定小写英文字符串 s 和窗口长度 k，考虑 s 中所有恰好由 k 个连续字符组成的子串，返回其中元音字母数量的最大值。此处元音只包括 a、e、i、o、u。

### 输入与输出

实现 `maxVowels(s, k) -> int`。只返回最多元音个数，不要求返回子串或其位置；字母 y 不算元音。

### 约束与约定

- `1 <= len(s) <= 100000`。
- s 只含小写英文字母，且 `1 <= k <= len(s)`。

### 示例

```text
输入：s = "abciiidef", k = 3
输出：3
```

示例长度为 3 的子串 iii 含三个元音，所以最大值为 3。

[官方原题与完整题面](https://leetcode.com/problems/maximum-number-of-vowels-in-a-substring-of-given-length/description/)。

## 解题思路与参考答案

## 题意

给小写字母串 `s` 和整数 $k$，在所有长度为 $k$ 的子串里，返回元音（`a e i o u`）个数的最大值。$1 \le k \le |s| \le 10^5$。

## 思路

这题用定长滑动窗口，和 `lc-643-maximum-average-subarray-i` 同一个骨架，只是把「和」换成「元音计数」。下标 `i` 进窗口时看 `s[i]` 是不是元音，`s[i-k]` 出窗口时同样判断，计数一步就能更新。暴力每个窗口重数一遍是 $O(nk)$。计数到 $k$ 已经是上限，可以直接返回。

拿 `"abciiidef"`、$k=3$ 走一遍。第一个窗口 `abc` 有 1 个元音，往右滑依次是 `bci` 1 个、`cii` 2 个、`iii` 3 个。3 等于 $k$，后面不用再看，答案 3。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert maxVowels("abciiidef", 3) == 3
assert maxVowels("aeiou", 2) == 2
assert maxVowels("leetcode", 3) == 2
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，额外空间 $O(1)$（元音集合大小固定）。

## 边界

没有元音时答案 $0$。

$k = |s|$ 时只有一个窗口，答案等于全串元音数。

窗口进出是同一类字符时计数不变，用布尔相减的写法就不必分情况。

## 追问

**多次询问任意区间 `[l, r]` 的元音数呢？**
预处理前缀和 `pre[i+1] = pre[i] + isVowel(s[i])`，每次询问算 `pre[r+1] - pre[l]`，$O(1)$ 回答。本题所有窗口的答案也可以这样算，只是多用 $O(n)$ 空间。

```python
def vowelPrefix(s):
    pre = [0]
    for c in s:
        pre.append(pre[-1] + (c in "aeiou"))
    return pre


def countVowels(pre, l, r):
    return pre[r + 1] - pre[l]
```

**改成「元音不超过 $k$ 个的最长子串」呢？**
窗口长度不再固定，换成可变窗口，右端扩张，元音超过 $k$ 就收左端，写法同 `lc-1004-max-consecutive-ones-iii`。

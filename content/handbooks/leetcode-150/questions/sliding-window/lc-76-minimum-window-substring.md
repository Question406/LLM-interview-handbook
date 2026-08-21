---
id: lc-76-minimum-window-substring
section: sliding-window
order: 4
level: S
title: LC 76 · 最小覆盖子串
quick: >-
  `need` 记 `t` 的缺额。右扩让 `valid` 升到 `required`，再尽可能左缩，并记录最短窗口。时间
  $O(|s|+|t|)$。
tags:
  - Sliding Window
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 76. 最小覆盖子串
    url: https://leetcode.cn/problems/minimum-window-substring/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题意

在 `s` 中找覆盖 `t` 全部字符（含重复次数）的最短子串。没有则返回空串。

## 思路

`need` 是 `t` 的计数，`required` 为其中不同字符数。右指针吃进 `s[right]`，当某个字符的窗口计数刚好顶到 `need` 时 `valid` 加一。`valid == required` 说明已覆盖，此时收缩左端：能缩就缩，并更新最短区间；左端字符掉到缺额以下则 `valid` 减一，停止收缩。

不要每次重新扫窗口比对。面试讲「覆盖计数 + 收缩」两段。

## 参考代码

```python
from collections import Counter


def minWindow(s: str, t: str) -> str:
    if not t or len(s) < len(t):
        return ""
    need = Counter(t)
    required = len(need)
    window: Counter[str] = Counter()
    valid = 0
    best_l, best_len = 0, len(s) + 1
    left = 0
    for right, ch in enumerate(s):
        window[ch] += 1
        if ch in need and window[ch] == need[ch]:
            valid += 1
        while valid == required:
            if right - left + 1 < best_len:
                best_l = left
                best_len = right - left + 1
            left_ch = s[left]
            window[left_ch] -= 1
            if left_ch in need and window[left_ch] < need[left_ch]:
                valid -= 1
            left += 1
    return "" if best_len == len(s) + 1 else s[best_l : best_l + best_len]


if __name__ == "__main__":
    assert minWindow("ADOBECODEBANC", "ABC") == "BANC"
    assert minWindow("a", "a") == "a"
    assert minWindow("a", "aa") == ""
    print("ok")
```

## 复杂度

时间 $O(|s|+|t|)$，左右指针各走一遍。空间 $O(\Sigma)$。

## 边界

- `t` 比 `s` 长：覆盖不可能，返回空串。
- `t` 有重复字符：`need` 记次数，只覆盖种类不够。
- 多个窗口一样短：记录最短时不要用 $\le$，用 $\lt$ 就能保留最先出现的那段。

## 追问

- **返回任意一个覆盖子串即可？** 不必维护 `best_len`。`valid` 第一次升到 `required` 时，当前 `[left, right]` 已经覆盖，直接 `return s[left:right+1]`。它通常不是最短，但合法。时间最好 $O(|t|)$ 量级就能停，最坏仍 $O(|s|+|t|)$。若还想顺手缩一下左端再返回，得到的是「以该右端为结尾的最短覆盖」，仍然不必扫完全文。

```python
from collections import Counter

def anyWindow(s, t):
    need, window = Counter(t), Counter()
    required, valid, left = len(need), 0, 0
    for right, ch in enumerate(s):
        window[ch] += 1
        if ch in need and window[ch] == need[ch]:
            valid += 1
        if valid == required:
            return s[left : right + 1]
    return ""
```

- **统计覆盖 `t` 的子串个数？** 模板从「最短」改成「计数」。右端推进后，一旦窗口覆盖，就说明以当前 `left` 为起点、右端 $\ge right$ 的子串都覆盖，答案加上 $|s|-right$，再收缩左端，重复直到窗口不再覆盖。这样每个合法 $[L,R]$ 恰好被数一次。时间 $O(|s|+|t|)$。不要对每个右端重新比对 `t`。若只要「以该右端结尾的覆盖子串个数」，覆盖后答案加 `left+1`（最短左端及其左边所有起点）。

```python
from collections import Counter

def countCovering(s, t):
    need, window = Counter(t), Counter()
    required, valid, left, ans = len(need), 0, 0, 0
    for right, ch in enumerate(s):
        window[ch] += 1
        if ch in need and window[ch] == need[ch]:
            valid += 1
        while valid == required:
            ans += len(s) - right
            left_ch = s[left]
            window[left_ch] -= 1
            if left_ch in need and window[left_ch] < need[left_ch]:
                valid -= 1
            left += 1
    return ans
```

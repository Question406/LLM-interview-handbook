---
id: lc-76-minimum-window-substring
section: sliding-window
order: 4
level: S
title: LC 76 · 最小覆盖子串
quick: >-
  滑动窗口加计数：`need` 记 `t` 里每个字符要几次，右端扩到 `valid` 达到
  `required`，说明所有字符都够了，再尽量收缩左端并记录最短窗口。每个字符只进出窗口一次，时间 $O(|s|+|t|)$。
tags:
  - Sliding Window
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 76. 最小覆盖子串
    url: 'https://leetcode.cn/problems/minimum-window-substring/'
    type: primary
  - title: 面试经典 150 题
    url: 'https://leetcode.cn/studyplan/top-interview-150/'
    type: reference
---

## 题目描述

给定字符串 s 和 t，在 s 中寻找一个最短的连续子串，使它包含 t 中全部字符，并满足每种字符至少出现 t 所要求的次数。可以包含额外字符，但不能把不相邻的位置拼接成结果。

### 接口与输出

实现 `minWindow(s: str, t: str) -> str`。存在覆盖子串时返回其文本，不存在时返回空字符串 `""`；字符区分大小写。

### 合法输入与约束

`1 <= len(s), len(t) <= 100000`，两个字符串只含大小写英文字母。t 中的重复字符必须按次数覆盖，例如 t 有两个 A 时，结果中也至少要有两个 A。

### 示例

```text
输入：s = "ADOBECODEBANC", t = "ABC"
输出："BANC"
```

以上为按原题规则整理的中文题面；[官方完整题目](https://leetcode.com/problems/minimum-window-substring/description/)。

## 解题思路与参考答案

## 题意

在 `s` 中找覆盖 `t` 全部字符（含重复次数）的最短子串。没有则返回空串。

## 思路

我会用滑动窗口：先扩右端直到覆盖，再收左端直到不再覆盖。每个字符只进出窗口一次，不用每次重新扫窗口去比对。

先准备计数。`need` 是 `t` 的字符计数，`required` 是其中不同字符的个数。右指针吃进 `s[right]`，某个字符的窗口计数刚好顶到 `need` 时，`valid` 加一。`valid == required` 说明已经覆盖，这时开始收缩左端，能缩就缩，边缩边更新最短区间。左端字符掉到所需次数以下时 `valid` 减一，停止收缩，回去继续扩右端。

拿 `s="ADOBECODEBANC"`、`t="ABC"` 看。右端走到下标 $5$ 的 `C` 时第一次覆盖，窗口是 `ADOBEC`，左端一缩掉 `A` 就不够了。右端走到下标 $10$ 的 `A` 时又覆盖，左端一路缩到 `CODEBA`。到最后的 `C`，左端能缩到 `BANC`，长度 $4$，就是答案。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert minWindow("ADOBECODEBANC", "ABC") == "BANC"
assert minWindow("a", "a") == "a"
assert minWindow("a", "aa") == ""
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(|s|+|t|)$，左右指针各走一遍。空间 $O(\Sigma)$。

## Edge Cases

`t` 比 `s` 长，不可能覆盖，返回空串。

`t` 有重复字符时，`need` 要记次数，光覆盖种类不够。

几个窗口一样短时，更新最短用 $\lt$，别用 $\le$，这样保留的是最先出现的那段。

## 追问

**返回任意一个覆盖子串就行呢？**
那就不用维护 `best_len`。`valid` 第一次升到 `required` 时，当前 `[left, right]` 已经覆盖，直接 `return s[left:right+1]`。它通常不是最短的，但合法。最好情况 $O(|t|)$ 量级就能停，最坏仍是 $O(|s|+|t|)$。如果还想顺手缩一下左端再返回，得到的是「以该右端结尾的最短覆盖」，同样不用扫完全文。

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

**要统计覆盖 `t` 的子串个数呢？**
模板从「最短」改成「计数」。右端推进后，窗口一旦覆盖，以当前 `left` 为起点、右端 $\ge right$ 的子串就都覆盖，答案加上 $|s|-right$，然后收缩左端，重复到窗口不再覆盖。这样每个合法的 $[L,R]$ 恰好被数一次，时间 $O(|s|+|t|)$，也不用对每个右端重新比对 `t`。如果只要「以该右端结尾的覆盖子串个数」，覆盖后答案加 `left+1`，也就是最短左端和它左边的所有起点。

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

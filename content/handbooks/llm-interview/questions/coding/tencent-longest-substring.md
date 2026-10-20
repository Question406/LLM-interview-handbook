---
id: tencent-longest-substring
section: coding
order: 213
level: A
title: 腾讯混元：最长无重复字符子串
quick: "用滑动窗口维护不重复的字符，并用哈希表记录每个字符上次出现的位置。右指针向前扫描；若字符在当前窗口内重复，就把左指针移到上次出现位置的下一位。时间为 $O(n)$，空间为 $O(\\Sigma)$。写代码前先说明窗口内字符始终唯一。"
tags:
  - Tencent
  - Hunyuan
  - Coding
  - Sliding Window
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 腾讯-混元大模型面经-华5硕
    url: https://www.nowcoder.com/feed/main/detail/692fed73109e4d31915e46d34d27c762
    type: candidate-first-hand
---

## 真题 / 考点说明

- 公司：腾讯 · 混元
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“手撕：最长无重复子串”**

LeetCode 3。和通用卡重复度高，但这是混元原帖原题，准备时按真题计时写一遍。滑动窗口需要始终满足一个条件：窗口 $[L,R]$ 内字符唯一，重复出现时 $L$ 跳到上次该字符的下一位。

## 思路

右指针 $R$ 从头扫到尾。用哈希记下每个字符上次出现的下标。若 `s[R]` 上次出现位置 $\ge L$，说明当前窗口内出现了重复字符，将 $L$ 移到 `last[s[R]]+1`。然后更新 `last` 和答案 `R-L+1`。

不要每次发现重复就从 $L$ 一位一位挪并删哈希，能过，但要讲清「直接跳」仍然正确：被跳过的字符即使还留在哈希里，也会因为下标 $\lt L$ 被忽略。

## 参考代码

```python
def length_of_longest_substring(s: str) -> int:
    last: dict[str, int] = {}
    left = 0
    ans = 0
    for right, ch in enumerate(s):
        if ch in last and last[ch] >= left:
            left = last[ch] + 1
        last[ch] = right
        width = right - left + 1
        if width > ans:
            ans = width
    return ans


if __name__ == "__main__":
    assert length_of_longest_substring("abcabcbb") == 3
    assert length_of_longest_substring("bbbbb") == 1
    assert length_of_longest_substring("pwwkew") == 3
    assert length_of_longest_substring("") == 0
    assert length_of_longest_substring("au") == 2
    print("ok")
```

## 复杂度

时间 $O(n)$，空间 $O(\Sigma)$。ASCII 可开 $128$ 数组；Unicode 用哈希。每个下标进出窗口常数次。

## 边界与追问

1. 空串、$1$ 字符、全相同、全不同、重复在窗口外（`abba` 答案是 $2$，不要把 $L$ 回退）。
2. 追问「至少包含 $k$ 种字符 / 最小覆盖子串」：还是滑窗，只是窗口需要满足的条件从无重复改为字符计数约束。
3. 追问字节流 / 超长串：窗口状态 $O(\Sigma)$，可以流式扫；不要把所有子串物化。Unicode 先约定按 code point 还是按 UTF-8 字节。

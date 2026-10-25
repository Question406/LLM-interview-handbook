---
id: tencent-longest-substring
section: coding
order: 213
level: A
title: 腾讯混元：最长无重复字符子串
quick: "用滑动窗口，让窗口里的字符始终不重复，再用哈希表记录每个字符上次出现的位置。右指针往前扫，字符如果在当前窗口内重复，就把左指针跳到上次出现位置的下一位。时间 $O(n)$，空间 $O(\\Sigma)$。"
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

## 题目描述

求一个字符串中不含重复字符的最长连续子串长度。子串必须连续，不能跳过中间字符。

下面的函数接口、输入表示和边界口径是本卡采用的手册练习约定；公开面经未披露完整题干的部分，不视为面试官原文。默认输入满足约束，无需额外编写非法输入校验。

### 接口与输入

实现 `length_of_longest_substring(s)`。s为Python字符串，允许为空；按Python字符元素比较相等性。

### 输出与约束

返回非负整数长度，不要求返回具体子串。空字符串结果为0；相同字符在不同位置再次出现时，不能同时属于同一个候选子串。

### 示例

```text
"abcabcbb" -> 3（例如"abc"）
"pwwkew" -> 3（例如"wke"，"pwke"不连续，不能计4）
"bbbbb" -> 1
"" -> 0
```

## 解题思路与参考答案

滑动窗口加一张「字符上次出现位置」的哈希表：右指针一路往前扫，如果当前字符上次出现的位置还在窗口里，就把左指针直接跳到那个位置的下一位，然后更新答案。窗口 $[L,R]$ 里的字符始终唯一，写代码前先把这个条件说出来。

这是腾讯混元的题，来自牛客候选人原帖，可信度 A，原话是**“手撕：最长无重复子串”**，就是 LeetCode 3。和通用卡重复度很高，但这是混元原帖的原题，准备时按真题计时写一遍。

## 思路

右指针 $R$ 从头扫到尾，哈希表记下每个字符上次出现的下标。如果 `s[R]` 上次出现的位置 $\ge L$，说明窗口里出现了重复，把 $L$ 移到 `last[s[R]]+1`。然后更新 `last` 和答案 `R-L+1`。比如 `"abcabcbb"`，扫到第二个 `a` 时 $L$ 从 0 跳到 1，窗口一直保持 3 个字符，答案是 3。

也可以发现重复后让 $L$ 一位一位地挪、顺便删哈希，能过。用直接跳的写法就要讲清为什么仍然正确：被跳过的字符就算还留在哈希里，下标也 $\lt L$，会被忽略。

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

## 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert length_of_longest_substring("abcabcbb") == 3` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

## 复杂度

时间 $O(n)$，空间 $O(\Sigma)$。ASCII 可以开 $128$ 的数组，Unicode 用哈希。每个下标进出窗口常数次。

## 追问

**要测哪些边界？**
空串、$1$ 个字符、全相同、全不同，还有重复出现在窗口外的情况：`abba` 答案是 $2$，$L$ 不能回退。

**至少包含 $k$ 种字符、最小覆盖子串怎么做？**
还是滑窗，只是窗口要满足的条件从无重复换成了字符计数约束。

**字节流或者超长串呢？**
窗口状态只有 $O(\Sigma)$，可以流式扫，别把所有子串物化。Unicode 要先约定按 code point 还是按 UTF-8 字节算。

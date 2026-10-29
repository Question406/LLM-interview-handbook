---
id: meta-longest-valid-parentheses
section: meta
order: 900
level: A
title: "Meta：Longest Valid Parentheses 与 sentinel index"
quick: "我会在 stack 底部放一个 sentinel index。遇到左括号存位置，遇到右括号先匹配；如果 stack 仍非空，当前位置到 stack top 之间就是一段合法 substring。"
companies:
  - meta
tags:
  - "Frontier Coding 2026-10-28"
  - 完整编程练习
  - "候选人报告改编"
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: "候选人自述：Meta ML Research Scientist loop"
    url: "https://www.reddit.com/r/leetcode/comments/1r37w7q/meta_ml_research_scientist_interview_experience/"
    type: interview
  - title: "LeetCode 32"
    url: "https://leetcode.com/problems/longest-valid-parentheses/"
    type: primary
---

## 题目描述

来源：同一位 Meta ML Research Scientist 候选人自述，standard coding 第二题为 LC 32。以下为可独立练习的题面重述。

### 输入、接口与规则

实现 `longest_valid_parentheses(text) -> int`。输入是只包含 `(` 与 `)` 的字符串，可为空，长度不超过 200000。返回最长连续、正确匹配括号 substring 的字符数；不能删除或重排字符，答案不是所有匹配 pairs 的总数。

正确匹配要求在该 substring 的每个 prefix 中左括号数不少于右括号，且最后两者相等。返回一个整数，不修改输入。目标时间 `O(N)`；可以使用 stack 或说明等价的线性方法。请解释遇到无法匹配的右括号时，下一段合法 substring 从哪里重新开始。

### 输入输出示例

```text
输入 ")()())" -> 返回 4，对应 "()()"。
输入 "(()" -> 2；输入 "()(())" -> 6；空字符串 -> 0。
```

## 回答思路

> **输入与任务：** 答案是连续 substring 的长度。  
> **做法与原因：** Stack 存未匹配位置，用 -1 或最近非法位置作长度计算的起点。  
> **正确性检查：** 用小字符串的穷举 oracle 比较，检查连续段和提前出现的右括号。

## 解题思路与参考答案

我会在 stack 底部放一个 sentinel index。遇到左括号存位置，遇到右括号先匹配；如果 stack 仍非空，当前位置到 stack top 之间就是一段合法 substring。

如果 stack 被清空，说明这个右括号无法匹配，就把它作为新的起点。这样不会把前后两段不连续的括号错误合并。

### 完整参考实现

```python
def longest_valid_parentheses(text):
    stack, longest = [-1], 0
    for index, char in enumerate(text):
        if char == "(":
            stack.append(index)
        else:
            stack.pop()
            if stack:
                longest = max(longest, index - stack[-1])
            else:
                stack.append(index)
    return longest
```

## 简单测试怎么写

将实现与下面测试按顺序保存为 `solution.py`，使用安装 NumPy/PyTorch 的 Python 运行 `python solution.py`。先核对题面的手算输出，再执行下列 assertions。

```python
for text, expected in [
    ("", 0),
    ("(()", 2),
    (")()())", 4),
    ("()(())", 6),
    ("(((", 0),
    (")))", 0),
    ("())(())", 4),
    ("(()())()", 8),
]:
    assert longest_valid_parentheses(text) == expected
# Independent quadratic oracle for all strings of length <= 9.
import itertools


def brute(text):
    best = 0
    for left in range(len(text)):
        balance = 0
        for right in range(left, len(text)):
            balance += 1 if text[right] == "(" else -1
            if balance < 0:
                break
            if balance == 0:
                best = max(best, right - left + 1)
    return best


for length in range(10):
    for chars in itertools.product("()", repeat=length):
        text = "".join(chars)
        assert longest_valid_parentheses(text) == brute(text)
print("Meta parentheses: passed")
```

## 复杂度与追问

时间 `O(N)`，最坏空间 `O(N)`。用 stack 数量或 pairs 数无法直接得到最长连续长度，必须保留位置；也可以讨论两次扫描的 constant-space 方法。

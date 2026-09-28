---
id: lc-394-decode-string
section: stack
order: 3
level: S
title: LC 394 · 字符串解码
quick: >-
  栈里存「进括号前的字符串和倍数」。遇到 `[` 把当前串和数字压栈并清空；遇到 `]` 弹出，拼成 `prev + cur * k`。多位数字要边读边乘
  10。时间和空间都是 $O(L)$，$L$ 为解码后长度。
tags:
  - String
  - Stack
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27
sources:
  - title: 394. Decode String
    url: https://leetcode.com/problems/decode-string/
    type: primary
  - title: LeetCode 75
    url: https://leetcode.com/studyplan/leetcode-75/
    type: reference
---

## 题意

编码规则是 `k[encoded_string]`，表示方括号里的串重复 $k$ 次，可以嵌套。输入保证合法：没有多余空格，括号匹配，数字只表示重复次数（原文里不含数字）。返回解码后的字符串。$|s| \le 30$，$k \le 300$，输出长度不超过 $10^5$。

## 思路

嵌套括号是典型的栈。维护当前正在拼的串 `cur` 和正在读的数字 `num`。

- 数字：`num = num * 10 + d`，`"12[a]"` 这种多位数靠这一步。
- `[`：进入新一层，把 `(cur, num)` 压栈，然后两者清空。
- `]`：本层结束，弹出 `(prev, k)`，`cur = prev + cur * k`。
- 字母：追加到 `cur`。

每层只需要记住「外层前缀」和「本层倍数」，所以一个存二元组的栈就够。递归写法等价，括号深度就是递归深度。

## 参考代码

```python
from typing import List, Tuple


def decodeString(s: str) -> str:
    stack: List[Tuple[str, int]] = []
    cur, num = "", 0
    for c in s:
        if c.isdigit():
            num = num * 10 + int(c)
        elif c == "[":
            stack.append((cur, num))
            cur, num = "", 0
        elif c == "]":
            prev, k = stack.pop()
            cur = prev + cur * k
        else:
            cur += c
    return cur


if __name__ == "__main__":
    assert decodeString("3[a]2[bc]") == "aaabcbc"
    assert decodeString("3[a2[c]]") == "accaccacc"
    assert decodeString("2[abc]3[cd]ef") == "abcabccdcdcdef"
    assert decodeString("abc3[cd]xyz") == "abccdcdcdxyz"
    assert decodeString("10[a]") == "a" * 10
    assert decodeString("leet") == "leet"
    print("ok")
```

## 复杂度

时间 $O(L)$，$L$ 是输出长度（字符串重复与拼接的总量受输出长度约束）；额外空间 $O(L)$。严格说深层嵌套时 `prev + cur * k` 会重复拷贝，最坏多一个嵌套深度的因子，本题数据下可以忽略。

## 边界

- 多位数字：`"10[a]"`、`"100[ab]"`，不能只取一位。
- 括号外的字母：开头、结尾、两段括号之间都可能有，直接进 `cur`。
- 没有任何括号：原样返回。

## 追问

- **递归写法？** 函数从下标 `i` 开始解析，遇到 `]` 或结尾返回「本层结果和下一个下标」；遇到 `k[` 就递归解析内层，再乘 $k$ 接上。

```python
def decodeStringRec(s):
    def parse(i):
        out, num = [], 0
        while i < len(s):
            c = s[i]
            if c.isdigit():
                num = num * 10 + int(c)
            elif c == "[":
                inner, i = parse(i + 1)
                out.append(inner * num)
                num = 0
            elif c == "]":
                return "".join(out), i
            else:
                out.append(c)
            i += 1
        return "".join(out), i

    return parse(0)[0]
```

- **输出巨大，只要第 $k$ 个字符？** 不能真的展开。先算出每段展开后的长度，再从外往里用长度定位（取模）到具体字符，思路同 LC 880。

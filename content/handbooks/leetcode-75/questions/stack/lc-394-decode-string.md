---
id: lc-394-decode-string
section: stack
order: 3
level: S
title: LC 394 · 字符串 decoding
quick: >-
  嵌套括号用栈，栈里存「进括号前的字符串和倍数」。遇到 `[` 把当前串和数字压栈并清空；遇到 `]` 弹出，拼成 `prev + cur *
  k`；多位数字要边读边乘 10。时间和空间都是 $O(L)$，$L$ 为 decoding 后长度。
tags:
  - String
  - Stack
  - Medium
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-27T00:00:00.000Z
sources:
  - title: 394. Decode String
    url: 'https://leetcode.com/problems/decode-string/'
    type: primary
  - title: LeetCode 75
    url: 'https://leetcode.com/studyplan/leetcode-75/'
    type: reference
---

## 题目描述

一个字符串用形如 k[内容] 的写法表示把方括号内的内容重复 k 次；这种写法可以嵌套，括号外普通字母直接保留。给定合法编码，返回完整 decoding 后的字符串。多位数字表示一个重复次数，不是连续多个独立指令。

### 输入与输出

实现 `decodeString(s) -> str`，输出 decoding 后的全部小写字母。数字只用于重复次数，原始文本不含数字；不能把方括号或次数数字保留到结果中。

### 约束与约定

- `1 <= len(s) <= 30`；字符仅为小写英文字母、数字、方括号。
- 每个重复次数在 1 到 300 之间。
- 输入保证括号匹配、语法合法，decoding 后长度不超过 100000。

### 示例

```text
输入：s = "3[a]2[bc]"
输出："aaabcbc"
```

示例中的 3[a] 生成 aaa，2[bc] 生成 bcbc，连接后得到 aaabcbc。

[官方原题与完整题面](https://leetcode.com/problems/decode-string/description/)。

## 解题思路与参考答案

## 题意

编码规则是 `k[encoded_string]`，表示方括号里的串重复 $k$ 次，可以嵌套。输入保证合法：没有多余空格，括号匹配，数字只表示重复次数（原文里不含数字）。返回 decoding 后的字符串。$|s| \le 30$，$k \le 300$，输出长度不超过 $10^5$。

## 思路

嵌套括号是典型的栈。我维护当前正在拼的串 `cur` 和正在读的数字 `num`，每进一层括号就把外层的状态压栈。读到数字时 `num = num * 10 + d`，`"12[a]"` 这种多位数靠这一步。读到 `[` 说明进入新一层，把 `(cur, num)` 压栈，两者清空。读到 `]` 说明本层结束，弹出 `(prev, k)`，`cur = prev + cur * k`。字母直接追加到 `cur`。

每层只需要记住「外层前缀」和「本层倍数」，所以一个存二元组的栈就够。递归写法等价，括号深度就是递归深度。

拿 `"3[a2[c]]"` 走一遍。读到 3 和 `[`，压入 `("", 3)`；读 `a`，`cur = "a"`；读到 2 和 `[`，压入 `("a", 2)`，`cur` 清空；读 `c`。第一个 `]` 弹出 `("a", 2)`，`cur = "a" + "cc" = "acc"`；第二个 `]` 弹出 `("", 3)`，`cur` 变成 `"accaccacc"`。

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

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert decodeString("3[a]2[bc]") == "aaabcbc"
assert decodeString("3[a2[c]]") == "accaccacc"
assert decodeString("2[abc]3[cd]ef") == "abcabccdcdcdef"
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(L)$，$L$ 是输出长度（字符串重复与拼接的总量受输出长度约束）；额外空间 $O(L)$。严格说深层嵌套时 `prev + cur * k` 会重复拷贝，最坏多一个嵌套深度的因子，本题数据下可以忽略。

## Edge Cases

数字可能有好几位，比如 `"10[a]"`、`"100[ab]"`，要边读边累积，只取一位会错。

括号外也会有字母，开头、结尾、两段括号之间都可能有，直接进 `cur`。

没有任何括号时原样返回。

## 追问

**递归怎么写？**
函数从下标 `i` 开始解析，遇到 `]` 或结尾就返回「本层结果和下一个下标」；遇到 `k[` 就递归解析内层，再乘 $k$ 接上。

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

**输出巨大，只要第 $k$ 个字符呢？**
那就不能真的展开。先算出每段展开后的长度，再从外往里用长度定位（取模）到具体字符，思路同 LC 880。

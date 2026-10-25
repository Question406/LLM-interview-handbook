---
id: lc-68-text-justification
section: array-string
order: 24
level: A
title: LC 68 · 文本左右对齐
quick: "贪心地每行尽量多装词，装不下就封行。中间行把多余空格均匀分进词缝，除不尽的余数从左到右每缝多给一格；最后一行和只有一个词的行左对齐、右侧补空格。时间 $O(n)$。"
tags:
  - String
  - Greedy
  - Hard
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 68. 文本左右对齐
    url: https://leetcode.cn/problems/text-justification/
    type: primary
  - title: 面试经典 150 题
    url: https://leetcode.cn/studyplan/top-interview-150/
    type: reference
---

## 题目描述

给定按顺序排列的单词和固定行宽，把它们排成每行恰好 maxWidth 个字符的文本。每行必须尽可能容纳更多完整单词，不能拆词或改变词序。除了最后一行外，文本左右对齐：所有额外空格分配到词间，尽量平均；无法平均时左边的间隔比右边多一个空格。最后一行左对齐，词间只放一个空格，其余空格补在行末；只有一个词的行也在右侧补齐。

### 输入与输出

实现 `fullJustify(words, maxWidth) -> list[str]`。返回排好版的行列表，每个字符串长度必须严格等于 maxWidth，包括行尾空格。

### 约束与约定

- `1 <= len(words) <= 300`。
- 每个单词由非空格字符组成，长度在 1 到 20 之间，且不超过 maxWidth。
- `1 <= maxWidth <= 100`。

### 示例

```text
输入：words = ["This", "is", "an", "example", "of", "text", "justification."], maxWidth = 16
输出：[
   "This    is    an",
   "example  of text",
   "justification.  "
]
```

示例输出中引号内的连续空格及末尾空格都是答案的一部分。

[官方原题与完整题面](https://leetcode.com/problems/text-justification/description/)。

## 解题思路与参考答案

## 题意

单词数组 `words` 与行宽 `maxWidth`。把单词排成左右对齐的文本：每行恰好 `maxWidth` 个字符；尽量多装完整单词；词之间至少一个空格。最后一行左对齐，右侧补空格。

## 思路

我会贪心地一行一行装：每行尽量加入完整单词，下一个词加上必要的空格会超过行宽，就先输出当前行。封行时分两种情况。一行只有一个词、或者是最后一行，就左对齐，词间一个空格，右边补空。中间的多词行要把多余空格 `spaces` 分到 `gaps = 词数-1` 个缝里，每缝至少 `spaces // gaps`，前 `spaces % gaps` 个缝再多一格。

拿第一个测试走一遍：`maxWidth = 16`，第一行装下 `This`、`is`、`an`，再加 `example` 就超了；三个词共 $8$ 个字符，剩下 $8$ 个空格分进 $2$ 个缝，每缝 $4$ 格，得到 `This    is    an`。

写的时候先写「怎么判断一行装得下」，再写空格分配，末行单独处理。

## 参考代码

```python
from typing import List


def fullJustify(words: List[str], maxWidth: int) -> List[str]:
    def flush(line: List[str], width: int, last: bool) -> str:
        if last or len(line) == 1:
            s = " ".join(line)
            return s + " " * (maxWidth - len(s))
        gaps = len(line) - 1
        spaces = maxWidth - width
        q, r = divmod(spaces, gaps)
        parts = []
        for i, w in enumerate(line[:-1]):
            extra = q + (1 if i < r else 0)
            parts.append(w)
            parts.append(" " * extra)
        parts.append(line[-1])
        return "".join(parts)

    ans: List[str] = []
    line: List[str] = []
    width = 0
    for w in words:
        need = width + len(w) + len(line)
        if need > maxWidth:
            ans.append(flush(line, width, False))
            line = [w]
            width = len(w)
        else:
            line.append(w)
            width += len(w)
    ans.append(flush(line, width, True))
    return ans


if __name__ == "__main__":
    assert fullJustify(
        ["This", "is", "an", "example", "of", "text", "justification."], 16
    ) == [
        "This    is    an",
        "example  of text",
        "justification.  ",
    ]
    assert fullJustify(
        ["What", "must", "be", "acknowledgment", "shall", "be"], 16
    ) == [
        "What   must   be",
        "acknowledgment  ",
        "shall be        ",
    ]
    assert fullJustify(
        [
            "Science",
            "is",
            "what",
            "we",
            "understand",
            "well",
            "enough",
            "to",
            "explain",
            "to",
            "a",
            "computer.",
            "Art",
            "is",
            "everything",
            "else",
            "we",
            "do",
        ],
        20,
    ) == [
        "Science  is  what we",
        "understand      well",
        "enough to explain to",
        "a  computer.  Art is",
        "everything  else  we",
        "do                  ",
    ]
    print("ok")
```

## 简单测试怎么写

把上面的参考代码保存为 `solution.py`，下面的代码放在同一个文件末尾。先准备输入，再调用本题函数，最后用 `assert` 比较实际值和预期值。

先手算一个普通输入，再补题目允许的最小输入和一个容易写错的分支。每条断言都写出明确预期值；只打印结果还需要人眼判断，`assert` 能在不符合预期时直接报错。

```python
assert fullJustify(
        ["This", "is", "an", "example", "of", "text", "justification."], 16
    ) == [
        "This    is    an",
        "example  of text",
        "justification.  ",
    ]
assert fullJustify(
        ["What", "must", "be", "acknowledgment", "shall", "be"], 16
    ) == [
        "What   must   be",
        "acknowledgment  ",
        "shall be        ",
    ]
assert fullJustify(
        [
            "Science",
            "is",
            "what",
            "we",
            "understand",
            "well",
            "enough",
            "to",
            "explain",
            "to",
            "a",
            "computer.",
            "Art",
            "is",
            "everything",
            "else",
            "we",
            "do",
        ],
        20,
    ) == [
        "Science  is  what we",
        "understand      well",
        "enough to explain to",
        "a  computer.  Art is",
        "everything  else  we",
        "do                  ",
    ]
print("simple tests passed")
```

运行 `python3 solution.py`，全部断言通过后会输出 `simple tests passed`；失败时按报错行检查该用例的输入和预期值。请用普通模式运行，`python3 -O` 会跳过 `assert`。

## 复杂度

时间 $O(n)$，$n$ 为所有单词字符数（每个词进出一行一次）。额外空间 $O(\texttt{maxWidth})$ 级（当前行）。

## 边界

一行只装得下一个词、且这个词长度正好等于 `maxWidth` 时，没有词缝，右边也不补，整行就是这个词。最后一行有多个词时，词间只留一个空格、右侧补空，不能两端拉齐。多余空格不能被词缝整除时，左边若干个缝会多一格，右边的缝少一格。

## 追问

**为什么多出来的空格从左边加？**
这是题面规定的：空格尽量均匀，不能均分时左边的词缝优先多一格。判题和常见排版习惯都这样，也有编辑器会把余数放中间或靠右。实现上先把「词间至少一格」算进行宽，封行时把剩下的 `spaces` 分到 `gaps = 词数-1` 个缝：`q, r = divmod(spaces, gaps)`，下标 $0\ldots r-1$ 的缝是 $q+1$，其余是 $q$。别用浮点除，余数也别从右边加。只有一个单词的行和最后一行不走这套分配，直接左对齐。时间仍随单词总长线性。

```python
def gap_widths(spaces, gaps):
    q, r = divmod(spaces, gaps)
    return [q + (1 if i < r else 0) for i in range(gaps)]
```

**两端对齐和左对齐分别什么时候用？**
只有「不是最后一行、且这一行至少两个词」才两端对齐：空格全分进词缝，行尾没有多余空格，行长恰好 `maxWidth`。最后一行要像普通段落结尾，词间一个空格、右侧补空，就是左对齐。一行只有一个词时没有词缝可分，也只能左对齐、右边补空，不然会在词前塞空格，变成右对齐。代码里先抽一个 `flush(line, last)`：`last or len(line)==1` 走 `" ".join` 再右补，否则走 `divmod`。最后一行也被均匀拉开、只有一个词的行忘了补到 `maxWidth`，是最常见的两个错。判断能不能再塞下一个词时，已经占用的词间空格是 `len(line)` 个，别当成 $0$。

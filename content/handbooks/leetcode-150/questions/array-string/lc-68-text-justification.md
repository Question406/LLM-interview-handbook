---
id: lc-68-text-justification
section: array-string
order: 24
level: A
title: LC 68 · 文本左右对齐
quick: >-
  贪心尽量多装词。最后一行左对齐；中间行把空格均匀塞进词缝，多出来的空格从左到右多给一格。时间
  $O(n)$。
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

## 题意

单词数组 `words` 与行宽 `maxWidth`。把单词排成左右对齐的文本：每行恰好 `maxWidth` 个字符；尽量多装完整单词；词之间至少一个空格。最后一行左对齐，右侧补空格。

## 思路

贪心：逐行累加单词，再放下一个会超宽就封行。一行只有一个词，或是最后一行：左对齐，词间一个空格，右边补空。中间多词行：多余空格 `spaces` 要分到 `gaps = 词数-1` 个缝里，每缝至少 `spaces // gaps`，前 `spaces % gaps` 个缝多一格。

白板我会先写「怎么判断一行装得下」，再写空格分配，最后单独处理末行。

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

## 复杂度

时间 $O(n)$，$n$ 为所有单词字符数（每个词进出一行一次）。额外空间 $O(\texttt{maxWidth})$ 级（当前行）。

## 边界

- 一行只装得下一个词且该词长度等于 `maxWidth`：没有词缝，右边也不补，整行就是这个词。
- 最后一行有多个词：词间只留一个空格，右侧补空，不能两端拉齐。
- 多余空格不能被词缝整除：左边若干缝会多一格，右边缝少一格。

## 追问

- **为什么多出来的空格要从左边加？** 题面规定：空格尽量均匀，不能均分时左边的词缝优先多一格。这是为了和判题、常见排版习惯一致，不是唯一美学解，有的编辑器会把余数放中间或靠右。实现上先把「词间至少一格」算进行宽，封行时剩下的 `spaces` 再分到 `gaps = 词数-1` 个缝：`q, r = divmod(spaces, gaps)`，下标 $0\ldots r-1$ 的缝是 $q+1$，其余是 $q$。不要用浮点除，也不要从右边加余数。单词语和最后一行根本不走这套分配，走左对齐。时间仍随单词总长线性。

```python
def gap_widths(spaces, gaps):
    q, r = divmod(spaces, gaps)
    return [q + (1 if i < r else 0) for i in range(gaps)]
```

- **两端对齐和左对齐分别何时用？** 只有「非最后一行且这一行至少两个词」才两端对齐：空格全部分进词缝，行尾没有多余空格，行长恰好 `maxWidth`。最后一行要看起来像普通段落结尾，词间一个空格、右侧补空，这是左对齐。一行只有一个词时没有词缝可分，也只能左对齐、右边补空，否则会在词前塞空格变成右对齐。白板写代码时我先抽 `flush(line, last)`：`last or len(line)==1` 走 `" ".join` 再右补，否则走 `divmod`。这块容易栽：最后一行也均匀拉空格，以及单词语忘了补到 `maxWidth`。判断能否再塞下一个词时，别忘了已经占用的词间空格是 `len(line)` 而不是 $0$。

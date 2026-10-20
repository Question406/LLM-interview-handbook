---
id: p3a-cursor-streaming-markdown-code-parser
section: coding
order: 809
level: A
title: "Cursor：跨 chunk 的 Markdown Code Parser"
quick: "用状态机区分普通文本、行内代码和代码块，并把跨 chunk 的连续反引号先攒着，等长度确定后再解释；正文统一做 HTML 转义，finish 时闭合未闭合的代码。"
companies:
  - ai-labs
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - cursor
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Cursor：跨 chunk 的 Markdown Code Parser"
    url: https://www.1point3acres.com/interview/problems/34db21b4-effb-505b-8bc3-d02502828352
    type: secondary
---

## 题目

LLM 的输出是一块一块流式到达的。写一个增量解析器，把其中的行内代码（单个反引号）和代码块（三个反引号）转成 HTML，每收到一块就输出已经能确定的部分。难点在于反引号可能被切在两块之间。

> 来源：一亩三分地题目详情页（2026-10-18 读取），题面是网站从面经整理的，没有逐条核对原帖；网站收录不等于公司官方确认。下面的接口、约束和测试是手册补的练习约定。

## 思路

用一个状态机，状态有三种：普通文本、行内代码、代码块。另外记一个计数：目前攒着、还没确定长度的连续反引号有几个。

为什么要攒着：如果一块以一个反引号结尾，它可能是行内代码的开头，也可能是三个反引号的第一个，要等到看见下一个非反引号字符（或者输入结束）才知道这个 run 有多长。提前输出 `<code>` 的话，后面再来两个反引号就没法改了。

run 长度确定后，按当前状态解释它：

- 普通文本里，1 个反引号开始行内代码，3 个开始代码块，其他长度原样输出；
- 行内代码里，1 个反引号结束；
- 代码块里，只有 3 个反引号才结束，单个反引号就是普通字符，不会嵌套解析行内代码。

所有正文都要做 HTML 转义，只有解析器自己生成的固定标签是原样输出的，这样代码内容不会变成可执行的 HTML。流结束时要显式 `finish()`，把没闭合的代码闭合掉。

测试时要把分隔符切在每一个可能的位置，再加上空块和未闭合的情况。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `Markdown().feed(chunk) -> str`：处理一块输入，返回这一块之后可以确定的 HTML。所有返回值依次拼起来就是最终 HTML。
- `finish() -> str`：结束输入，确定最后的反引号 run 并闭合未闭合的代码。重复调用返回空字符串；`finish()` 之后再 `feed` 抛 `ValueError`。
- 只支持恰好 1 个反引号的行内代码和恰好 3 个反引号的代码块，其他长度的反引号 run 按字面输出。不解析标题、链接、强调等其他 Markdown 语法。
- 所有文本做 HTML 转义。总文本长度不超过 $10^5$。

### 输入输出示例

```text
feed("a`<x>`b") + finish()     -> "a<code>&lt;x&gt;</code>b"
"```x`y```" 逐字符 feed        -> "<pre><code>x`y</code></pre>"
feed("`unclosed") + finish()   -> "<code>unclosed</code>"
```

### 解题思路与正确性

反引号 run 在结束之前一个字符也不输出，所以无论输入在哪里被切开，解析器看到的 run 长度都和一次性输入时相同，输出也就相同。测试把 `` a`<x>`b `` 在每个位置切成两块，验证结果都一致。

状态只在 run 被解释时切换，代码块状态下单个反引号不会触发任何切换，所以不会误把块内内容当作行内代码。

### 完整参考实现（Python 3）

```python
import html

PLAIN, INLINE, BLOCK = "plain", "inline", "block"


class Markdown:
    """流式解析 `inline code` 和 ```fenced code```，feed 返回这一段已经能确定的 HTML。"""

    def __init__(self):
        self.mode = PLAIN
        self.pending_ticks = 0  # 还没结束的连续反引号个数，可能跨 chunk
        self.finished = False

    def _flush_ticks(self):
        """反引号 run 已经结束：按当前模式决定它是开/闭标记，还是字面量。"""
        run = self.pending_ticks
        self.pending_ticks = 0
        if run == 0:
            return ""
        if self.mode == PLAIN and run == 1:
            self.mode = INLINE
            return "<code>"
        if self.mode == PLAIN and run == 3:
            self.mode = BLOCK
            return "<pre><code>"
        if self.mode == INLINE and run == 1:
            self.mode = PLAIN
            return "</code>"
        if self.mode == BLOCK and run == 3:
            self.mode = PLAIN
            return "</code></pre>"
        return "`" * run  # 其他长度（以及代码块里的单个反引号）原样输出

    def feed(self, chunk):
        if self.finished:
            raise ValueError("feed() called after finish()")
        out = []
        for char in chunk:
            if char == "`":
                # 先攒着：只有看到下一个非反引号字符，才知道这个 run 有多长
                self.pending_ticks += 1
                continue
            out.append(self._flush_ticks())
            out.append(html.escape(char, quote=False))
        return "".join(out)

    def finish(self):
        """结束输入：确定最后一个反引号 run，并自动闭合未闭合的代码。可重复调用。"""
        if self.finished:
            return ""
        out = self._flush_ticks()
        if self.mode == INLINE:
            out += "</code>"
        elif self.mode == BLOCK:
            out += "</code></pre>"
        self.mode = PLAIN
        self.finished = True
        return out
```

### 可执行测试

```python
def parse(chunks):
    parser = Markdown()
    return "".join(parser.feed(chunk) for chunk in chunks) + parser.finish()

# 行内代码：在每个位置切成两块，结果都一样
text = "a`<x>`b"
expected = "a<code>&lt;x&gt;</code>b"
for cut in range(len(text) + 1):
    assert parse([text[:cut], text[cut:]]) == expected

# 代码块：逐字符喂入，块内的单个反引号是普通字符
text = "```x`y```"
assert parse(list(text)) == "<pre><code>x`y</code></pre>"

# 未闭合的代码在结束时自动闭合
assert parse(["`unclosed"]) == "<code>unclosed</code>"

# 普通文本也要转义
assert parse(["<script>&"]) == "&lt;script&gt;&amp;"

# 两个反引号不是标记，原样输出；空 chunk 无影响
assert parse(["a``b", ""]) == "a``b"

# finish 可重复调用，之后不能再 feed
parser = Markdown()
parser.feed("x")
assert parser.finish() == ""
assert parser.finish() == ""
try:
    parser.feed("y")
except ValueError:
    pass
else:
    raise AssertionError("feed after finish should raise ValueError")
```

### 复杂度与追问

设输入总长为 T。每个字符处理一次，时间 O(T)；解析器自身状态是 O(1)，不算返回的字符串。

- 一段非常长的反引号 run 要等它结束才能输出，所以输出会有延迟；对 UI 来说可以先渲染已确定的部分，再在 run 结束时补上。
- 扩展到完整 CommonMark 时，代码块的分隔符可以是 3 个以上的反引号或波浪号，开头还可以带语言标签，结束条件和嵌套规则都要重新定义，不能把这个练习当成完整的 Markdown 实现。

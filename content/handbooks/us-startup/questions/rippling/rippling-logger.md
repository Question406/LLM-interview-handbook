---
id: rippling-logger
section: rippling
order: 2
level: A
title: Rippling：AI coding 电面，logger 先删子串再截断
quick: >-
  公开帖能核对的只有两步：打印前删掉配置的字符串的所有出现，再把消息截断，顺序是先删后截。2026 年这轮电面可选 AI coding，每改一个功能都要能 print 出当前结果。自己先定函数和顺序，不要把整段题干贴进模型。
tags:
  - Rippling
  - Coding
  - AI Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-22
sources:
  - title: Rippling SDE II 电面，logger，2026
    url: https://www.1point3acres.com/bbs/thread-1176930-1-1.html
    type: candidate-first-hand
  - title: Rippling Offer Received, AI Coding Experience
    url: https://leetcode.com/discuss/post/7649290
    type: candidate-first-hand
  - title: Implement logger and card ranking
    url: https://prachub.com/coding-questions/implement-logger-and-card-ranking
    type: secondary
---

## 题目描述

本题采用手册重构练习约定；下列接口、边界和样例是为了独立完成练习而明确的要求，不代表面试帖逐字题面。

实现一个可配置日志器，每次打印消息前先删指定子串，再截断，并同时返回最终打印文本。公开帖能确认的核心是这两步；本练习不增加搜索、存储或大写转换命令。

### 输入与接口

实现 Logger()，公开配置属性 remove 与 limit，初始均为None；提供 log(message)。message为字符串；remove为待删的非空字符串、空字符串或None；limit为非负整数或None，按Python字符串字符数截断。调用者直接更新配置属性。

### 输出与约束

log先对原message做一次从左到右不重叠的子串删除，再保留前limit个字符。remove为None或空串时不删除，limit为None时不截断，limit=0时结果为空串。大小写敏感。返回处理后的字符串，并向标准输出打印同一字符串及一个换行。

删除只执行一次，不反复消除删除后新拼出的匹配。配置仅影响之后的log，不回溯修改之前输出。不修改传入字符串，也无需保存历史消息。所有配置输入均合法，不要求测试负数长度。

### 示例

```text
logger=Logger()，logger.remove="xx"，logger.limit=3
logger.log("xxabcdef") -> 返回"abc"，打印"abc\n"
logger.remove=None
logger.log("xxabcdef") -> 返回"xxa"，打印"xxa\n"
logger.limit=0
logger.log("hello") -> 返回""，打印"\n"
```

## 解题思路与参考答案

这题能核对的只有两步：打印前删掉配置字符串的所有出现，再把消息截断，顺序是先删后截。我会把配置状态和变换分开写，每加一个功能就 print 一次；用 AI 的话，自己先定好函数和顺序再让模型填，别把整段题干贴进去。

帖子是 2026 年 4–6 月的 Rippling SDE II，海投，电面选了 AI coding。作者说题目就是地里那道 logger：打印前去掉配置字符串的每一次出现，再截断消息，每个功能做完都要能 print。帖子后半被截断了，后面还有什么命令，原文没公开。他两轮 coding 都碰到同一件事：面试官不建议把题目全部贴给 ChatGPT，自己改写题干又慢，还容易漏约束，测试时间都花在对不齐的实现上。这轮结果是挂。

另一篇拿到 offer 的 LeetCode Discuss 写的是流程，跟这道 logger 无关：电面和 onsite 都可以用 ChatGPT、Cursor 或 Claude，代码拷回 HackerRank 跑，题风是面向对象，不出力扣题。他的做法是自己先定结构，让模型写实现和测试，只采纳没有把题目变复杂的优化。Prachub 把 logger 扩成了一张命令表：`SET_REMOVE`、`SET_TRUNCATE`、`SET_UPPERCASE`、`SET_STORE`、`LOG`、`SEARCH`，变换顺序固定为删除、截断、大写。这是练习用的复原，这帖里核对不到。同一时期还有一篇电面是快递员三段 API，那是 `rippling-driver-pay`，和 logger 是两道题。

实现时，配置只影响后续消息，已经打印的历史不回溯。每次 `log` 都先从原消息开始，依次执行删除和截断：

```python
class Logger:
    def __init__(self):
        self.remove = None
        self.limit = None

    def log(self, message):
        text = message
        if self.remove:
            text = text.replace(self.remove, "")
        if self.limit is not None:
            text = text[: self.limit]
        print(text)
        return text
```

空的删除串不能拿去 `replace`。`"".replace` 的行为和「关闭删除」不一样，空配置应当是 no-op。截断长度小于 0 时问面试官，练习版把它当成 0。顺序也别弄反：先截断再删除的话，删完可能又短一截，和「先删再截」的测试对不上。帖子的顺序是先删、再截断。

用 AI 的时候，先自己写下函数和顺序，再让模型填函数体。把整题贴进去，模型会加上帖子里没有的 SEARCH、大小写，你还要花时间删。HackerRank 上最后跑的是你粘进去的代码，测试失败算你的。面试官要是问你怎么用的工具，就讲你拒绝了哪一条建议，只说「我用了 Cursor」没有信号。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

用 xxabcdef 和 limit=3 区分变换顺序：先删 xx 再截断应得到 abc。再测关闭删除和零长度，并捕获打印内容与返回值一起比较。

```python
import io
from contextlib import redirect_stdout

logger = Logger()
logger.remove, logger.limit = "xx", 3
output = io.StringIO()
with redirect_stdout(output):
    assert logger.log("xxabcdef") == "abc"
    logger.remove = None
    assert logger.log("xxabcdef") == "xxa"
    logger.limit = 0
    assert logger.log("hello") == ""
assert output.getvalue() == "abc\nxxa\n\n"
print("simple tests passed")
```

## 追问

**删除会不会连锁？**
`replace` 一遍删掉的是不重叠的出现。删完要是又拼出新的目标串，一遍不够。帖子没要求反复删到没有为止，我会问一句，默认一遍。

**SEARCH 要不要做？**
面试官加上「把变换后的消息存下来再查」才做，线性扫已存的消息就够了，不用主动写后缀数组。

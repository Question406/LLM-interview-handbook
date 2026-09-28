---
id: rippling-logger
section: rippling
order: 2
level: A
title: Rippling：AI coding 电面，logger 先删子串再截断
quick: >-
  2026 年电面可选 AI coding。公开帖能核对的只有两步：打印前删掉配置的字符串的所有出现，再把消息截断。
  每改一个功能都要能 print 出当前结果。不要把整段题干贴进模型。
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

## 真题记录

2026 年 4–6 月，Rippling SDE II，海投。电面选了 AI coding。作者说题目是地里那道 logger：打印前去掉配置字符串的每一次出现，再截断消息。每个功能做完都要能 print。帖子后半被截断，后面还有什么命令，原文没公开。

作者两轮 coding 都遇到同一件事：面试官不建议把题目全部贴给 ChatGPT。自己改写题干又慢，还容易漏约束，测试时间花在对不齐的实现上。这轮结果是挂。

另一篇 LeetCode Discuss（拿到 offer）写的是流程，不是这道 logger：电面和 onsite 都可以用 ChatGPT、Cursor 或 Claude，代码拷回 HackerRank 跑。题风是面向对象，不是力扣题。他的做法是自己先定结构，让模型写实现和测试，只采纳没有把题目变复杂的优化。

Prachub 把 logger 扩成命令表：`SET_REMOVE`、`SET_TRUNCATE`、`SET_UPPERCASE`、`SET_STORE`、`LOG`、`SEARCH`，变换顺序固定为删除、截断、大写。这是练习用的复原，不是这帖里能核对的原文。

同一时期还有一篇电面是快递员三段 API，那是 `rippling-driver-pay`，不是 logger。

## 我会怎么写

状态和变换分开。配置变了，已打印的历史不回溯。

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

空的删除串不能拿去 `replace`。`"".replace` 的行为和「关闭删除」不一样，空配置应当是 no-op。截断长度小于 0 时问面试官；练习版把它当成 0。

顺序若是先截断再删除，删完可能又短一截，和「先删再截」的测试对不上。帖子的顺序是先删、再截断。

## 用 AI 的时候

先自己写下函数和顺序，再让模型填函数体。把整题贴进去，模型会加上帖子里没有的 SEARCH、大小写，你还要花时间删。HackerRank 上最后跑的是你粘进去的代码，测试失败算你的。

面试官若问你怎么用的工具，讲你拒绝了哪一条建议。只说「我用了 Cursor」没有信号。

## 追问

**删除会不会连锁？** `replace` 一遍是删掉不重叠的出现。若删完又拼出新的目标串，一遍不够。帖子没要求反复删到没有为止。我会问一句，默认一遍。

**SEARCH 要不要做？** 只有面试官加上「把变换后的消息存下来再查」才做。线性扫已存消息就够。不要主动写后缀数组。

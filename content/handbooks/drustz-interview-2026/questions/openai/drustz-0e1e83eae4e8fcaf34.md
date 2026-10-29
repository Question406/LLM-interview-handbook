---
id: drustz-0e1e83eae4e8fcaf34
section: openai
order: 125
level: A
title: Refactor a Chatbot Codebase
quick: original-structured-preparation-guide · Refactor a Chatbot Codebase
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/52d61176-7455-4756-a5d5-7c9ddb53f0d2
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 重构一个 Chatbot 代码库

> 内容定位：本地面经直接确认这是一道“读旧代码并保持行为重构”的题。以下给出可操作的重构流程；原始 starter code 若与练习版不同，仍应以现场测试为准。

## 要完成什么

旧实现把 `messages`、`aways`、`tacos` 设为全局变量，在一个 `sendMessage` 中用固定字符串切片判断 `/meet`、`/givetaco` 等命令，同时混合解析、状态修改和输出。目标不是重写产品，而是在现有行为不变的前提下，使新增 bot 不必继续修改巨型条件分支。

先把现有输入输出变成 characterization tests。例如同一组输入在重构前后都必须得到完全相同的消息序列：

```text
alice: /meet @bob
MeetBot: meeting created for @alice and @bob
alice: ping @bob
AwayBot: @bob may be in a meeting
```



## 重构顺序

1. 把脆弱的 `msg[1:5]` 和多次 `split` 提取为 `CommandParser.parse(text) -> Command | None`，集中处理空格、缺参数和非法数字。
2. 用 `ChatState` 封装 away/taco 状态，用 `MessageSink` 封装日志，全部通过构造函数注入。
3. 定义 `Bot.handle(command, sender) -> list[str]`，分别抽出 AwayBot、MeetBot、TacoBot。
4. 用 registry 将 `command.type` 映射到 handler；ChatApp 只做“记录原消息—解析—分发—记录回复”。
5. 每一步都运行旧测试，再补充 malformed command、重复送达和跨 bot 状态变化测试。

不应在第一步顺手改变命令语义或输出文案；发现旧行为可疑时先锁定测试并单独记录，避免“重构”和“修 bug”混在一次提交里。

## 复杂度与边界

若按命令类型直接查 registry，路由为期望 `O(1)`；AwayBot 若仍遍历所有离开用户查 mention，则一次消息为 `O(A·L)`，其中 `A` 为 away 用户数、`L` 为文本长度，可进一步用显式 mention parser 优化。状态空间为 `O(A + U + H)`。重点边界包括空文本、Unicode 用户名、重复 taco、bot 顺序依赖、一个命令触发多个副作用、handler 抛异常，以及 Java/Python 迁移时是否仍保持原来的可观察行为。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/52d61176-7455-4756-a5d5-7c9ddb53f0d2)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

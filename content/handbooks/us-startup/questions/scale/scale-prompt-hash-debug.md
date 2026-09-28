---
id: scale-prompt-hash-debug
section: scale
order: 1
level: A
title: Scale AI：一段能调模型的代码，输出空了，查 prompt 的 hash
quick: >-
  新卒流程先是 HackerRank，再是 60 分钟技术面，然后设计和 debug 连着做。
  Debug 给了大约 150 到 200 行模块化的代码和他们模型的 key。候选人对出来的原因是 prompt 的 hash 流程，hash 用来少花 token。
tags:
  - Scale AI
  - Debugging
  - LLM
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-22
sources:
  - title: Scale AI New Grad Software Engineer Interview Experience (2026)
    url: https://www.tryexponent.com/experiences/scale-ai-software-engineer-interview-b83485
    type: candidate-first-hand
---

## 真题记录

Exponent 上 2026 年的 Scale AI 新卒 SWE。海投之后第一封是 HackerRank，没有招聘电话。隔了几周，60 分钟技术面，接着系统设计和 debug 背靠背，作者把这两轮当成 onsite。之后被拒，没走到他猜测的文化面。

Debug 的材料：大约 150 到 200 行，结构清楚，外加一个 key，打的是 Scale 自己的模型接口。现象是系统不返回模型输出。代码不乱，难在看清谁调用谁。作者用 print 缩小范围，结论是问题在 prompt 的 hashing 流程里。他们用 hash 减少 token 花费。

作者还写了一句文化：问到工作时，面试官说有点像 996。这是一个人的转述。

同一页没有给出 HackerRank 的题面，也没有设计题的原文。别的站点把「合并标注区间」「RLHF 队列的类设计」写成 Scale 的常考题，这份经验里没有这两道，我不收。

## 我会怎么查

先确认失败点在请求发出之前还是响应回来之后。没有输出，可能是没发、发了被缓存挡下、或者响应被丢掉。

Hash 若用来决定「这段 prompt 是否已经算过」，错的 hash 会命中别人的空缓存，或者每次都 miss 又在读缓存时抛掉。我会打印四样：归一化之后的 prompt、hash 输入的字节、hash 值、缓存命中还是回源。

归一化是常见坑。一端 strip 了空白或把换行折成空格，另一端用原文做 key，于是永远对不上。修的时候让写缓存和读缓存用同一个函数产出字节，不要在调用点各写一次 strip。

Token 花费是这道题的产品约束。缓存命中就不该再把 prompt 送给模型。修 bug 时不要顺手把缓存删掉来「保证有输出」，那会让每次请求都付 token。

## 设计和前面的编码

作者说越往后越像他们的业务，轮次要自己往前带。设计题题面未知。结合他 debug 里已经出现的东西，我会准备：请求怎么去重、缓存 key 含什么、模型挂了是返回错误还是返回上次结果。这些和他遇到的代码是同一类问题。

HackerRank 题面没公开。Scale 的编码轮时间紧，作者用了「很耗时间」来形容。按普通 medium 练速度，不要按这份经验去背某一道力扣。

## 追问

**hash 碰撞？** 碰撞会读到别的 prompt 的结果。面试里先把 key 修成稳定字节。若要讲生产，key 用密码学 hash，冲突时再比较原文。不要用 Python 内置 `hash()`，进程之间会变。

**为什么打印而不是断点？** 150 行、调用关系不清楚时，打印「这个函数有没有被走到」比一步步跟更快。作者就是这么缩小的。找到函数之后再读分支。

---
id: scale-prompt-hash-debug
section: scale
order: 1
level: A
title: Scale AI：一段能调模型的代码，输出空了，查 prompt 的 hash
quick: "公开复盘把根因定位在用于减少 token 花费的 prompt hashing 流程；排查时可以先判断请求有没有发出，再看归一化后的 prompt、hash 输入和缓存命中情况。新卒流程先是 HackerRank，再是 60 分钟技术面，然后设计和 debug 连着做。Debug 提供约 150 到 200 行模块化代码和模型接口的 key。"
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

公开复盘把根因定位在 prompt 的 hashing 流程，hash 用来减少 token 花费，作者没有公开具体哪一行出错。我会先用 print 判断问题发生在请求发出之前还是响应回来之后，再沿着 hash 和缓存的读写流程查。

来源是 Exponent 上 2026 年的 Scale AI 新卒 SWE。海投之后第一封就是 HackerRank，没有招聘电话。隔了几周是 60 分钟技术面，接着系统设计和 debug 背靠背，作者把这两轮当成 onsite。之后被拒，没走到他猜测的文化面。Debug 的材料是大约 150 到 200 行结构清楚的代码，外加一个 key，打的是 Scale 自己的模型接口。现象是系统不返回模型输出。代码不乱，难在看清谁调用谁。作者用 print 缩小范围，结论是问题在 输入提示（prompt） 的 hashing 流程里，他们用 hash 减少 token 花费。

作者还写了一句文化：问到工作时，面试官说有点像 996。这是一个人的转述。同一页没有给出 HackerRank 的题面，也没有设计题的原文。别的站点把「合并标注区间」「RLHF 队列的类设计」写成 Scale 的常考题，这份经验里没有这两道，我不收。

换我来查，第一步是确认失败点在请求发出之前还是响应回来之后。没有输出，可能是根本没发、发了被缓存挡下，或者响应被丢掉了。hash 要是用来决定「这段 prompt 是否已经算过」，错的 hash 会命中别人的空缓存，或者每次都 miss、又在读缓存时被抛掉。我会打印四样东西：归一化之后的 prompt、hash 输入的字节、hash 值、缓存命中还是回源。

我会重点检查归一化是否一致。比如一端 strip 了空白、把换行折成空格，另一端拿原文做 key，于是永远对不上。修的时候让写缓存和读缓存用同一个函数产出字节，别在每个调用点各写一次 strip。还要记得 token 花费是这道题的产品约束，缓存命中了就不该再把 prompt 送给模型。修 bug 时别顺手把缓存删掉来「保证有输出」，那样每次请求都要付 token。

设计轮和前面的编码，作者说越往后越像他们的业务，轮次要自己往前带。设计题题面未知，结合他 debug 里已经出现的东西，我会准备三件事：请求怎么去重、缓存 key 里含什么、模型挂了是返回错误还是返回上次结果。这些和他碰到的代码是同一类问题。HackerRank 题面没公开，作者用「很耗时间」形容 Scale 的编码轮，按普通 medium 练速度就好，别照这份经验去背某一道力扣。

## 追问

**hash 碰撞了怎么办？**
碰撞会读到别的 prompt 的结果。面试里先把 key 修成稳定字节；要讲生产的话，key 用密码学 hash，冲突时再比较一次原文。别用 Python 内置的 `hash()`，进程之间会变。

**为什么打印，不用断点？**
150 行、调用关系不清楚的时候，打印「这个函数有没有被走到」比一步步跟更快，作者就是这么缩小范围的。找到函数之后再读分支。

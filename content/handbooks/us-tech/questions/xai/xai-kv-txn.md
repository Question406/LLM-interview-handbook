---
id: xai-kv-txn
section: xai
order: 1
level: A
title: xAI：内存 KV 怎么加事务？15 分钟屏幕上的 race 怎么找？
quick: >-
  基础是 map。事务要 snapshot isolation 或等价：读集/写集，commit 时冲突则 abort。15 分钟视频面常见把带
  sleep 的 deposit 丢过来找 data race。先写清共享状态和锁粒度，再谈 GPU / 训练系统。
tags:
  - xAI
  - Concurrency
  - KV Store
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: xAI Interview Question Bank (1Point3Acres)
    url: https://www.1point3acres.com/interview/problems/company/xai
    type: secondary
  - title: xAI interview questions from candidate reports
    url: https://aceoffer.app/interviews/xai
    type: secondary
---

## 真题记录

- 公司：xAI
- 来源：一亩三分地 xAI 题库（2026-08 更新）列出 in-memory KV with transactions、BankAccount race 的 15 分钟视频面；AceOffer 汇总 80+ 份报告，KV+事务和 race 都是高频
- 口味：短、贴系统、要你当场改对。算法花样不是重点

和 Anthropic 内存库 (`anthropic-inmemory-db`) 亲戚，但 xAI 更抠 **并发正确性**。TTL 不是主线，事务和 race 才是。

## KV + 事务

单对象 `get/put` 用一把锁或 concurrent map 就够。事务要规定隔离级别。面试够用的是 snapshot isolation：

1. `begin`：记下事务 id，读的时候拷贝当前版本号。
2. `get`：读开始时的快照，写入自己的写缓冲，不直接打到全局。
3. `commit`：对写集加锁（按 key 排序，避免死锁），检查读集版本没被别人改过，否则 abort；通过则一次性应用写集、升版本。

不要一上来写完整 MVCC 引擎。把读写集、冲突检测、commit 原子性说清楚，代码能在单测里演示 `T1` 写 `a`、`T2` 写 `a` 必有一个 abort。

Rollback / 可恢复 iterator 也出现在同一题库：迭代到一半要能从 cursor 恢复。状态机比算法难。把 cursor 做成 `(key, version)`，不要用「list 下标」这种插入即失效的东西。

## 15 分钟 BankAccount race

公开预览：一段 `deposit` 读余额、sleep、写回。经典 lost update。找法：

- 共享可变状态是 `balance`。
- 临界区是读-改-写，sleep 只是把窗口拉大。
- 修法：`synchronized` / mutex 包住整段，或 `compareAndSet` 循环。Java 里单靠 `synchronized` 方法还要注意：follow-up 可能禁止改原类、让你 subclass / wrap。那是装饰器锁，不是再写一个 balance 字段。

现场用数据竞争的语言说：两个线程都能读到 100，都写成 110，丢了一次存款。不要只说「加个锁」而不说锁住哪一行。

Rate limiter、token bucket 是相邻题。同样先画共享计数器和时间窗口，再谈分布式。xAI 报告里还出现过「你能不能接受 60–100 小时、Palo Alto 坐班」。那是文化匹配，不是技术题，按自己实际情况答，不要演。

## 追问

- **为什么不用 serializable 全局大锁？** 能写对，但吞吐差。面试先正确再并发度。
- **和训练 checkpoint 的关系？** 同一类：原子可见的版本。权重文件要么完整要么不可见，不要半份。
- **Go / Rust 追问？** 政府相关岗位的报告里出现过。普通 SWE 以你简历语言为准。

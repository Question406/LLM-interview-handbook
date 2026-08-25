---
id: ali-be-thread-lock
section: alibaba-oa
order: 51
level: A
title: 阿里研发面：线程池七参数，`synchronized` 和 `ReentrantLock` 怎么选？
quick: >-
  七参数是核心/最大/存活、队列、工厂、拒绝策略。`synchronized` 是 JVM 锁；`ReentrantLock` 能公平、可中断、多条件。AQS 用 CLH 变体排队。
tags:
  - Alibaba
  - 并发
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阿里校招 Java 面经（秒杀/LRU）
    url: https://www.nowcoder.com/feed/main/detail/0a3142d863914f689cc76fbc3bb68ba6
    type: candidate-first-hand
---

## 真题记录

- 岗位：阿里校招 Java

## 定义

线程池把「创建线程」和「执行任务」拆开。`ThreadPoolExecutor` 七参数按执行语义记，不要背成单词表：`corePoolSize` 是常驻工人；`maximumPoolSize` 是峰值上限；`keepAliveTime` + `TimeUnit` 是非核心线程空闲回收；`workQueue` 是任务缓冲；`threadFactory` 决定线程名、守护属性，方便排查；`handler` 是队列和线程都满之后的拒绝策略。提交顺序必须说对：先把核心线程填满，再入队，队列满才开到最大线程，再满才拒绝。这块容易把「先扩线程再入队」讲反，面试官会立刻打断。

锁更简单：保护临界区，保证同一时刻只有约定数量的线程能改共享状态。`synchronized` 是 JVM 内置监视器锁，进入代码块或方法时获取，退出或异常时自动释放，可重入。`ReentrantLock` 是 JUC 里基于 AQS 的显式锁，必须在 `finally` 里 `unlock`。AQS 本体是一个 `state` 整数加一条 CLH 变体的双向等待队列：获取失败的线程入队停车，释放时唤醒后继；独占模式对应锁，共享模式对应 `CountDownLatch` / `Semaphore`。

## 对比 / 分层

| | `synchronized` | `ReentrantLock` |
| --- | --- | --- |
| 获取 / 释放 | 编译成 monitorenter / exit，异常自动释放 | 手写 lock / unlock |
| 尝试与超时 | 不能 `tryLock` | `tryLock`、限时、可中断 |
| 公平性 | 非公平（有偏） | 可公平，默认非公平 |
| 条件队列 | 一把锁一个 `wait/notify` 集合 | 多把 `Condition` |
| 适用 | 短临界区、语法简单 | 需要取消、公平、多条件排队 |

拒绝策略也要分层：`AbortPolicy` 抛异常，调用方能感知过载；`CallerRunsPolicy` 把任务打回提交线程，形成反向压；`DiscardPolicy` 静默丢新任务；`DiscardOldestPolicy` 丢队列头再试。交易、支付禁止静默丢。队列选型：CPU 密集用有界队列 + 较小最大线程；IO 密集（调下游 HTTP / DB）可以把最大线程抬高，但必须有界，无界 `LinkedBlockingQueue` 会把 OOM 藏到堆里。

死锁四条件照说：互斥、持有并等待、不可抢占、环路等待。预防用固定加锁顺序、超时 `tryLock`、缩小锁粒度。阿里面经常把线程池和锁串起来：线程池耗尽是不是锁等下游超时引起的。

## 阿里场景

下单服务里常见两类池。一类是「计算池」，做价格、优惠、库存预校验，CPU 密集，核心数接近 CPU，队列短，拒绝走快速失败并让上游限流。另一类是「IO 池」，调库存中心、优惠中心、会员，核心小、最大线程按下游超时和连接池算：假设单机 $200$ 个下游连接、P99 $50$ ms，理论并发大约是连接数，再留余量。线程名必须带业务前缀，例如 `order-price-`，否则夜间看 dump 分不清是哪个池在堵。

锁的场景：本地扣减一个活动库存计数，临界区只有几行内存操作，用 `synchronized` 或 `LongAdder` 就够。如果要「库存不足时等待补货通知」，需要多条件队列，用 `ReentrantLock` + `Condition`。跨进程不要用 JVM 锁，改 Redis / DB。双十一时最怕的不是锁实现选错，而是线程池队列堆了十万下单请求，下游已经超时，池里的线程还在重试，把故障放大。正确姿势是有界队列 + 快速失败 + 让网关限流，而不是把 `maximumPoolSize` 调到 $2000$。

## 追问

- 核心线程会不会超时回收？默认不会，除非 `allowCoreThreadTimeOut`。
- 为什么不推荐 `Executors.newFixedThreadPool`？默认无界队列，背压失效。
- `tryLock` 失败后怎么做？降级、排队或返回「系统繁忙」，不要空转。
- AQS 的 `state` 在可重入锁里表示什么？持有次数；读写锁会把高低位拆开。
- 公平锁一定更安全吗？公平降低吞吐，锁饥饿少，交易热路径一般非公平。
- 如何定位死锁？`jstack` 看 `waiting to lock`，或 `ThreadMXBean.findDeadlockedThreads`。
- 线程池拒绝了，任务丢了怎么审计？拒绝时打业务单号日志，必要时落补偿表。

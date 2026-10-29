---
id: ali-be-thread-lock
section: alibaba-oa
order: 51
level: A
title: 阿里研发面：线程池七参数，`synchronized` 和 `ReentrantLock` 怎么选？
quick: >-
  线程池七参数分别控制核心线程数、最大线程数、空闲存活时间及单位、任务队列、线程工厂和拒绝策略，提交顺序是先填核心线程、再入队、队列满才扩到最大线程、再满才拒绝。`synchronized` 是 JVM 内置锁；`ReentrantLock` 支持公平锁、可中断获取、`tryLock` 和多个条件队列，底层 AQS 用 CLH 变体管理等待线程。
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

线程池的七个参数我按任务提交时经过的顺序讲：先填满核心线程，再进队列，队列满了才扩到最大线程，还满就走拒绝策略。把顺序讲成「先扩线程再入队」，面试官会立刻打断。锁的选择看需求：短临界区用 `synchronized` 就够，要超时、可中断、公平或多个条件队列时用 `ReentrantLock`。这是阿里校招 Java 面的题。

线程池把创建线程和执行任务拆开。`ThreadPoolExecutor` 的七个参数按执行语义记，别背成单 vocabulary：`corePoolSize` 是常驻工人；`maximumPoolSize` 是峰值上限；`keepAliveTime` + `TimeUnit` 控制非核心线程空闲多久回收；`workQueue` 是任务缓冲；`threadFactory` 决定线程名和守护属性，方便排查；`handler` 是队列和线程都满之后的拒绝策略。

拒绝策略有四种。`AbortPolicy` 抛异常，调用方能感知过载；`CallerRunsPolicy` 把任务打回提交线程执行，形成背压，让提交速度降下来；`DiscardPolicy` 静默丢掉新任务；`DiscardOldestPolicy` 丢掉队列头再重试。交易、支付禁止静默丢。队列选型上，CPU 密集用有界队列加较小的最大线程数；IO 密集（调下游 HTTP / DB）可以把最大线程抬高，但必须有界，无界的 `LinkedBlockingQueue` 会把 OOM 藏在堆里。`Executors.newFixedThreadPool` 不推荐也是这个原因，它默认用无界队列，背压就失效了。

锁是用来保护临界区的，保证同一时刻只有约定数量的线程能改共享状态。`synchronized` 是 JVM 内置的监视器锁，进入代码块或方法时获取，退出或抛异常时自动释放，可重入。`ReentrantLock` 是 JUC 里基于 AQS 的显式锁，必须在 `finally` 里 `unlock`。AQS 本体是一个 `state` 整数加一条 CLH 变体的双向等待队列：获取失败的线程进队等待，释放时唤醒后继；独占模式对应锁，共享模式对应 `CountDownLatch` / `Semaphore`。

| | `synchronized` | `ReentrantLock` |
| --- | --- | --- |
| 获取 / 释放 | 编译成 monitorenter / exit，异常自动释放 | 手写 lock / unlock |
| 尝试与超时 | 不能 `tryLock` | `tryLock`、限时、可中断 |
| 公平性 | 非公平（有偏） | 可公平，默认非公平 |
| 条件队列 | 一把锁一个 `wait/notify` 集合 | 多把 `Condition` |
| 适用 | 短临界区、语法简单 | 需要取消、公平、多条件排队 |

死锁有四个条件：互斥、持有并等待、不可抢占、环路等待。预防靠固定加锁顺序、超时 `tryLock`、缩小锁粒度。阿里面经常把线程池和锁串起来问：线程池耗尽，是不是锁在等下游超时引起的。

## 放到阿里的场景里

下单服务里常见两类池。一类是计算池，做价格、优惠、库存预校验，CPU 密集，核心数接近 CPU，队列短，拒绝时快速失败并让上游限流。另一类是 IO 池，调库存中心、优惠中心、会员，核心小，最大线程按下游超时和连接池来算：假设单机 $200$ 个下游连接、P99 $50$ ms，理论并发大约就是连接数，再留些余量。线程名必须带业务前缀，比如 `order-price-`，否则夜里看 dump 分不清是哪个池在堵。线程池拒绝了任务也要能审计，拒绝时打上业务单号的日志，必要时落补偿表。

锁也按场景选。本地扣减一个活动库存计数，临界区只有几行内存操作，用 `synchronized` 或 `LongAdder` 就够。如果要「库存不足时等补货通知」，需要多个条件队列，就用 `ReentrantLock` + `Condition`。跨进程别用 JVM 锁，改用 Redis / DB。双十一更常见的情况是线程池队列堆了十万个下单请求，下游已经超时，池里的线程还在重试，把故障放大。正确的姿势是有界队列 + 快速失败 + 让网关限流，别把 `maximumPoolSize` 调到 $2000$。

## 追问

**核心线程会不会超时回收？**
默认不会，除非开了 `allowCoreThreadTimeOut`。

**`tryLock` 失败后怎么做？**
降级、排队，或者返回「系统繁忙」，别空转。

**AQS 的 `state` 在可重入锁里表示什么？**
持有次数。读写锁会把它的高低位拆开用。

**公平锁一定更安全吗？**
公平锁减少锁饥饿，但会降低 throughput，交易热路径一般用非公平。

**怎么定位死锁？**
用 `jstack` 看 `waiting to lock`，或者调 `ThreadMXBean.findDeadlockedThreads`。

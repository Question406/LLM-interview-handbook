---
id: ali-be-jvm-gc
section: alibaba-oa
order: 50
level: A
title: 阿里研发面：JVM 内存怎么分，CMS 和 G1 差在哪？
quick: >-
  堆分新生代和老年代，类元数据在堆外的元空间，另外还有直接内存、线程栈和代码缓存。CMS 是并发标记清除，不整理，碎片多；G1 把堆切成 Region
  按价值回收，停顿更可控。低延迟我优先看 G1/ZGC，throughput 优先看并行收集。
tags:
  - Alibaba
  - JVM
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 阿里校招 Java 面经（秒杀/LRU）
    url: 'https://www.nowcoder.com/feed/main/detail/0a3142d863914f689cc76fbc3bb68ba6'
    type: candidate-first-hand
  - title: 2026 校招高频题总览
    url: 'https://www.cnblogs.com/autodriver/p/19829365'
    type: secondary
---

JVM 内存我先拆成堆内和堆外：堆里是新生代和老年代，堆外有元空间、直接内存、线程栈和 JIT 代码缓存。CMS 和 G1 的差别主要在堆怎么组织：CMS 的老年代是连续的一整块，并发标记清除但不整理，所以会碎；G1 把堆切成等大的 Region，挑垃圾多的先回收，停顿更可预期。这是阿里校招 Java / 研发面的常见题。

堆是 GC 主要回收的地方。新生代（Eden + Survivor $S_0/S_1$）放短命对象，老年代放活得久或者放不下的大对象。JDK 8 之后方法区落地成元空间，类元数据放在本地内存，不再占堆。堆外的直接内存就是 NIO / Netty 的 DirectByteBuffer。口述时我先画这张图，再讲对象的路径：新对象进 Eden；Eden 满了触发 Minor GC，活下来的进 Survivor；年龄到阈值或者 Survivor 装不下，就晋升到老年代；老年代不够再 Major / Full GC。

分配失败和「堆满了」是两回事。大对象可能直接进老年代；元空间增长、直接内存没释放、线程栈占得太多，都会 OOM，这时堆看起来还空着。线程开太多就是一个例子，每个线程都有栈，堆外先爆，看起来像「内存泄漏」。所以讲内存分区时，我会把每一块和它对应的 OOM 绑在一起说。

收集器按目标分三类：要 throughput 用 Parallel，要低停顿、可预期用 CMS / G1，要近乎无停顿用 ZGC / Shenandoah。校招对比 CMS 和 G1 就够。

| | CMS | G1 |
| --- | --- | --- |
| 堆模型 | 整代连续，老年代并发清除 | 堆切成等大 Region，按价值回收 |
| 算法 | 标记-清除，老年代不整理 | 复制/整理，Region 腾空后可复用 |
| 停顿 | 初始标记 + 重新标记两次 STW，其余并发 | 有 `MaxGCPauseMillis` 目标，Young + Mixed |
| 代价 | 碎片、Concurrent Mode Failure 退化成 Serial Old | Remembered Set、写屏障，CPU 和内存开销更大 |
| 失败形态 | 浮动垃圾占位，预留空间不够就 Full GC | 疏散失败、Humongous 对象占多个 Region |

CMS 的并发清除不移动对象，老年代会越来越碎，再来一个大对象就可能触发「并发模式失败」，退化成 Serial Old，停顿不可控，这也是它被 G1 替换的原因。G1 用 SATB 做并发标记，优先回收垃圾占比高的 Region，停顿更可预测，但不保证每次都短。JDK 9 起 G1 是默认收集器。低延迟再提一句 ZGC：着色指针加读屏障，停顿和堆大小解耦，校招点到即可。

调参我一般先看 GC 日志里的停顿分布和晋升速率，再去动新生代比例、Region 大小、并发标记线程数。`-Xmx` 别加到机器内存的 $90\%$，元空间和直接内存会把宿主机打满。

## 放到阿里的场景里

淘天交易链路是典型的短请求、高 QPS、对尾延迟敏感。一次 Full GC 停几百毫秒，下游会超时重试，重试又放大堆分配，最后形成雪崩。双十一前更常见的是两种情况：促销规则对象、商品快照、Hessian 反序列化把 Eden 打爆，晋升太快；或者网关堆了太多 DirectBuffer 没归还，堆内 GC 看起来很健康，进程却被 cgroup 杀掉。

可以落到一个具体服务上讲，比如商品详情或购物车。读路径尽量走堆外缓存或本地缓存，避免每个请求都 new 一堆 JSON 对象。写路径（下单）对象生命周期短，新生代给够，减少晋升。延迟 SLA 紧的链路用 G1，并盯住 P99 停顿；批处理对账、离线导出才用 Parallel 换 throughput。

线上排查先看报的是 `Java heap space`、`Metaspace` 还是 `Direct buffer memory`。堆 OOM 做 heap dump，看是泄漏还是峰值太大；元空间看动态代理、热加载有没有卸载；直接内存看 Netty 的泄漏检测。同时对照 GC 日志、线程 dump 和容器内存限额，光把 `-XX:+UseG1GC` 加上不算排查完。

## 追问

**Minor GC 很频繁但停顿短，要不要把新生代加大？**
不一定。加大会拉长单次 Minor GC，要看晋升率和 P99 再定。

**什么时候上 ZGC？**
堆很大、停顿预算在十毫秒以内，并且能接受更高的 CPU 和内存开销。

**交易高峰能调 `System.gc()` 吗？**
不能。它会诱发 Full GC，生产上默认当事故处理。

**怎么证明问题不在 GC？**
对照同一分钟的接口 P99、GC 停顿、CPU 和老年代占用，对不上就去查锁、慢 SQL 和下游超时。

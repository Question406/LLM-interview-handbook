---
id: ali-be-jvm-gc
section: alibaba-oa
order: 50
level: A
title: 阿里研发面：JVM 内存怎么分，CMS 和 G1 差在哪？
quick: >-
  堆分新生代 / 老年代，再加元空间。CMS 是并发标记清除，碎片多。G1 按 Region 回收，停顿更可控。低延迟我优先看 G1/ZGC，吞吐优先看并行收集。
tags:
  - Alibaba
  - JVM
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阿里校招 Java 面经（秒杀/LRU）
    url: https://www.nowcoder.com/feed/main/detail/0a3142d863914f689cc76fbc3bb68ba6
    type: candidate-first-hand
  - title: 2026 校招高频题总览
    url: https://www.cnblogs.com/autodriver/p/19829365
    type: secondary
---

## 真题记录

- 岗位：阿里校招 Java / 研发

## 定义

JVM 运行时内存我先拆成堆内和堆外。堆是 GC 主战场：新生代（Eden + Survivor $S_0/S_1$）放短命对象，老年代放活得久或放不下的大对象。JDK 8 之后方法区落地成元空间，在本地内存里存类元数据，不再占堆。堆外还有直接内存（NIO / Netty 的 DirectByteBuffer）、线程栈、JIT 代码缓存。口述我会先画这张图，再讲对象路径：新对象进 Eden；Eden 满触发 Minor GC，活下来的进 Survivor；年龄到阈值或 Survivor 装不下，晋升老年代；老年代不够再 Major / Full GC。

分配失败不等于「堆满」。大对象可能直接进老年代；元空间涨、直接内存没释放、线程栈爆炸，都会 OOM，但堆看起来还空着。所以「哪一块内存」要和「哪一种 OOM」绑在一起讲。

## 对比 / 分层

收集器按目标分三层：吞吐（Parallel）、低停顿可预期（CMS / G1）、近停顿（ZGC / Shenandoah）。校招对打 CMS 和 G1 即可。

| | CMS | G1 |
| --- | --- | --- |
| 堆模型 | 整代连续，老年代并发清除 | 堆切成等大 Region，按价值回收 |
| 算法 | 标记-清除，老年代不整理 | 复制/整理，Region 腾空后可复用 |
| 停顿 | 初始标记 + 重新标记两次 STW，其余并发 | 有 `MaxGCPauseMillis` 目标，Young + Mixed |
| 代价 | 碎片、Concurrent Mode Failure 退化成 Serial Old | Remembered Set、写屏障，CPU 和内存开销更大 |
| 失败形态 | 浮动垃圾占位，预留空间不够就 Full GC | 疏散失败、Humongous 对象占多个 Region |

CMS 的并发清除不移动对象，所以老年代会碎；再来一个大对象就可能触发「并发模式失败」。G1 用 SATB 并发标记，优先回收垃圾占比高的 Region，停顿更可预测，但不保证每次都短。JDK 9 起 G1 是默认；低延迟再提 ZGC：着色指针 + 读屏障，停顿与堆大小解耦，校招点到即可。

调参我一般先看 GC 日志里的停顿分布和晋升速率，再动新生代比例、Region 大小、并发标记线程。不要一上来把 `-Xmx` 加到机器内存的 $90\%$，元空间和直接内存会把宿主机打满。

## 阿里场景

淘天交易链路是典型「短请求、高 QPS、对尾延迟过敏」。一次 Full GC 停几百毫秒，下游会超时重试，重试再放大堆分配，形成雪崩。双十一前更常见的不是「算法选错」，而是：促销规则对象、商品快照、Hessian 反序列化把 Eden 打爆，晋升太快；或者网关堆了太多 DirectBuffer 没归还，堆内 GC 看起来很健康，进程却被 cgroup 杀掉。

口述可以落到一个具体服务：商品详情或购物车。读路径尽量走堆外缓存或本地缓存，避免每次请求都 new 一堆 JSON 对象。写路径（下单）对象生命周期短，新生代给够，减少晋升。对延迟 SLA 紧的链路用 G1 并盯 P99 停顿；批处理对账、离线导出才用 Parallel 换吞吐。

线上排查顺序：先看是 `Java heap space`、`Metaspace` 还是 `Direct buffer memory`。堆 OOM 做 heap dump 看是否泄漏或峰值过大；元空间看动态代理 / 热加载有没有卸载；直接内存看 Netty 的泄漏检测。阿里内部常见配套是 GC 日志 + 线程 dump + 容器内存限额一起看，不要只调 `-XX:+UseG1GC` 就结束。

## 追问

- Minor GC 很频繁但停顿短，要不要把新生代加大？加大会拉长单次 Minor GC，要看晋升率和 P99。
- CMS 为什么会被 G1 替换？碎片 + 失败后的 Serial Old，停顿不可控。
- 什么时候上 ZGC？堆很大、停顿预算到十毫秒以内，且能接受更高 CPU / 内存。
- 线程数开太多会怎样？每个线程有栈，堆外先爆，看起来像「内存泄漏」。
- `System.gc()` 能不能在交易高峰调用？会诱发 Full GC，生产默认当事故。
- 如何证明不是 GC 问题？对照同一分钟的接口 P99、GC 停顿、CPU、老年代占用，对不上就去锁、慢 SQL、下游超时。

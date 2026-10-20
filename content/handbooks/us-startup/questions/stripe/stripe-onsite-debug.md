---
id: stripe-onsite-debug
section: stripe
order: 3
level: A
title: Stripe：Bug Bash、集成轮，和分布式计数器设计
quick: >-
  Senior onsite 的系统设计是分布式 metric counter。Bug Bash 有人只记得 retry policy 的两个字段互相覆盖。
  集成轮是在不熟的仓库里按文档接 API，不许用 AI 把功能写出来。
tags:
  - Stripe
  - Debugging
  - System Design
realInterview: true
status: published
format: markdown
updatedAt: 2026-09-22
sources:
  - title: Stripe L3 全套挂经，系统设计与 retry policy
    url: https://www.1point3acres.com/bbs/thread-1171504-1-1.html
    type: candidate-first-hand
  - title: Stripe Software Engineer Interview Guide，Bug Bash 与 Integration
    url: https://www.tryexponent.com/guides/stripe-software-engineer-interview
    type: secondary
---

## 真题记录

同一篇 2026 年 3 月 Stripe senior 挂经。店面是 `stripe-csv-validate`。Onsite 里作者记得的系统设计是 distributed metric counter，并说可以对照 Hello Interview 的讲法。回帖有人问 coding 的 bug，作者只记得第一个和 retry policy 有关：两个 field 会互相 overwrite。其余 bug 他写了记不清。

VO 两周后拒信，不是模板信。作者自己的判断是不够 strong。这不能反推「做完就会过」。

Exponent 指南把 SWE onsite 写成五轮里的三轮编码：普通业务编码、Bug Bash、Integration，外加 system design 和行为面。校招经常不考完整系统设计。指南里的 Bug Bash 例子是另一批报告：路径忘了判断是不是目录、AST 少了一个 visitor、并发下读改写丢更新。不要把这三例说成 3 月那次的题。

Integration 的公开描述是：不熟的仓库，可以查文档和网页，不许用 AI coding assistant，45–60 分钟交一个能跑的改动。有候选人觉得难点是选哪个 API，不是算法。

## Metric counter 我会怎么讲

题目是计数器，不是通用时序数据库。先问：哪些 metric 名、哪些 tag、聚合是 sum 还是 last、查询窗口、能不能丢点。

写入路径：SDK 本地按 `(name, tags)` 累加，几秒刷一次。网关按 key 分片，单分片内原子加。查询走副本或预聚合，不在请求里扫原始事件。

Stripe 场景里我会主动说三件事。时钟用服务端收到的时间，不信客户端时钟。同一批上报带 idempotency key，重试不要双计。基数高的 tag（user id 这种）要拒绝或采样，不然一个 metric 名下面的序列会爆。

一致性是「短窗口可以少一点，不能多计」。多计会让告警误报，比少计更难查。

## Bug Bash 我会怎么做

先让失败测试复现，再缩小到一个函数。retry policy 两个字段互相覆盖，常见是后写的配置把先写的整个对象换掉，而不是按字段合并。我会把合并写成显式的字段拷贝，并加一个测试：只改第二个字段时，第一个字段还在。

指南里的另三例，准备方式是一样的：目录判断、visitor 缺分支、没加锁的读改写。练的是在别人的仓库里十分钟内找到相关文件，不是背 bug。

## 追问

**计数器挂了写入怎么处理？** 本地缓冲有上限。满了丢弃并打一个 `dropped` 自监控。阻塞业务请求去等计数器，会让计数器变成支付路径上的依赖。

**集成轮选错 API 了？** 指南说面试官会把你推向更合适的端点。先读完文档里和这个字段相关的两三个方法，再说你为什么调用这一个。选错了改口，比在错的端点上写完整解析便宜。

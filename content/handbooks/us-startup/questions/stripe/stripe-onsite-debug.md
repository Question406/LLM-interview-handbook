---
id: stripe-onsite-debug
section: stripe
order: 3
level: A
title: Stripe：Bug Bash、集成轮，和分布式计数器设计
quick: >-
  Senior onsite 的系统设计是分布式 metric counter，我会按「短窗口可以少计、不能多计」来设计。Bug Bash 有人只记得 retry policy 的两个字段互相覆盖，先复现再缩到一个函数。集成轮是在不熟的仓库里按文档接 API，不许用 AI 把功能写出来。
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

## 题目描述

来源确认的只是轮次与题型；下面接口场景和“不能多计”是手册练习约定，不是完整现场题面。

### 场景与目标

本卡包含三类独立练习：分布式指标计数器、已有仓库中的 Bug Bash，以及按文档完成 API 集成。任选一类作为一次限时任务。

### 需要满足的功能

- 计数器：接收带 metric、tags、时间与批次标识的增量，按指定窗口查询聚合值。
- Bug Bash：在给定仓库和失败复现中找出配置字段互相覆盖的问题，交付最小修复及回归证明。
- 集成：根据提供的外部 API 文档，为现有项目完成指定可运行功能，并处理失败与重试。

### 约束与交付物

计数器的流量、窗口和可接受延迟由候选人先澄清；本练习约定重复上报不得多计。仓库、API 规格和现场 bug 原文未公开，不能把推测的代码缺陷当成事实。

请给出需求边界、对外接口及返回语义、核心数据对象、主要请求的完整生命周期、故障与恢复行为，以及能验证设计是否达标的指标。题目不预先指定数据库、模型或调度算法；需要解释自己作出的选择与代价。

### 请求与结果示例

同一批“requests += 10”因网络重试到达两次时，计数器不能返回增加 20；配置修复练习中，只修改第二个字段后，第一个字段原有值必须仍在。

## 解题思路与参考答案

准备 Stripe senior onsite，我会分别练分布式计数器设计、在已有仓库里定位 bug，以及按文档集成 API。公开复盘里的设计题是 metric counter，bug 只记得 retry policy 两个字段互相覆盖；集成轮的材料来自另一份指南，要求在不熟的仓库里完成改动，不许用 AI 写功能。

来源还是那篇 2026 年 3 月的 Stripe senior 挂经，店面是 `stripe-csv-validate`。Onsite 里作者记得的系统设计是 distributed metric counter，他说可以对照 Hello Interview 的讲法。回帖有人问 coding 里的 bug，作者只记得第一个和 retry policy 有关，两个 field 会互相 overwrite，其余的他写了记不清。VO 两周后收到拒信，不是模板信，作者自己的判断是不够 strong。这推不出「做完就会过」。

Exponent 指南把 SWE onsite 写成五轮，其中三轮编码：普通业务编码、Bug Bash、Integration，外加 system design 和行为面，校招经常不考完整系统设计。指南里的 Bug Bash 例子来自另一批报告：路径忘了判断是不是目录、AST 少了一个 visitor、并发下读改写丢更新。别把这三例说成 3 月那次的题。Integration 的公开描述是：不熟的仓库，可以查文档和网页，不许用 AI coding assistant，45–60 分钟交一个能跑的改动。有候选人觉得难点在选哪个 API，算法本身不难。

Metric counter 先把范围收窄，题目是计数器，不用做成通用时序数据库。先问清楚：哪些 metric 名、哪些 tag，聚合是 sum 还是 last，查询窗口多大，能不能丢点。写入路径是 SDK 在本地按 `(name, tags)` 累加，几秒刷一次；网关按 key 分片，单分片内原子加；查询走副本或预聚合，不在请求里扫原始事件。

放在 Stripe 的场景里，我会主动说三件事。时钟用服务端收到的时间，不信客户端时钟。同一批上报带 idempotency key，重试不会双计。user id 这种基数高的 tag 要拒绝或采样，不然一个 metric 名下面的序列会爆。一致性上，短窗口可以少一点，但不能多计，多计会让告警误报，比少计更难查。

Bug Bash 先让失败测试复现，再缩小到一个函数。retry policy 两个字段互相覆盖，常见原因是后写的配置把先写的整个对象换掉了，没有按字段合并。我会把合并写成显式的字段拷贝，再加一个测试：只改第二个字段时，第一个字段还在。指南里的另三例准备方式一样，目录判断、visitor 缺分支、没加锁的读改写，练的是在别人的仓库里十分钟内找到相关文件，背 bug 没用。

## 追问

**计数器挂了，写入怎么处理？**
本地缓冲设上限，满了就丢弃，同时打一个 `dropped` 自监控。让业务请求阻塞着去等计数器，计数器就成了支付路径上的依赖。

**集成轮选错 API 了怎么办？**
指南说面试官会把你推向更合适的端点。先读完文档里和这个字段相关的两三个方法，再说你为什么调用这一个。选错了就改口，比在错的端点上写完整套解析便宜。

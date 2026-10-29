---
id: sd-job-scheduler
section: general
order: 16
level: A
title: 设计任务调度平台：重试、租约和重复执行
quick: 假设 worker 完成任务，却在回报成功前断线。调度器可能再次分配，因此业务不能默认每个任务只执行一次。
companies: []
tags:
  - System Design
  - 设计练习
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
collapseAnswer: true
updatedAt: '2026-10-28'
sources:
  - title: Apache Kafka：Design
    url: 'https://kafka.apache.org/documentation/#design'
    type: primary
  - title: PostgreSQL：Transaction Isolation
    url: 'https://www.postgresql.org/docs/current/transaction-iso.html'
    type: primary
---

## 题目描述

设计后台任务平台，支持提交、延时执行、重试、取消和结果查询。任务可能运行10分钟，worker 可能失联后恢复。请输出任务状态机、调度队列、租约与重试策略，说明重复领取、过期 worker 提交和取消竞态。练习要求控制并发与重试预算，不承诺任意外部操作严格只执行一次。

### 作答要求与场景

请用文字与图说明输入或业务事件怎样到达最终输出，写清失败或重试时用户能观察到的结果。给至少一个具体请求或事件序列作为示例，最后说明怎样验证设计。场景假设与补充规则由本手册设定。

## 回答思路

> **问题与场景：** 假设 worker 完成任务，却在回报成功前断线。
>
> **做法与原因：** 我会保存任务状态与尝试记录，用租约和 heartbeat 判断 worker 是否仍活跃，并让执行结果支持幂等提交。
>
> **检查与取舍：** 测试租约过期后旧 worker 又恢复、重复回报和调度器重启。

## 可以这样回答

假设 worker 完成任务，却在回报成功前断线。调度器可能再次分配，因此业务不能默认每个任务只执行一次。

我会保存任务状态与尝试记录，用租约和 heartbeat 判断 worker 是否仍活跃，并让执行结果支持幂等提交。重试次数、退避与永久失败要有明确规则。

测试租约过期后旧 worker 又恢复、重复回报和调度器重启。重点是重复执行不会破坏结果，而不是声称绝不会重复。

## 技术备查

## 参考答案与设计讨论

持久化任务状态，用租约调度执行，用执行代次拒绝过期提交；业务副作用仍需要幂等。

![设计任务调度平台：重试、租约和重复执行：核心数据流](/system-design/job-scheduler.svg)

图展示核心数据流；权限、状态和故障恢复以正文约定为准。

### 状态与领取

任务保存标识、参数摘要、下一次可运行时间、尝试次数和 deadline。就绪任务进入队列，worker 条件领取并记录租约与执行代次，运行中续租。队列提供唤醒，数据库状态是恢复依据，不能把已消费当成已完成。

### 处理旧 worker 回归

租约到期后新 worker 领取更高代次，提交结果时比较代次；旧 worker 的结果必须被拒绝。仅检查数据库还不够，外部存储也应支持 fencing 或 idempotency key，否则旧 worker 仍可能产生副作用。

### 重试、取消与公平

可重试失败按退避调度，有总次数和总耗时；长期失败进入可审查的隔离状态。取消由状态更新传播到执行端，尽力终止资源使用，并说明无法撤销的已提交效果。租户配额和任务类别队列防止长任务独占。

### 例子与追问

worker A 暂停导致租约过期，B 代次2完成；A 恢复后代次1提交被拒绝。若任务是发邮件，必须定义供应商幂等或允许重复的 conditions。进度百分比不是结果提交证明，调度器重启后按持久状态恢复。


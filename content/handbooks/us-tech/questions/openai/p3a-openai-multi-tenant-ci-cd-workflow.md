---
id: p3a-openai-multi-tenant-ci-cd-workflow
section: openai
order: 642
level: A
title: "OpenAI：多租户 CI/CD：调度、隔离和执行语义"
quick: "多租户 CI/CD 持久化 DAG、步骤状态和租约，worker 在隔离环境执行，“恰好一次”只能承诺到状态提交和产物发布。"
companies:
  - openai
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · multi-tenant-ci-cd-workflow"
    url: https://www.1point3acres.com/interview/problems/company/openai/multi-tenant-ci-cd-workflow
    type: secondary
---

## 题目

设计一个多租户 CI/CD 系统：git push 触发用户定义的工作流，执行过程要容错，并实时展示状态。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；收录为面经题型不代表公司官方确认。规模数字、SLO 和故障情景是手册补的练习约定。

## 思路

把工作流 DAG、每个步骤的状态和租约都持久化，worker 在隔离环境里执行用户代码。

这题常被追问"恰好一次"。要先说清楚保证的对象：可以做到"状态提交恰好一次"或"产物发布恰好一次"，但如果 worker 在执行任意 shell 命令时崩溃，仅靠队列无法保证这条外部命令只执行一次。可实现的保证来自幂等步骤、去重提交或事务边界。

## 完整非编程练习（场景与参考回答）

### 具体题目与需求澄清

git push 触发用户定义的 DAG，要求租户隔离、实时日志、worker 故障后可以恢复。对任意 shell 命令，不承诺外部效果恰好一次。

开始回答时复述这些范围，问面试官是否需要缓存、矩阵构建和手动审批步骤。

### 一套可展开的参考答案

**1. 架构与关键路径。**

1. webhook 入口验签并去重。
2. 解析工作流定义，把 DAG 持久化。
3. 调度器把依赖已满足的 job 放进 ready 队列。
4. 隔离 runner 领取并执行 job。
5. 产物写入产物存储，日志实时推流。

控制面从不直接执行用户代码。

**2. 数据模型和状态变化。**

- `workflow(commit_sha, definition_version)`
- `job(deps, state, attempt, lease, resource)`
- `artifact(digest)`

job 状态为 queued / running / succeeded / failed / cancelled。

**3. 走一遍一次 push。** 开发者 push 了提交 abc123，webhook 验签后按投递 id 去重，系统读取该提交里的工作流定义，生成 workflow 和三个 job：build、test、deploy，其中 test 依赖 build。调度器先把 build 放进 ready，runner 领取时拿到租约，执行时日志按 `(job, attempt, offset)` 写入并推给页面。build 成功后用 CAS 把状态提交为 succeeded 并登记产物 digest，test 随之变为 ready，依此推进。

**4. 失败、重复与恢复。**

- runner 崩溃后，租约到期，job 重新调度；结果提交用 CAS，只成功一次。
- 外部部署命令需要稳定的幂等键或事务支持。
- 日志按 job / attempt / offset 存储，不能把不同 attempt 的日志拼成一次连续成功。

**5. 容量和验证指标。** 监控队列等待、成功率、重复副作用、每租户资源配额、缓存命中率和日志延迟。push 高峰决定需要多少并发 runner，而不只是 API QPS。

### 面试追问与参考回答

**用户坚持要 exactly-once 怎么办？** 把保证范围限定在状态提交和产物发布上。任意第三方命令如果没有事务或去重协议，只能做到至少一次，或者在不确定时停下等人工恢复。

**一个租户提交了大量 job，怎样不影响其他租户？** 每个租户有并发 runner 和资源配额，调度器按租户公平轮转 ready 队列。runner 本身是隔离的，一个租户的 job 吃满资源也只会让它自己排队。

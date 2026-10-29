---
id: p3a-openai-multi-tenant-ci-cd-workflow
section: openai
order: 642
level: A
title: OpenAI：多租户 CI/CD：调度、隔离和执行语义
quick: >-
  把工作流 DAG、job 状态和租约持久化，调度器只放行依赖已满足的任务，runner 在隔离环境执行。崩溃后靠租约重新调度，结果用 CAS
  去重提交；恰好一次要限定到状态提交或产物发布，任意 shell 命令的外部效果还需要 idempotency key 或事务支持。
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
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · OpenAI · multi-tenant-ci-cd-workflow
    url: >-
      https://www.1point3acres.com/interview/problems/company/openai/multi-tenant-ci-cd-workflow
    type: secondary
---

我会把工作流和步骤状态放在持久控制面，把用户代码交给隔离 runner 执行。任务靠租约恢复，提交靠 CAS 去重；“恰好一次”只能明确保证到状态提交或产物发布。Runner 执行任意 shell 命令时崩溃，队列无法判断外部副作用是否已经发生，还要靠幂等步骤、去重协议或 transaction scope。

题目是 git push 触发用户定义的 DAG，要容错并实时展示状态。开始先确认是否需要缓存、矩阵构建和手动审批步骤；这些会影响状态模型和调度。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理。规模数字、SLO 和故障情景是手册补的练习约定。

入口接 webhook 后先验签、按投递 id 去重，再读取对应提交里的工作流定义，持久化 DAG。调度器只把依赖已满足的 job 放进 ready 队列。控制面不执行用户代码，runner 领取租约后在隔离环境运行，产物进产物存储，日志实时推给页面。

状态可以用 `workflow(commit_sha, definition_version)`、`job(deps, state, attempt, lease, resource)` 和 `artifact(digest)` 表示。Job 在 queued / running / succeeded / failed / cancelled 之间转换，日志按 job / attempt / offset 保存，避免把重试前后的输出拼成一次成功。

比如开发者 push abc123，系统生成 build、test、deploy 三个 job，test 依赖 build。先运行 build，执行日志按 `(job, attempt, offset)` 记录；成功时用 CAS 把状态改为 succeeded 并登记产物 digest，test 才进入 ready。Runner 中途崩溃则等租约到期重新调度，旧 attempt 即使回来提交，也只有一次结果能生效。外部部署命令还要用稳定的 idempotency key 或事务。

容量先看 push 高峰需要多少并发 runner，同时监控队列等待、成功率、重复副作用、每租户资源配额、缓存命中率和日志延迟，API QPS 无法单独代表执行压力。

## 追问

**用户坚持要 exactly-once 怎么办？**
把范围限定在状态提交和产物发布。第三方命令没有事务或去重协议时，只能至少一次执行，或在结果不确定时停下等待人工恢复。

**一个租户提交很多 job，其他租户会被拖住吗？**
每租户设置并发 runner 和资源配额，调度器公平轮转各租户的 ready 队列。Runner 也要隔离，这样资源被占满时主要让该租户自己排队。

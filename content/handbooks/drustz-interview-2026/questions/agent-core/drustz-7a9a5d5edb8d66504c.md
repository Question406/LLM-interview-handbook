---
id: drustz-7a9a5d5edb8d66504c
section: agent-core
order: 72
level: A
title: 分布式水平扩展（单机 harness → cluster） · 核心概念 ⭐⭐⭐
quick: 作者文档章节 · 分布式水平扩展（单机 harness → cluster） · 核心概念 ⭐⭐⭐
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - Agent · Core、Gaps 与 Benchmarks
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/scaling.md
    type: primary
---
## 核心概念 ⭐⭐⭐

| 概念 | 要点 | 面试一句话 |
|---|---|---|
| Typed task queue | SQLite 表轮询 → Redis Stream / SQS / Postgres `FOR UPDATE SKIP LOCKED`；消息只带 run_id + step 指针，payload 留在 DB；按 task 类型分 queue，独立扩缩容与限流 | 「queue 传指针不传状态，source of truth 永远在 DB」 |
| Worker lease / fencing | lease 到期即失去写权，单调递增 fencing token 拒绝僵尸 worker 的迟到写入——细节见 [state & memory](?book=drustz-interview-2026&section=agent-core&question=drustz-027e90f708cef5244f)，此处不重复 | 「lease 管活性，fencing 管安全性」 |
| Orchestrator 分片 | 按 run_id 一致性哈希，同一 run 的全部事件路由到同一 shard → shard 内单线程串行处理，免分布式锁；shard 挂/rebalance 时从 event log replay 重建内存态 | 「分片买到的是 per-run 串行化，不只是容量」 |
| Event log 外部化 | Postgres append-only 单表（`(run_id, seq)` 唯一索引做写幂等）→ 按租户/时间分区 → 写 QPS 或 fan-out consumer 数撑不住再上 Kafka（run_id 做 partition key 保 per-run 有序） | 「别一步跳 Kafka，单表分区能扛到超乎想象的量级」 |
| Durable execution | workflow code 严格 deterministic（同输入产生同 command 序列），crash 后 replay Event History 恢复；activity 至少执行一次 → 副作用必须幂等 | 「非确定性全部隔离进 activity，这是 replay 成立的前提」 |
| 两阶段放置 🤖 | reserve（DB 占位）→ node agent ack → commit；agent 静默靠 lease 超时回收 reservation；再配 reconciliation loop 对账 desired vs actual | 「placement 是跨 scheduler/DB/agent 的分布式提交，不是一次 RPC」 |
| 全局 budget / 热点租户 | token/cost 本地累加 + 异步聚合到中心，接受有界软超支；硬 cap 才走中心化 rate limiter；热点租户独立 queue/shard，隔离 noisy neighbor 保其他人 p99 | 「精确扣减和热路径低延迟不可兼得，选有界超支」 |

**Temporal 一段话**（[docs](https://docs.temporal.io/workflow-execution)）：每步执行持久化为 Event History，worker crash 后在新 worker 上 replay——已完成的 activity 直接返回存储结果不重跑，所以 LLM 调用、tool 执行、时间、随机数一切非确定性都必须包进 activity；agent 场景两个额外约束：history 有上限（约 50K events），long-horizon run 要 continue-as-new 截断；模型/prompt 升级会破坏 replay 兼容，需 versioning API 或按 run 固定版本。自建时你在复刻的就是这套 event sourcing + replay，只是把「determinism 约束」换成「显式状态机 + event log」。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/scaling.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/scaling.md)。作者整理资料；许可和第三方来源范围见阅读指南。

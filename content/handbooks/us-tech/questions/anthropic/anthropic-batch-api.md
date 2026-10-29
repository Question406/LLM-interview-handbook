---
id: anthropic-batch-api
section: anthropic
order: 21
level: A
title: Anthropic：Batch API 和在线 serving 的调度差在哪，适合什么负载？
quick: >-
  Batch 用独立队列处理可延迟的独立请求，公开价格约为在线一半，多数一小时内完成，处理窗口到 24 小时。它不占 Messages
  RPM，也不提供流式，适合评测、distillation 和离线抽取。结果按 custom_id 对账，只重试失败项，依赖 tool 结果的在线 agent
  仍留在 Messages。
tags:
  - Anthropic
  - Batch API
  - Serving
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Batch processing (Claude Docs)
    url: 'https://platform.claude.com/docs/en/build-with-claude/batch-processing'
    type: primary
  - title: Message Batches API reference
    url: 'https://platform.claude.com/docs/en/api/messages/batches'
    type: primary
---

Batch 适合可以等、彼此独立的离线工作，在线 Messages 适合用户正在等待的流式回复和工具循环。比如一批评测问题可以隔天收结果，agent 下一步却依赖当前 tool 返回，就不适合每轮丢进 Batch。

公开 API 给 Batch 约 50% 折扣，多数批次一小时内结束，但处理窗口为 24 小时，未完成条目会过期。这是 throughput 与成本的选择，平均一小时不能当尾延迟 SLO。

## 提交与结果都按独立请求管理

在线 Messages 支持同步或流式，RPM、输入与输出 token 分别限流，429 时退避，见 `anthropic-rate-limit`。Batch 通过 `POST /v1/messages/batches` 提交独立的 Messages 请求，用自己的批次提交和队列积压限额，不占在线 Messages RPM。把离线评测转去 Batch，能给交互请求腾出额度。

每条请求带 `custom_id`，JSONL 结果不保证原顺序，因此用 id 对账。单批大约最多 10 万条或 256 MB，先到为准；结果保留约 29 天。`processing_status` 从 `in_progress` 到 `ended`，计数区分 succeeded / errored / expired / canceled，一条失败不影响其他条目。

Batch 不支持 `stream: true`、Fast mode、Threads 或 `max_tokens: 0` 缓存预热。共享前缀可用 1 小时 prompt cache，见 `anthropic-prompt-cache`；批处理常超过 5 分钟，短 TTL 可能在排队时过期。在线预热应留在在线路径，或接受批内自命中。

## 调度目标决定负载选择

在线路径优化 P50/P95 TTFT、decode 平滑和用户公平，Batch 允许把请求延后，填入加速器空闲时段。排队设计上，在线用截止时间和优先级控制，Batch 是尽力而为的 throughput 队列；混部时 Batch 可以被抢占或降速，24 小时是处理窗口。

离线评测、红队和诚实性测试可用 Batch，相关集见 `anthropic-eval-honesty`、`anthropic-needle`。distillation、合成数据、CAI 批评改写、分类、审核、长文档抽取、带 citations 的证据问答，以及大 thinking 预算任务也适合，见 `anthropic-extended-thinking`。

聊天和宿主多轮 tool 循环仍走在线。文档允许 Batch 请求带 tool use，可以处理单请求内的服务端检索等工具，但同批请求仍彼此独立，不保证按依赖顺序执行。

提交后退避轮询，结束后拉 `results_url`，避免每 100ms 查一次。按 `custom_id` 入仓，只重试过期或错误项，防止成功项的非幂等工具重复执行。取消只能停止尚未开始的条目，运行中的仍计费。结果在保留期内落盘，未结束的批次也不能记成成功。

高并发消费可能略超 workspace 预算，排产需留余量。同批可混模型和 prompt，但会计与缓存命中更难解释，评测尽量保持同构。300k 生成或超大 thinking 单请求可能超过一小时，按 24 小时窗安排。

## 追问

**Batch 折扣能和 cache 叠加吗？**
官方说明可以叠加倍率。共享前缀选 1 小时 TTL 更适合批内复用，不要依赖与在线共用的 5 分钟缓存。

**在线和 Batch 混部谁优先？**
产品调度应保护在线交互，Batch 是可延迟负载。

**评测一定要 Batch 吗？**
不一定。集很小且当天就要结果时，在线也可以；Batch 的优势是成本和独立额度。

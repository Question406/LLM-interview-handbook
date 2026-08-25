---
id: anthropic-batch-api
section: anthropic
order: 21
level: A
title: Anthropic：Batch API 和在线 serving 的调度差在哪，适合什么负载？
quick: >-
  Batch 走独立队列，价大约一半，多数一小时内、SLA 到 24
  小时，不占 Messages 的 RPM。无流式、请求彼此独立，不适合聊天和要马上接 tool 的 agent。适合评测、蒸馏、离线分类、长文档抽取。波谷填谷，不要拿它扛 Tail
  SLO。
tags:
  - Anthropic
  - Batch API
  - Serving
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Batch processing (Claude Docs)
    url: https://platform.claude.com/docs/en/build-with-claude/batch-processing
    type: primary
  - title: Message Batches API reference
    url: https://platform.claude.com/docs/en/api/messages/batches
    type: primary
---

基础设施 / 应用岗会把 Message Batches 当成「便宜版 Messages」。调度模型完全不同：在线路径为 TTFT 和流式服务；Batch 为吞吐和成本，延迟可到一天。官方：大约 50% 折扣，多数批次一小时内结束，处理窗口 24 小时，超时未完成会过期。这是公开 API 题，不是内部调度论文。

## 两条队列，别混成一个限流器

在线 Messages：同步或流式，RPM / 输入 token / 输出 token 分开限，见 `anthropic-rate-limit`。429 要立刻退避，用户在等。

Batch：`POST /v1/messages/batches` 提交一组独立的 Messages 请求。HTTP 限的是「你能提交多少批次 / 队列里积压多少条」，**不占用** 在线 Messages 的 RPM。文档写明 Batches 用量不影响 Messages 限流。所以高峰时把评测卸到 Batch，是在给交互流量腾桶，不是「同一个桶换个打折开关」。

每条请求带 `custom_id`。结果 JSONL **不保证原顺序**，用 id 对账。单批次上限大约 10 万条或 256 MB，先到为准。结果保留约 29 天。`processing_status` 从 `in_progress` 到 `ended`，计数里有 succeeded / errored / expired / canceled。一条失败不拖死同批其他条。

不能做的：`stream: true`、Fast mode、Threads、`max_tokens: 0` 的 cache 预热。批处理常超过 5 分钟，共享前缀用 1 小时 prompt cache，见 `anthropic-prompt-cache`。批里写的 ephemeral cache 等你下一条在线请求时可能已经过期，所以预热要在在线路径做，或接受批内自命中。

## 调度差：SLO vs 填谷

在线 serving 优化 P50/P95 TTFT、decode 平滑、每个用户公平。Batch 优化加速器占用：把可延迟请求塞进波谷，提高利用率。面试用排队的话说：在线是有截止时间的优先队列；Batch 是尽力而为的吞吐队列。同一集群里，Batch 会被抢占或降速，所以 24 小时是硬窗不是承诺一小时。

负载合适：

- 离线评测、红队、诚实性套件（`anthropic-eval-honesty`、`anthropic-needle`）。
- 蒸馏 / 合成数据、CAI 的批评改写。
- 分类、审核、长文档抽取、带 citations 的接地问答。
- 打开很大 thinking 预算的难题，见 `anthropic-extended-thinking`。

不合适：聊天、要流式打字、agent 下一步依赖这一步 tool 结果。每轮 tool 若都丢进新批次，用户等到的是小时级。工具循环留在线；离线「单轮、自包含」才进 Batch。文档允许 batch 里带 tool use，但那是单请求内的服务端工具（检索等），不是你自己的多轮宿主循环。

## 怎么接

提交后轮询或等结束再拉 `results_url`。按 `custom_id` 写入仓。过期 / 错误单独重试，不要整批重放。花费上限：高并发下可能略超 workspace 预算，财务上按峰值留余量。和在线限流一样 fail closed：批没结束不要当成功。

错法：用 Batch 扛登录后的第一句回复；拿平均「不到一小时」当 P99 SLO；把互相依赖的 agent 步塞进同一批却假设顺序执行——它们是并行、独立的。

轮询间隔用指数退避，不要 100ms 打状态接口。结果 JSONL 按 `custom_id` 对账，不要假设和下单顺序相同。同一批可以混模型、混 prompt，但会计和缓存命中会变乱，评测集还是同构更好。超大 thinking 单请求可能单独跑过一小时，按 24 小时窗排产。失败条单独重试，成功条不要重放，避免非幂等工具双花。取消批次只能停还没开始的条目，已经在跑的仍会计费。

取消批次只能停还没开始的条目，已经在跑的仍会计费。结果文件有过期时间，评测流水线要在保留期内落盘。

和 `anthropic-prompt-cache` 一起设计：批内共享前缀、1 小时 TTL；不要指望批和在线对话共用同一条 5 分钟缓存。

## 追问

- **折扣和 cache 怎么叠？** 官方说倍率和 Batch 折扣可叠。共享前缀用 1 小时 TTL，否则批还在排队 cache 已经冷了。
- **一条 300k 生成？** 单请求就可能跑很久，按 24 小时窗排，不要再和短请求比「一小时大多完成」。
- **和在线混部时谁饿死？** 产品上应保证在线优先。Batch 是可延迟需求；饿死在线就是调度答错了。
- **评测为什么必须 Batch？** 不是必须，是单位质量更便宜、不挤用户 RPM。要当天出数且集很小，在线也行。

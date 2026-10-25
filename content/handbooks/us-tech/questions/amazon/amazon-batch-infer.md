---
id: amazon-batch-infer
section: amazon
order: 14
level: A
title: Amazon：Bedrock batch 和实时推理怎么选，吞吐和成本各看什么？
quick: "用户正在等回复时用实时 Invoke / Converse，重点看 TTFT 和 E2E p99；夜间摘要、回填和评测用 batch，看作业完成时间与成功率。Batch 把 JSONL 放到 S3 异步处理，价格通常约为按需一半，但不支持工具调用和服务端多轮。"
tags:
  - Amazon
  - Bedrock
  - Batch
  - Inference
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Process multiple prompts with batch inference
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference.html
    type: primary
  - title: Amazon Bedrock pricing
    url: https://aws.amazon.com/bedrock/pricing/
    type: primary
  - title: Monitor Amazon Bedrock with Amazon CloudWatch
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-runtime-metrics.html
    type: primary
  - title: Amazon Titan Text Embeddings V2 now available in Amazon Bedrock
    url: https://aws.amazon.com/blogs/aws/amazon-titan-text-v2-now-available-in-amazon-bedrock-optimized-for-improving-rag/
    type: primary
---

我会按有没有用户等待来选：聊天和 agent 调工具走实时，每晚十万张工单摘要等离线任务走 batch。这样能把实时配额留给用户，也避免回填任务拉高 p99。Bedrock batch 读取 `InvokeModel` 或 `Converse` 格式的 JSONL，异步处理后把结果写到 S3。

## 延迟目标和失败处理有什么不同

实时：聊天、Seller 助手、Agent 填参。用户正在等待回复。瓶颈是 首个 token 的等待时间（TTFT）、输入 Guardrail、输入预填充（prefill，即处理输入并建立缓存）、配额排队。吞吐用 in-flight 连接和 token/s 描述，长 prompt 和限流重试会显著拉高 p99。

Batch：每晚摘要十万张工单、给知识库重嵌、离线 LLM-as-judge、回放评测集。瓶颈是作业排队、S3 吞吐、记录是否可重试、失败部分如何补。实际耗时可以是分钟到小时。用实时 API 硬打十万次，会先撞 RPM，还可能拖慢用户请求、拉高 p99，影响实时服务。

两种模式可以这样对照：

| 问题 | 实时 | Batch |
| --- | --- | --- |
| 有人在等吗 | 是 | 否 |
| SLO | TTFT / E2E p99 | 作业完成时间和成功率 |
| 工具 / 多轮 | 可以 | 不行 |
| 成本 | 按需或预留 | 通常更低的批量价 |
| 失败 | 单请求重试 | 按行重跑失败 JSONL |

Embedding 是教科书例子：Titan 文档写检索步用低延迟调用，建索引用吞吐型 batch。同一模型，两条 API，见 `amazon-titan-embed`。

## 怎么估成本、安排作业

成本先按 token 数乘单价估，batch 再按公开折扣计算，通常量级约为按需一半，具体以当时价目表为准。设计里可以估「省 50%」，但要标清价格假设。评测、回填、翻译语料和日更摘要适合从实时路径挪走，把配额留给用户。

Batch 仍按队列处理 JSONL。记录要彼此独立，按长度分组统计，避免一条 32k 请求拖慢整个分片；按任务设 `max_tokens`，使用幂等 job 名，失败行单独提交。文档写了不支持跨区 inference profile 当 model id 的常见坑——作业用基础 model id，不要把实时用的路由 profile 直接塞进 `CreateModelInvocationJob`。

质量上用同一提示、温度 0 抽查 batch 与实时输出是否对齐。输入侧 Guardrails 尽量在生成 JSONL 前执行；输出证据检查可以离线再跑一趟。Batch 每条记录独立，没有服务端多轮，也不支持工具调用、`response_format` 或 Provisioned Throughput。Agent 循环仍用实时或自建编排，见 `amazon-bedrock-agents`。

观测时，实时看 `TimeToFirstToken` 和 `InvocationLatency`；batch 看作业状态、成功行数和 EventBridge 完成事件。四小时的回填任务要按作业完成目标监控。Nova 路由也是实时功能，离线评测路由策略时，应用评测集仍用离线方式运行，见 `amazon-nova`、`amazon-titan-eval`。

客服回复后轮询 S3 达不到实时体验，全库 embedding 又容易占满实时配额。作业只有 2% 失败时，按行补跑就可以，避免全量重跑。

相关：`amazon-p99-stream`、`amazon-lp-ml`。

## 追问

**p95 要 2 秒还能 batch 吗？**
不能。那是 `amazon-bedrock-rag` 的实时预算。Batch 的 SLO 是「今天早上 6 点前索引可用」。
**为什么 batch 没有 TTFT？**
没有流式用户。完成时间是作业级。硬看第一条记录何时写出没有产品意义。
**JSONL 里能不能带会话历史？**
可以当纯文本塞进单条 prompt，但记录之间不共享 KV，也没有服务端记忆。多轮仍是你自己把历史拼进去。
**和 SageMaker Batch Transform？**
自托管模型走 SageMaker；托管 FM 走 Bedrock batch。别把两套权限和重试模型糊在一起。

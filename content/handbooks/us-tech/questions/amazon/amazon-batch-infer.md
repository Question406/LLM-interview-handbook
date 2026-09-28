---
id: amazon-batch-infer
section: amazon
order: 14
level: A
title: Amazon：Bedrock batch 和实时推理怎么选，吞吐和成本各看什么？
quick: >-
  用户在等，用 Invoke / Converse（可流式），SLO 钉 TTFT 和 E2E p99。没人在等，用 batch：JSONL 上
  S3，异步出结果，公开定价大约是按需一半，吞吐靠队列而不是并发连接。Batch 不做工具调用和结构化输出，也不接 Provisioned
  Throughput。
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

平台岗把「能不能全部走实时」问成成本和配额题。Bedrock 文档：batch 把多条 prompt 异步跑完，结果写 S3；输入按 `InvokeModel` 或 `Converse` 的 JSONL 格式。**不支持 Provisioned Throughput，不支持 tool calling / `response_format`。** 每条记录独立，没有多轮。公开价通常按需折扣（量级是一半，具体看当时价目表，不要背美元）。实时尾巴怎么拆见 `amazon-p99-stream`。

## 两套时钟，两套瓶颈

实时：聊天、Seller 助手、Agent 填参。用户盯着空气泡。瓶颈是 TTFT、输入 Guardrail、prefill、配额排队。吞吐用 in-flight 连接和 token/s 描述，p99 被长 prompt 和限流重试拉爆。

Batch：每晚摘要十万张工单、给知识库重嵌、离线 LLM-as-judge、回放评测集。瓶颈是作业排队、S3 吞吐、记录是否可重试、失败部分如何补。墙钟可以是分钟到小时。用实时 API 硬打十万次，会先撞 RPM，再把 p99 用户流量打死——这是没所有权。

选法：

| 问题 | 实时 | Batch |
| --- | --- | --- |
| 有人在等吗 | 是 | 否 |
| SLO | TTFT / E2E p99 | 作业完成时间和成功率 |
| 工具 / 多轮 | 可以 | 不行 |
| 成本 | 按需或预留 | 通常更低的批量价 |
| 失败 | 单请求重试 | 按行重跑失败 JSONL |

Embedding 是教科书例子：Titan 文档写检索步用低延迟调用，建索引用吞吐型 batch。同一模型，两条 API，见 `amazon-titan-embed`。

## 吞吐和成本怎么报，才像 Amazon

成本：token 数 × 单价，batch 乘公开折扣。把「省 50%」写进设计可以，把某年某区的美元价背出来没有必要，价会变。更有用的是 **把不该实时的 token 挪走**：评测、回填、翻译语料、日更摘要。实时配额留给用户路径。这是 Frugality 加 Customer Obsession，见 `amazon-lp-ml`。

吞吐：batch 不是无限并行。服务按队列消化 JSONL。你能提高的是：记录独立、长度分桶（避免一条 32k 拖死整个 shard）、输出 `max_tokens` 不要按聊天乱开、幂等 job 名、失败行单独再提交。文档写了不支持跨区 inference profile 当 model id 的常见坑——作业用基础 model id，不要把实时用的路由 profile 直接塞进 `CreateModelInvocationJob`。

质量：同一 prompt，batch 和实时应对齐（温度 0 抽查）。不要假设异步换了另一套解码。Guardrails：能在输入侧拦的，建 JSONL 前就拦，省生成钱；输出接地若必须，离线跑第二趟，不要幻想 batch 里有完整 Agent 循环。Agent 用实时或自建编排，见 `amazon-bedrock-agents`。

观测：实时看 `TimeToFirstToken` 和 `InvocationLatency`；batch 看作业状态、成功行数、EventBridge 完成事件。不要用聊天 p99 仪表盘去「监控」一个跑了四小时的回填。Nova 路由也是实时功能，离线评测路由策略时，应用集仍离线打，见 `amazon-nova`、`amazon-titan-eval`。

错法：用 batch 做客服回复再轮询 S3 假装低延迟；用实时打全库 embedding；batch 里塞工具调用；Provisioned 已经买了还往 batch 上靠（文档写不支持）。另一错法：作业失败 2% 就全量重跑——按行补，控制成本。

## 追问

- **p95 要 2 秒还能 batch 吗？** 不能。那是 `amazon-bedrock-rag` 的实时预算。Batch 的 SLO 是「今天早上 6 点前索引可用」。
- **为什么 batch 没有 TTFT？** 没有流式用户。完成时间是作业级。硬看第一条记录何时写出没有产品意义。
- **JSONL 里能不能带会话历史？** 可以当纯文本塞进单条 prompt，但记录之间不共享 KV，也没有服务端记忆。多轮仍是你自己把历史拼进去。
- **和 SageMaker Batch Transform？** 自托管模型走 SageMaker；托管 FM 走 Bedrock batch。别把两套权限和重试模型糊在一起。

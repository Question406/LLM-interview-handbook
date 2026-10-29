---
id: amazon-p99-stream
section: amazon
order: 4
level: A
title: Amazon：流式生成的 p99，首 token 和整段完成为什么要拆开报？
quick: >-
  TTFT 衡量用户等到第一个字多久，E2E 衡量整段何时完成，两项都要报 p99。前者主要查排队、输入护栏和
  prefill，后者还要查输出长度、decode throughput 和输出护栏。聊天与工具任务分别定 SLO，再用客户端与服务端埋点定位。
tags:
  - Amazon
  - Bedrock
  - Streaming
  - Latency
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Monitor Amazon Bedrock with Amazon CloudWatch
    url: >-
      https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-runtime-metrics.html
    type: primary
  - title: >-
      Amazon Bedrock now supports observability of First Token Latency and Quota
      Consumption
    url: >-
      https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-bedrock-observability-ttft-quota/
    type: primary
  - title: Improve operational visibility for inference workloads on Amazon Bedrock
    url: >-
      https://aws.amazon.com/blogs/machine-learning/improve-operational-visibility-for-inference-workloads-on-amazon-bedrock-with-new-cloudwatch-metrics-for-ttft-and-estimated-quota-consumption/
    type: primary
---

## 可以这样回答

首 token 和整段完成要分开报，因为它们对应不同的可用时刻。聊天用户看到第一个字就能开始读，工具调用却要等 JSON 参数闭合才能执行。比如整段 4 秒、3.5 秒才出现第一个字，聊天体验仍会像卡住；首字很快，也不表示工单已经能落库。

CloudWatch 把 `TimeToFirstToken` 定义为流式 API 收到请求到第一个输出 token，`InvocationLatency` 则到最后一个 token。聊天或 Seller 助手可以定 TTFT p99，例如 800ms；Agent、JSON 工具、摘要落库和 Automated Reasoning 更关心 E2E，并结合输出 token 数看。输出翻倍时 E2E 可能翻倍，TTFT 基本不变。`amazon-bedrock-rag` 中 p95 2 秒也必须说明指哪一段。

## 技术备查

首 token 和整段完成要分开报，因为它们对应不同的可用时刻。聊天用户看到第一个字就能开始读，工具调用却要等 JSON 参数闭合才能执行。比如整段 4 秒、3.5 秒才出现第一个字，聊天体验仍会像卡住；首字很快，也不表示工单已经能落库。

CloudWatch 把 `TimeToFirstToken` 定义为流式 API 收到请求到第一个输出 token，`InvocationLatency` 则到最后一个 token。聊天或 Seller 助手可以定 TTFT p99，例如 800ms；Agent、JSON 工具、摘要落库和 Automated Reasoning 更关心 E2E，并结合输出 token 数看。输出翻倍时 E2E 可能翻倍，TTFT 基本不变。`amazon-bedrock-rag` 中 p95 2 秒也必须说明指哪一段。

## 沿请求路径拆延迟

TTFT 可以近似拆成排队、输入护栏、prefill 和网络：

$$
T_{\mathrm{TTFT}} \approx T_{\mathrm{queue}}+T_{\mathrm{input\_guard}}+T_{\mathrm{prefill}}+T_{\mathrm{net}}
$$

Prefill 随输入长度变化，这里用大约 $O(T_{\mathrm{in}})$ 的 attention 开销描述这部分。RAG 放入 20 块政策，首字预算就会被拉长，见 `amazon-bedrock-rag`。输入 Guardrail 同步运行，违规时省一次推理，通过时则增加 TTFT，见 `amazon-guardrails`。

服务端指标还不包含自家网关缓冲。反向代理攒满 chunk 才刷、CDN / SSO / 会话建立或前端等待，都可能让客户端比 CloudWatch 更慢。需要同时对上网关、服务端 TTFT 和第一个像素的埋点。

整段完成还要加 decode 和输出检查：

$$
T_{\mathrm{E2E}} \approx T_{\mathrm{TTFT}}+N_{\mathrm{out}}/R_{\mathrm{decode}}+T_{\mathrm{output\_guard}}
$$

$R_{\mathrm{decode}}$ 表示 token / s。输出 grounding 常等整段或大段才检查，会增加 E2E，未必影响 TTFT。PII 可以边流边打码，但第一个词还无法说明整句是否胡编，因此需要明确采用尾部校验还是边流弱过滤。

## 用真实长度分布找尾延迟

p99 常来自限流重试、跨区推理冷启动、同批一条 32k prompt、过大的 `max_tokens`，或客户端把流攒成一次 JSON。配额和延迟应一起看，先区分等待配额与计算慢。分布右偏时 p50 正常，p99 仍可能被排队和长输入拉高。

用线上 prompt 长度分布回放，分别画 TTFT 与 E2E 的 p50 / p95 / p99，按输入和输出长度切片。截提示、减检索块、输入拦截和扩 prefill 并发主要影响 TTFT；限制输出、speculative decoding 和小模型 decode 则影响 E2E。每段有负责人，超标时才知道该改哪里，这也对应 Insist on the Highest Standards 和 Dive Deep，见 `amazon-lp-ml`。

非流式 `InvokeModel` 只提供整段结果。产品切到打字机效果后，需要增加流式指标；原来的 E2E SLO 不能代表首屏体验。

## 追问

**能只报一个「流式 p99」吗？**
这样难以确定优化方向。同一个总值可能由输入太长造成，也可能由输出太长造成，两个阶段要分别看。

**服务端首 token 200ms，用户仍嫌慢怎么办？**
先核对客户端和网关时间。服务端 `TimeToFirstToken` 没包含完整的用户路径。

**Guardrails 怎样接入预算？**
输入检查算进 TTFT。输出证据支持可在流后校验、异步标红或先流后改；高风险域则接受更长 E2E，保留所需检查。

**acceptance checks 用 p95 还是 p99？**
用户可见路径两者都报，acceptance checks 看 p99，并追查 p95 到 p99 之间的限流和超长输入。

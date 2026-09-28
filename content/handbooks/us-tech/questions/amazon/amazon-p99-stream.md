---
id: amazon-p99-stream
section: amazon
order: 4
level: A
title: Amazon：流式生成的 p99，首 token 和整段完成为什么要拆开报？
quick: >-
  流式产品体感是首 token，工具调用和工单落库体感是整段完成。两个数的瓶颈不同：TTFT 是排队、prefill、输入
  Guardrail；E2E 是输出长度、decode 吞吐、输出校验。混成一个 InvocationLatency，p99 动了你不知道该加卡还是该截提示。
tags:
  - Amazon
  - Bedrock
  - Streaming
  - Latency
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Monitor Amazon Bedrock with Amazon CloudWatch
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-runtime-metrics.html
    type: primary
  - title: Amazon Bedrock now supports observability of First Token Latency and Quota Consumption
    url: https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-bedrock-observability-ttft-quota/
    type: primary
  - title: Improve operational visibility for inference workloads on Amazon Bedrock
    url: https://aws.amazon.com/blogs/machine-learning/improve-operational-visibility-for-inference-workloads-on-amazon-bedrock-with-new-cloudwatch-metrics-for-ttft-and-estimated-quota-consumption/
    type: primary
---

Bedrock 应用和内部 GenAI 平台岗会把延迟问成 SLO 设计。CloudWatch 现在把 `TimeToFirstToken` 和 `InvocationLatency` 分开：前者是流式 API 从收到请求到第一个输出 token，后者是到最后一个 token。和 `amazon-bedrock-rag` 的 p95 2 秒是同一类题：预算要切开，平均值没用。Amazon 口味是所有权：每个分段有负责人，p99 超了能指出是排队、prefill 还是生成太长。

## 用户感知的不是同一个时钟

聊天窗、Seller 助手：用户盯着空白气泡。第一个 token 出来就开始读，后面的 decode 被阅读盖住。这时 SLO 该钉 TTFT 的 p99，比如 800ms，而不是整段 4 秒。整段 4 秒但 3.5 秒才冒第一个字，产品体感是挂了。

Agent、JSON 工具、工单摘要落库、Automated Reasoning 要看完整答案：第一个 token 再快，函数参数没闭合也不能调工具。这时 SLO 钉 E2E / `InvocationLatency`，并按输出 token 数归一。官方也提醒：`InvocationLatency` 变差，要先分清是服务吞吐掉了，还是输出变长了。输出 token 翻倍，E2E 翻倍，TTFT 可以几乎不动。

所以面试开口：流式体验报 TTFT；完成契约报 E2E；两者都看 p99，不看平均。分布右偏，排队和限流全在尾巴上。p50 好看、p99 爆炸，是典型的批次里塞进一条超长 prompt。

## p99 尾巴拆给谁

TTFT 大致是：

$$
T_{\mathrm{TTFT}} \approx T_{\mathrm{queue}}+T_{\mathrm{input\_guard}}+T_{\mathrm{prefill}}+T_{\mathrm{net}}
$$

Prefill 跟输入长度走，大约 $O(T_{\mathrm{in}})$ 的注意力。RAG 把 20 块政策塞进提示，首 token 先死，见 `amazon-bedrock-rag`。输入 Guardrail 在生成前同步跑，拦得住省一次推理，过了的请求把评估时间叠进 TTFT，见 `amazon-guardrails`。服务端 `TimeToFirstToken` 不含你家里的网关缓冲：反向代理若攒满 chunk 再刷，客户端 TTFT 会比 CloudWatch 差一截。对账时要有一份客户端埋点。

E2E 再加：

$$
T_{\mathrm{E2E}} \approx T_{\mathrm{TTFT}}+N_{\mathrm{out}}/R_{\mathrm{decode}}+T_{\mathrm{output\_guard}}
$$

$R_{\mathrm{decode}}$ 是 token / s。输出接地检查往往要等整段或大段，会直接打在 E2E，不一定打 TTFT。流式中间拦 PII 可以边生成边打码，但 grounding「是否胡编」很难在第一个词上做完。现场要说清你选了哪种：尾部校验换尾延迟，还是边流边做弱过滤。

p99 常见凶手不是「模型慢」：限流重试、跨区推理冷启动、同批次一条 32k 提示、输出 `max_tokens` 开太大、客户端把流攒成一次 JSON。配额指标和延迟要一起看：尾巴可能是排队等配额，不是 kernel。

评测别用单条 curl。用线上 prompt 长度分布回放，分别画 TTFT 和 E2E 的 p50 / p95 / p99。A/B 换模型只报平均耗时，Bar Raiser 会追 p99 和超长输入分位。这是 Insist on the Highest Standards，不是仪表盘审美。

非流式 `InvokeModel` 没有 TTFT 这个概念，只有整段。产品一旦改成打字机效果，监控必须加流式指标，不能沿用旧的 E2E SLO 假装首屏也达标。Seller Support 那种 p95 2 秒，要写明是 TTFT 还是整段；混报会让检索和生成两段预算对不上，见 `amazon-bedrock-rag`。

## 追问

- **为什么不报一个「流式 p99」就完事？** 因为优化方向反着来。截提示、减检索块、输入拦、扩 prefill 并发，是 TTFT。截最大输出、投机解码、换小模型 decode，是 E2E。一个数两个药。
- **首 token 已经 200ms，用户还是嫌慢？** 看客户端。CDN、SSO、网关 buffer、前端等会话建立，都不在 Bedrock 的 `TimeToFirstToken` 里。先对上三张图：网关、服务端 TTFT、第一个像素。
- **Guardrails 放哪才不影响 p99？** 输入必须在首 token 前，认这笔预算。输出接地不要挡第一个字；高风险域就接受 E2E 变长，或异步标红、先流后改。别为了 p99 把接地关掉，幻觉比慢更贵。
- **p99 和 p95 报哪个？** 用户可见路径两边都报，门禁用 p99。p95 好看、p99 被限流和超长 prompt 拉开，正是 Amazon 要你 Dive Deep 的地方，见 `amazon-lp-ml`。

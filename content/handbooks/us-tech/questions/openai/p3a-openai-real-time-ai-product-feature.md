---
id: p3a-openai-real-time-ai-product-feature
section: openai
order: 635
level: A
title: "OpenAI：实时 AI 产品：流式响应、准入与成本"
quick: "实时 AI 功能要分别衡量排队时延、首 token 时延和完整响应时延，并按每个请求的 token 成本做准入，而不是只数 QPS。"
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
  - title: "1Point3Acres · OpenAI · real-time-ai-product-feature"
    url: https://www.1point3acres.com/interview/problems/company/openai/real-time-ai-product-feature
    type: secondary
---

## 题目

设计一个面向大量用户的实时或流式 AI 功能，并讨论流量变成十倍时怎么办。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；收录为面经题型不代表公司官方确认。规模数字、SLO 和故障情景是手册补的练习约定。

## 思路

先把时延拆成三段：排队时延、首 token 时延（TTFT）和完整响应时延。用户感受最强的是首 token，吞吐压力则来自完整响应。

准入控制要按请求成本算，而不是只数 QPS：一个要输出 4000 token 的请求和一个只要 50 token 的请求，消耗的 GPU 完全不同。服务端支持取消、超时和限流；客户端要区分"可以安全重试的失败"和"已经输出了一部分的失败"。

定位瓶颈时看 token 吞吐、队列长度和 GPU 饱和度这三个信号。

## 完整非编程练习（场景与参考回答）

### 具体题目与需求澄清

假设是一个实时写作助手：峰值 1000 请求/秒，平均输出 1000 token，要求首 token P95 &lt;1 秒，支持取消和流式结果。

开始回答时复述这些假设，问面试官是否有不同的用户等级，以及能否降级到更小的模型。

### 一套可展开的参考答案

**1. 架构与关键路径。**

1. 客户端通过 SSE 发起请求。
2. 鉴权和准入层按 token 预算决定接收、排队还是拒绝。
3. 请求进入有界队列。
4. 模型路由把请求发到对应的 serving 集群。

请求创建记录和生成事件流分开存。客户端凭 request id 和事件序号可以断线续传。

**2. 数据模型和状态变化。** request 记录用户、参数快照、token 预算、状态和已计费用量。状态按 accepted → queued → running → completed / cancelled / failed 变化。只输出了一部分的结果不能当成完整答案。

**3. 走一遍正常请求。** 用户选中一段文字点"润色"，客户端带幂等键发起 SSE。准入层按预估输出 token 扣减该用户和全局预算，请求入队；轮到它时 serving 开始生成，每个 token 带递增序号推给客户端，第一个 token 到达即记录 TTFT。生成结束后记录实际用量并计费，状态改为 completed。

**4. 失败、重复与恢复。**

- 队列超出预算时直接拒绝，或者告诉用户预计排队时间。
- 用户取消要传播到模型侧，及时回收 KV cache。
- 网络重连按序号去重；同一个幂等键不能悄悄创建一次新生成。

**5. 容量和验证指标。** 1000 × 1000 = 每秒 100 万输出 token，这是吞吐需求，不能直接换算成 GPU 数，必须用目标模型实测每卡的 token 吞吐。监控 TTFT、每 token 时延（TPOT）、取消后浪费的 token 和队列等待时间。

### 面试追问与参考回答

**流量变成十倍怎么办？** 先按用户和成本限流、压低输出预算或降级到更小的模型，然后再扩 GPU。放任无界队列只会把失败变成超时。

**用户在生成到一半时断网，回来后应该看到什么？** 客户端带着 request id 和最后收到的序号重连，服务端如果还保留着事件流就从断点续传。若请求已因断开被取消，就展示已收到的部分并标记为未完成，让用户选择重新生成。

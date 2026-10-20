---
id: p3a-anthropic-sd-q1-inference-api
section: anthropic
order: 621
level: A
title: "Anthropic：Inference API：动态批处理与 GPU 利用率"
quick: "推理 API 的准入层按 token 和 KV cache 预算排队，调度器用连续批处理把 GPU 填满，并在请求结束或取消时立刻回收资源。"
companies:
  - anthropic
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Anthropic · sd-q1-inference-api"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/sd-q1-inference-api
    type: secondary
---

## 题目

设计一个跨多块 GPU 的 LLM 推理服务。面试官会深入追问流量突增时怎么办，以及 prefill 和 decode 两个阶段怎样处理。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；收录为面经题型不代表公司官方确认。规模数字、SLO 和故障情景是手册补的练习约定。

## 思路

准入层按 token 数和 KV cache 预算排队，而不是按请求数。调度器支持连续批处理（continuous batching）：一个请求生成结束就立刻把它的位置让给等待中的请求，不必等整批结束。

回答里要说明三类目标和问题：首 token 时延与吞吐之间的取舍、长请求和短请求之间的公平，以及取消和 OOM 的处理。如果提出把 prefill 和 decode 分到不同机器上，要算出 KV cache 跨机传输的成本。

## 完整非编程练习（场景与参考回答）

### 具体题目与需求澄清

API 接收长短 prompt 混合的请求，支持流式响应和取消。设定 GPU 的 KV 预算、首 token 时延目标和单 token 时延目标，不预先假设所有请求成本相同。

开始回答时复述这些范围，问面试官是否有多个模型、是否有租户优先级。

### 一套可展开的参考答案

**1. 架构与关键路径。**

1. 鉴权，并按 token 预算做准入。
2. 按长度和租户进入公平队列。
3. continuous batching 调度器组批。
4. GPU executor 执行 prefill 和 decode。
5. 流式网关把 token 推给客户端。

模型版本和路由独立管理。

**2. 数据模型和状态变化。** request 记录输入和输出预算、deadline、占用的 KV blocks、所处阶段和取消状态。阶段按 prefill → decode → done 推进。还在队列里等待的请求不预占 GPU 的 KV。

**3. 走一遍一个请求。** 一个 2000 token 的 prompt 到达，准入层按"输入 2000 + 最大输出"估算所需 KV blocks，当前预算够，就放进对应长度档的队列。下一个调度步里，调度器把它加入正在运行的批次，先做 prefill 算出整段 prompt 的 KV，随后每一步和批里其他请求一起 decode 一个 token，并经网关流式返回。生成到停止符后，状态变为 done，KV blocks 立即释放，下一步就有新请求补进来。

**4. 失败、重复与恢复。**

- 准入层限制 KV 总量，在 OOM 发生之前就挡住请求。
- worker 失联时，重跑请求或明确返回失败，不把两次生成拼接成一个不连贯的结果。
- 取消时及时回收 slot 和 KV；客户端断开后不必默认一直生成到结束。

**5. 容量和验证指标。** 用实测的 token/s 反推需要多少 GPU。监控 TTFT、TPOT、排队等待、KV 利用率、padding 浪费和 SLO 违约。批次更大能提高吞吐，但也会拉高每个请求的时延。

### 面试追问与参考回答

**什么时候值得把 prefill 和 decode 分开部署？** 先估算每个请求的 KV 字节数和跨机传输时间。如果网络传输吃掉了分离带来的收益，就保留在同一张卡上做两个阶段，或者按请求长度分池。

**流量突然翻倍怎么办？** 准入层根据当前 KV 余量和队列长度估算等待时间，超出 deadline 的请求直接拒绝并返回可重试信号，而不是让队列无限变长。同时按租户配额保护付费用户，低优先级请求先被限流。

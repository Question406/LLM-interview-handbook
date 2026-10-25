---
id: p3a-anthropic-sd-q1-inference-api
section: anthropic
order: 621
level: A
title: "Anthropic：Inference API：动态批处理与 GPU 利用率"
quick: "我会按 token 和 KV cache 预算控制准入，再用连续批处理调度 GPU。一个请求结束或取消就回收资源、补进下一个请求，同时看首 token 时延、吞吐和长短请求的公平性。"
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

我会先限制能进入 GPU 的 token 和 KV 总量，再用 continuous batching 让结束的请求及时让出位置。请求长度差很多，按请求个数限流会低估长请求的成本。

比如一个 2000 token 的 prompt 到达，准入层用“输入 2000 + 最大输出”估算 KV blocks，预算允许才进入按长度和租户划分的公平队列。下一个调度步把它补进批次，GPU executor 先做 prefill，算出整段 prompt 的 KV，随后每步和其他请求一起 decode 一个 token，流式网关把结果发给客户端。遇到停止符就变成 done，立即释放 KV blocks，让新请求补进来。

请求记录要带着输入和输出预算、deadline、KV blocks、阶段和取消状态，按 prefill → decode → done 推进。排队中的请求先不占 GPU KV。模型版本和路由另外管理，入口先鉴权，再做 token 准入。

取消或客户端断开时及时释放 slot 和 KV。worker 失联时，要么重跑，要么明确报失败，两次生成直接拼起来可能不连贯。准入限制应在 OOM 前生效。

容量要从实测 token/s 倒推 GPU 数量，同时监控 TTFT、TPOT、排队等待、KV 利用率、padding 浪费和 SLO 违约。批次变大通常能换吞吐，但每个请求会更慢；如果要把 prefill 和 decode 分到不同机器，还得先算 KV 跨机传输是否划算。

### 面试追问与参考回答

**什么时候值得把 prefill 和 decode 分开部署？**
先估算每个请求的 KV 字节数和跨机传输时间。如果网络传输吃掉了分离带来的收益，就保留在同一张卡上做两个阶段，或者按请求长度分池。

**流量突然翻倍怎么办？**
准入层根据当前 KV 余量和队列长度估算等待时间，超出 deadline 的请求直接拒绝并返回可重试信号，而不是让队列无限变长。同时按租户配额保护付费用户，低优先级请求先被限流。

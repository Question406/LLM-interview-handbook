---
id: p3a-xai-rate-limiter-design
section: xai
order: 620
level: A
title: "xAI：双向限流：入口、公平队列与下游配额"
quick: "入口和出站各限自己的额度，中间用有界公平队列与背压衔接。入口通过只表示可排队，调度时还要检查出站全局令牌和剩余 deadline；取消已发出的请求也不能退回已经消耗的调用额度。"
companies:
  - xai
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - Design
  - xAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · xAI · rate-limiter-design"
    url: https://www.1point3acres.com/interview/problems/company/xai/rate-limiter-design
    type: secondary
---

## 题目

一个服务对外提供 API，内部又要调用外部模型供应商，入口和出站各有独立的限额。设计一套限流方案，让入口流量不会压垮服务，出站调用不会超过供应商配额，同时多个用户之间要公平。

> 来源：一亩三分地 xAI 题卡摘要（2026-10-18 读取），属于网站对候选人报告的二手整理，没有逐条核对原帖，网站收录也不代表公司官方确认；规模数字、SLO 和故障情景是手册补的练习约定。

我会把入口限流和出站限流分开，中间用有界队列衔接。入口保护自己的服务，出站守住供应商配额；入口允许排队，并不代表请求立刻能发给下游。

练习假设入口 100 请求/秒，下游 10 调用/秒，多个用户共享，队列最多 1000 项、最长等待 30 秒，支持公平调度和取消。持续进 100、出 10 时，每秒积压 90，约 11.1 秒队列就满，因此要在满之前拒绝或降级。先确认额度按请求还是 token、是否按用户分层、请求成本差异，以及排队超时怎样展示。

请求先经过用户和全局两层入口令牌桶，再进入按租户分组的公平队列；调度器拿到出站共享令牌才交给模型 worker。令牌与预算由统一原子存储管理。多节点可以共享原子扣减，也可以分发总量守恒的配额，不能每台机器独立用完整的供应商额度。

request 保存 (id, user, cost, deadline, state)，bucket 保存 (tokens, `last_refill`)，公平队列为各租户保存 queue cursor。比如 U 发请求，两层入口桶各扣 1 个令牌，写入 U 的子队列，置 queued，deadline 为当前时间加 30 秒。调度器轮转到 U 时，从出站桶扣令牌，再置 dispatched；worker 收到响应后置 done 并返回结果。

取消会把请求移出可调度集合，但已经发出的调用消耗了额度，要单独结算。下游 429 时按 Retry-After 暂停出站，把压力回传入口，避免立即重试形成风暴。共享存储故障时按风险选 fail-closed，或只允许有限本地额度。开场就要约定故障时宁可拒绝还是放行，不能无限透支。

监控排队时间、丢弃数、每个用户实际份额与公平份额的差距，以及外部配额利用率。请求出队时再检查剩余等待预算，避免已经来不及完成的调用继续占额度。

## 追问

**每台机器各分 10/s 可以吗？**
不可以，N 台会变成 10N/s。共享原子扣减，或 N 台各分 10/N 的租约配额，处理下线回收与时钟偏差，才能保证总量。

**等了 25 秒，只剩 5 秒，要发吗？**
先看下游预期耗时。如果 P50 就超过 5 秒，大概率来不及返回，应以超时结束；出队检查 deadline 能避免这次浪费。

相关：[[p3a-xai-twitter-insight-platform-take-home]]、[[xai-rate-limiter]]、[[p3a-xai-distributed-token-bucket-limiter]]、[[msft-azure-tpm]]

Twitter Insight 的 take-home 还要实现数据校验和 worker 重试；`xai-rate-limiter` 是每租户与全局两层懒填充令牌桶；分布式编码题把补充、检查和扣减放进共享原子存储。Azure TPM 从外部 API 调用方角度讨论配额与 429 后的降级。

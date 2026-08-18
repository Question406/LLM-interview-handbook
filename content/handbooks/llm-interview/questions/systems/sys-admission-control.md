---
id: sys-admission-control
section: systems
order: 23
level: S
title: 容量不足时，LLM API 该拒绝、排队、降级还是缩短预算？
quick: 以 SLO 和 error budget 决策，而不是平均 QPS。按 tenant/tier、deadline 与 token budget admission；设队列上限和 Retry-After，优先降级模型/工具/推理预算或拒绝低优先级请求，避免无限排队拖垮全部用户。
tags:
  - Admission Control
  - SLO
  - Reliability
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: Google SRE Book — Service Level Objectives
    url: https://sre.google/sre-book/service-level-objectives/
    type: primary
---

请求入队前估计输入/输出 token、工具次数、deadline 和用户等级。若在当前队列下无法满足 deadline，透明地返回限流、建议稍后重试或进入异步任务；不要让所有请求无限等待直至超时。

降级路径需是产品契约：选择更小模型、关闭昂贵工具、缩短 reasoning budget、只生成摘要或改异步。不同 tenant 的公平性可通过配额、并发上限和加权队列维护，而不是由最会重试的客户端抢资源。

验收看 P95/P99 latency、429/timeout、完成质量、每层队列长度和 error-budget burn。平均 QPS 低时也可能因一批超长 prompt 触发服务雪崩。

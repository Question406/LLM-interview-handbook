---
id: drustz-a8304cbb8a4d8e8346
section: anthropic
order: 98
level: A
title: Constant Latency Inference API for String List Processing
quick: >-
  original-structured-preparation-guide · Constant Latency Inference API for
  String List Processing
companies:
  - anthropic
tags:
  - DrustZ
  - original-structured-preparation-guide
  - Anthropic · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/db839215-fa43-437a-9e99-412a95249805
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Constant Latency Inference API for String List Processing

## 证据边界

当前官方页面公开描述足以确认：输入是字符串列表，输出也是字符串列表；列表长度在 1–100 之间时 API latency 应基本恒定；可使用一组 GPU servers，并需说明 data flow、database 和 network。它不是普通聊天/流式生成题。公开描述没有给模型耗时、单字符串最大长度或“constant”的误差范围；若字符串长度无上限，恒定延迟在物理上不可能，必须先要求 token 上限和明确 SLO。

## 可读需求与请求流程

假设固定模型版本，每个字符串最多 `L` tokens，返回值与输入顺序一一对应。API 同步返回，P99 在列表 1、10、100 项时都不超过同一预算，例如 150ms；过载时宁可快速 `429`，不能无限排队破坏 SLO。请求携带idempotency key，单项错误采用结构化 per-item error 或全请求失败，需与面试官确认。

```text
POST /v1/process
{"request_id":"r1","items":["a","bb","ccc"]}
→ {"request_id":"r1","outputs":["A","BB","CCC"],"latency_ms":82}

Gateway → tokenizer/validator → deadline scheduler
→ 固定 100×L padded tensor 或固定 GPU execution group
→ gather(index) 恢复顺序 → response
```



## 解法与架构

核心是用固定工作形状换取可预测时延：请求不足 100 项时 mask/pad 到 100；长度也按上限或 bucket padding。Scheduler 按 `model_version、length_bucket、deadline` 路由到预热 GPU，预分配显存，禁止冷加载进入热路径。若单卡的 batch-100 仍超预算，就把 100 项固定切到 `g` 张 GPU 并行，延迟由最慢 shard 决定；始终为每个请求预留相同 execution-group 容量。代价是小列表浪费算力，可在不突破 deadline 的前提下把多个小请求装入同一固定 batch，但必须按 request/index 拆回结果。

Hot path 只用内存队列与内部 gRPC；数据库不参与同步计算。可异步写 `request_id、model_version、status、latency、payload_hash`，结果大对象放 TTL blob store；敏感原文默认不落库。跨机 payload 设大小上限、压缩阈值和 locality-aware routing。

## 容量推导

先基准测试最坏固定 batch。若一张 GPU 处理 `100×L` 需 80ms，则单卡理论 12.5 requests/s；按 70% 利用率承载 1000 RPS 需 `ceil(1000×0.08/0.7)=115` 张 GPU，再加故障冗余。若每请求占 `g` 卡，公式再乘 `g`。队列允许等待时间必须从 150ms 总预算中扣除；autoscaling 冷启动慢，所以靠 warm capacity、admission control 和实时 queue-delay 预测，而非等队列变长才扩容。

## 边界与故障测试

测试列表长度 1/100/0/101、空字符串、重复字符串、Unicode、超长 token、输出乱序、某一项失败。GPU 崩溃时以 request ID idempotent retry到热备，但超过 deadline 立即失败；验证半数 GPU 下线会触发限流而非长队。还要测模型版本滚动发布、padding mask 泄漏、tokenizer 成瓶颈、网络分片超时、数据库不可用不影响热路径，以及 1 项与 100 项 P50/P99 差距是否真的满足“constant”定义。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/db839215-fa43-437a-9e99-412a95249805)

代码说明：无法独立解析的片段按 text 保留原文；完整代码文件可通过来源或下载包查看。


---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

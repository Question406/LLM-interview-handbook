---
id: drustz-0883d6cfb06a90f9f4
section: openai
order: 78
level: A
title: Implement an Async Message Bus for sendAsyncMessage (Simulation)
quick: >-
  original-structured-preparation-guide · Implement an Async Message Bus for
  sendAsyncMessage (Simulation)
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
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
      https://www.1point3acres.com/interview/problems/b06f318b-6c42-43eb-baec-ae8a0e10c31e
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Async Message Bus：`sendAsyncMessage` 模拟

> 旧正文把消息原语视为已经存在，目标是树拓扑聚合，并不是实现 message bus。公开页面没有 endpoint/Future 和投递保证的完整定义。

## 基础设计

维护 endpoint → handler 注册表与消息队列。`sendAsyncMessage` 只创建 envelope 并入队，返回 request ID/Future，不在调用栈中同步执行 handler。event loop/worker 出队、分发并完成 Future；请求/响应用 correlation ID 匹配。

确定性延迟模拟可使用逻辑时钟和按 `deliver_at` 排序的 min-heap：

```text
Envelope(id, source, destination, payload, deliver_at, correlation_id)
```



基础版可承诺 at-most-once；加入重试后必须有幂等 key 和 dedupe table。payload 应复制或冻结，避免发送方入队后继续修改。

## 复杂度与边界

注册/查找平均 `O(1)`；FIFO 入出队 `O(1)`，延迟 heap `O(log M)`；空间 `O(pending messages + futures + endpoints)`。覆盖未知 endpoint、handler 异常、超时取消、重复/乱序、回调再次发消息、无限循环、背压、公平和关闭时 pending 工作。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/b06f318b-6c42-43eb-baec-ae8a0e10c31e)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

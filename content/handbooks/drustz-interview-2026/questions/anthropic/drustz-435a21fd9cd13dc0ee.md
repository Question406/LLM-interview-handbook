---
id: drustz-435a21fd9cd13dc0ee
section: anthropic
order: 73
level: A
title: Route Multiple Prompt Calls to Multiple GPT Servers Using a Hash Table
quick: >-
  original-structured-preparation-guide · Route Multiple Prompt Calls to
  Multiple GPT Servers Using a Hash Table
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
      https://www.1point3acres.com/interview/problems/46a64535-7d55-4b9f-af3e-9db6d856187a
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 用哈希把 Prompt 请求路由到多个 GPT Server

> 公开信息只确认“用哈希表路由多个 prompt 调用”；路由键、服务器动态变化和失败语义未公开。旧正文是 GPU batching inference API，现已移除。

## 固定服务器池

为每个请求选择稳定 routing key：按 prompt 内容可提高相同请求的缓存粘性；按 tenant/request ID 通常更均衡。固定服务器列表时：

```text
server_index = stable_hash(routing_key) % server_count
```



按服务器分组批量发送，并保存原始请求下标；异步响应返回后按下标还原输出顺序。不能使用 Python 进程随机化的 `hash()` 做跨进程稳定路由，应选固定算法。

## 动态服务器池

服务器会增删时使用一致性哈希环和虚拟节点，减少重映射。健康检查失败时顺时针选择下一健康节点；重试携带相同 idempotency key，避免下游重复执行。热点 key 可加 bounded-load 一致性哈希或在多个候选中选当前队列最短者。

## 复杂度与边界

固定池每请求平均 `O(1)`；一致性哈希每次查找 `O(log(VS))`，建环 `O(VS log(VS))`。覆盖空服务器池、Unicode/空 prompt、热 key、上下线、超时、乱序响应、背压和重试幂等。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/46a64535-7d55-4b9f-af3e-9db6d856187a)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

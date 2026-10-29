---
id: drustz-cd2c682ec221882aa3
section: openai
order: 62
level: A
title: >-
  Coding: Design a Distributed Rate Limiter with Persistence (Clock Skew, Redis
  Fallback)
quick: >-
  original-structured-preparation-guide · Coding: Design a Distributed Rate
  Limiter with Persistence (Clock Skew, Redis Fallback)
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
      https://www.1point3acres.com/interview/problems/ee08a6d0-0eac-4767-86af-19287ae5af50
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 分布式限流器：持久化、时钟偏差与 Redis Fallback

## 题目要解决什么

实现 `allowRequest(key, now_ms)` 与 `reset(key)`。多个应用实例共享配额；需要处理 clock skew、Redis 不可用时的本地降级与文件持久化，以及 Redis 恢复后的异步重放和并发测试。

## 正常路径

选择 sliding-window log：每个 key 使用 Redis ZSET 保存窗口内已接受请求。Lua 脚本在一次原子操作中完成：

```text
读取 Redis TIME
删除窗口外成员
检查当前数量
允许时插入带唯一 request_id 的成员
```



使用 Redis 时间避免 app server 时钟偏差；传入的 `now_ms` 只用于确定性测试或范围校验。

## Redis 故障时的策略

fallback 没有通用正确答案，必须按业务风险选择：

- **Fail closed**：拒绝请求，保护昂贵或敏感下游，但降低可用性；
- **Fail open**：继续放行，适合低风险读请求，但可能造成过载；
- **Local emergency window**：每实例只使用预分配的保守子配额，并用线程安全 deque 记录；每次 allow/reject/reset 追加到本地 WAL。

WAL 事件带幂等 request ID 与 generation；`reset` 增加 generation，防止恢复重放时让已经重置的旧请求“复活”。恢复后只重放仍在窗口内、属于当前 generation 的准入事件。网络分区期间无法同时保证严格全局配额和持续服务，保守子配额以利用率换取超发上界。

## 并发与恢复

Lua 脚本保证单 key 原子性；本地 deque、WAL 与 reset 使用同一 key/shard 锁。Redis 恢复后先验证 generation，再逐步退出 fallback，避免惊群。至少测试正常限流、窗口端点、并发、clock skew、Redis 故障/恢复和 reset。

## 复杂度与边界

单次 ZSET 操作约 `O(log q + r)`，其中 `q` 是 key 的窗口内请求数、`r` 是本次清掉的过期项；所有请求只被清理一次。空间为活动窗口内已接受事件数。还要覆盖磁盘满、WAL 尾记录损坏、重放幂等、Redis 主从切换和配置变更。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/ee08a6d0-0eac-4767-86af-19287ae5af50)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

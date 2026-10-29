---
id: drustz-d24ee040d4b3f93a80
section: agent-core
order: 74
level: A
title: 分布式水平扩展（单机 harness → cluster） · 常见坑 ⭐⭐
quick: 作者文档章节 · 分布式水平扩展（单机 harness → cluster） · 常见坑 ⭐⭐
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - Agent · Core、Gaps 与 Benchmarks
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/scaling.md
    type: primary
---
## 常见坑 ⭐⭐

- [ ] 开场直接上 Kafka/K8s/微服务——说不出每步演进的触发指标，senior 面大忌
- [ ] 把完整 run state 塞进 queue 消息——queue 是投递机制不是 source of truth，at-least-once 重投即状态错乱
- [ ] 讲 replay 不讲 determinism 约束——LLM 调用不包 activity/不存结果，replay 直接产生分叉执行
- [ ] 分片只讲 hash 不讲 rebalance——答不出「从 event log 重建 shard 内存态」等于没做过
- [ ] 全局 budget 每个 token 同步扣中心 DB——热路径上造全局锁；正解是本地累加异步聚合 + 有界超支

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/scaling.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/scaling.md)。作者整理资料；许可和第三方来源范围见阅读指南。

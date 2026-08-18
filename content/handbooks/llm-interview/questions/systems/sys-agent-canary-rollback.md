---
id: sys-agent-canary-rollback
section: systems
order: 26
level: A
title: 如何为模型、system prompt、tool schema 与 retrieval index 的组合变更做 canary 和一键回滚？
quick: 把每个组件显式版本化。先过离线 golden / 对抗切片，再 shadow 和小流量 canary；发布阈值同时覆盖 task success、安全拒绝、格式率、P95 latency 和成本，并保留兼容 schema 与完整回滚 artifact。
tags:
  - Canary
  - Rollback
  - Agent Operations
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: Google SRE Workbook — Canarying Releases
    url: https://sre.google/workbook/canarying-releases/
    type: primary
---

Agent 的一次“模型升级”通常同时改变 prompt、tool schema、retrieval index、policy 和 evaluator。若只记录 model ID，线上回归无法定位。为每个组件生成 immutable version 和兼容性声明，在线请求/trace 也携带组合版本。

发布顺序是离线 golden 与安全对抗集、shadow replay、小流量 canary、逐步扩大。gate 应同时比较 task completion、格式/工具错误、安全拒绝、人工升级、P95 latency 和每任务成本；只看平均 win rate 会漏掉高风险退化。

回滚要能把整组版本还原，包括 index snapshot 和 schema adapter。对有外部副作用的 tool call 使用幂等键、审计和 kill switch，避免半发布状态持续执行。

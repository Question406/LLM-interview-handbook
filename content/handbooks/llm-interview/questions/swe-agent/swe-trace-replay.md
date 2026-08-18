---
id: swe-trace-replay
section: swe-agent
order: 4
level: A
title: 一次失败怎样可重放？Coding Agent 的 trace 需要记录哪些字段，才能归因？
quick: 记录输入/上下文 hash、模型与 prompt/schema 版本、每次 tool request/response、文件 diff、image digest、seed、时间和权限决策；用根 span 串联 LLM、工具与测试，并把 snapshot 与外部副作用版本化。
tags:
  - Tracing
  - SWE Agent
  - Debugging
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-17
sources:
  - title: OpenTelemetry Specification Overview
    url: https://opentelemetry.io/docs/specs/otel/overview/
    type: primary
---

根 span 对应一个 issue resolution attempt；子 span 对应检索、LLM generation、shell/tool call、文件编辑、测试和 review。每个 span 带 request ID、开始结束时间、输入摘要 hash、模型/工具版本、成本、错误码和权限决策。

重放还需要 repo SHA、容器 image digest、依赖锁、环境变量引用、seed、网络 mock 和每次 filesystem snapshot/diff。外部 API 响应若不能重放，至少保留脱敏录制件并标注其版本。

trace 既要能查模型幻觉，也要能识别工具超时、测试不稳定和 policy 拒绝。未经脱敏的源码、secret 和用户数据不可直接进入通用 observability 后端。

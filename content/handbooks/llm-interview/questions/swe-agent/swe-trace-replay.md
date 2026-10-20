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
updatedAt: 2026-08-21
sources:
  - title: OpenTelemetry Specification Overview
    url: https://opentelemetry.io/docs/specs/otel/overview/
    type: primary
---

「看了模型回复」不够归因。一次 SWE 失败可能来自幻觉、工具超时、测试 flaky、依赖漂移或 policy 拒绝。没有可重放 trace，事后只能猜。面试官要听的是：根 span 串起哪些子系统，哪些字段足以在相同镜像上 replay，哪些数据绝不能进通用日志。Trace 既是调试工具，也是评测合同的一部分：没有它，resolved 不可审计。

## 字段合同

根 span 对应一次 issue resolution attempt；子 span 覆盖检索、LLM generation、shell / 编辑、测试、review。每个 span 至少带：request ID、起止时间、输入摘要 hash（不要默认存全文）、模型 / 输入提示（prompt） / tool 字段和类型规范（schema） 版本、token 数与费用、错误码、权限决策（allow / deny / escalate）。文件系统侧记录每次 edit 的 diff 与关键路径 snapshot；环境侧记录 repo SHA、image digest、依赖锁、环境变量引用（值脱敏）、seed、网络 mock 版本。外部 API 若不能重放，保留脱敏录制件并标版本。时间戳要对齐测试日志，否则无法判断「是命令失败还是测到了旧状态」。缺 request ID 关联，tool 结果就可能被接到错误的下一步 prompt 上。

## 怎样重放、怎样归因

重放分两级：确定性 replay（同镜像、同 mock、同命令序列）验证工具与评测器；条件 replay（同输入 hash、重采样模型）验证模型方差。归因时看第一个不可恢复错误：是观察错、计划错、命令被拒、测试不稳定，还是 evaluator 误判。后续连锁失败不要全部算根因。trace 要能回答：这一步的上下文是否已过期、这一次 tool 结果是否被后续 prompt 看到、policy 拒绝是否被模型当成「环境坏了」而瞎改。聚合时按 first-failure 类别切片，而不是按最终退出码。能重放才能说「修了模型」还是「修了 flaky 测试」。

## 失败模式与隐私

评测上能刷或失效的点：只记最终 patch、不记中间命令；把 secret 和源码全文打进 APM；没有 span 关联导致 tool 结果对不上 request；时钟不同步；用 LLM 读自己的 trace 当唯一根因。未经脱敏的源码、凭证、用户数据不能进通用 observability 后端；用 hash + 受控对象存储，并设 TTL 销毁。没有销毁策略的 trace 会变成新的泄密面。支持重放的失败记录才能用于持续排障，仅保存聊天日志通常不够。落地最小字段集：`attempt_id`、输入 hash、镜像 digest、模型版本、逐步 tool IO、diff、权限决策、测试状态转移、first-failure 标签。缺关联 ID 或脱敏策略，trace 要么不能重放，要么不能进生产。

排障时先重放工具与测试，再决定要不要重采样模型。若确定性 replay 已经失败，问题在 harness 或环境，不该先怪模型。脱敏策略与 TTL 写进同一份 tracing 设计，避免调试通道变成泄密通道。

## 追问

- **为什么要输入 hash 而不是全文？** 可关联、可去重、默认可进日志；全文按需从受控存储取。
- **flaky test 怎么在 trace 里看出来？** 同 patch 重跑测试状态翻转，且模型侧 span 无新 edit。
- **和 run contract 怎么分？** `swe-run-contract` 定义一次尝试的输入输出；本题定义逐步字段才能定位是哪一层坏了。
- **工具超时怎么标？** 标在 tool span 的错误码，不要并进模型幻觉；重放时应能单独注入同一超时。

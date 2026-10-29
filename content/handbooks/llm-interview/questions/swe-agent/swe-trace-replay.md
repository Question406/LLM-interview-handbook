---
id: swe-trace-replay
section: swe-agent
order: 4
level: A
title: 一次失败怎样可重放？Coding Agent 的 trace 需要记录哪些字段，才能归因？
quick: "每一步都要记：输入和上下文的 hash、模型与 prompt/schema 版本、每次 tool 的 request/response、文件 diff、image digest、seed、时间和权限决策。用根 span 把 LLM、工具和测试串起来，snapshot 和外部副作用都做版本化，这样失败才能重放、才能归因。"
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

要让失败可重放，trace 得用一个根 span 串起 LLM、工具和测试，每一步记下输入 hash、各种版本、tool 的请求和响应、文件 diff、环境 digest、seed 和权限决策。光看模型回复归不了因。没有它，resolved 也没法审计，所以它本身就是评测合同的一部分。

一次 SWE 失败可能来自 hallucination，也可能是工具超时、测试 flaky、依赖漂移或者 policy 拒绝。比如模型调 `run_test` 时被 policy 拒了，它以为是环境坏了，开始乱改代码，最后 patch 失败。只看聊天记录，你会以为模型不会修；有了 trace，第一步出错的位置一目了然。

字段这样定。根 span 对应一次 issue resolution attempt，子 span 覆盖检索、LLM generation、shell 和编辑、测试、review。每个 span 至少带 request ID、起止时间、输入摘要的 hash（默认别存全文）、模型 / prompt/ tool 字段和类型规范（schema）的版本、token 数和费用、错误码、权限决策（allow / deny / escalate）。文件系统那边，记录每次 edit 的 diff 和关键路径的 snapshot；环境那边，记 repo SHA、image digest、依赖锁、环境变量引用（值要脱敏）、seed、网络 mock 版本。外部 API 不能重放的，保留脱敏的录制件并标好版本。时间戳要和测试日志对齐，否则分不清是命令失败了，还是测到了旧状态。少了 request ID 关联，tool 结果可能被接到错误的下一步 prompt 上。

重放分两级。确定性 replay 用同一个镜像、同一套 mock、同一串命令，验证工具和评测器；条件 replay 保持输入 hash 不变、重新 sampling 模型，验证模型的方差。我排障时先做确定性 replay，如果它都失败了，问题在 harness 或环境，不该先怪模型。

归因看第一个不可恢复的错误：是观察错了、计划错了、命令被拒了、测试不稳定，还是 evaluator 误判。后面的连锁失败不全算根因。trace 要回答得了这几个问题：这一步的上下文是不是已经过期；这次 tool 结果后面的 prompt 有没有看到；policy 拒绝有没有被模型当成「环境坏了」去瞎改。聚合统计按 first-failure 类别切片，别按最终退出码。能重放，才说得清这次是修了模型还是修了 flaky 测试。

隐私也要一起设计。未经脱敏的源码、凭证、用户数据不能进通用的 observability 后端，用 hash 加受控对象存储，再设 TTL 销毁。没有销毁策略的 trace 会变成新的泄密面，脱敏和 TTL 要写进同一份 tracing 设计。评测上容易失效的地方有：只记最终 patch，不记中间命令；把 secret 和源码全文打进 APM；没有 span 关联，tool 结果对不上 request；时钟不同步；让 LLM 读自己的 trace 当唯一的根因判断。只存聊天日志一般不够做持续排障。

落地的最小字段集是 `attempt_id`、输入 hash、镜像 digest、模型版本、逐步 tool IO、diff、权限决策、测试状态转移、first-failure 标签。缺了关联 ID，trace 不能重放；缺了脱敏策略，trace 进不了生产。

## 追问

**为什么存输入 hash，不存全文？**
hash 能关联、能去重，默认就可以进日志；全文需要时再从受控存储里取。

**flaky test 在 trace 里怎么看出来？**
同一个 patch 重跑，测试状态翻转了，而模型侧的 span 没有新的 edit。

**这题和 run contract 怎么分？**
`swe-run-contract` 定义一次尝试的输入和输出；这题定义逐步要记哪些字段，才能定位是哪一层坏了。

**工具超时怎么标？**
标在 tool span 的错误码上，别并进模型 hallucination；重放时要能单独注入同一个超时。

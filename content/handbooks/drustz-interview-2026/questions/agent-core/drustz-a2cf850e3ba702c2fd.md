---
id: drustz-a2cf850e3ba702c2fd
section: agent-core
order: 23
level: A
title: 05 · Reliability 与 Failure Recovery · 2. 每个失败回答四问 ⭐⭐⭐
quick: 作者文档章节 · 05 · Reliability 与 Failure Recovery · 2. 每个失败回答四问 ⭐⭐⭐
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/05_reliability.md
    type: primary
---
## 2. 每个失败回答四问 ⭐⭐⭐

| 问题 | 要回答什么 |
|---|---|
| Detection | 什么 signal 能发现？ |
| Containment | 如何缩小 blast radius？ |
| Recovery | 如何回到已知状态？ |
| Prevention | 加什么 invariant/eval/tool 改进？ |






**示例：三类高频失败的四问速答**



| 失败 | Detection | Containment | Recovery | Prevention |
|---|---|---|---|---|
| write 类工具 timeout | executor timeout 信号 | 状态标 `unknown`，暂停同类写 | 按 `operation_key` 查外部 status 再决定重试 | idempotency key + retry matrix（见 [./01_loop_and_tools.md](?book=drustz-interview-2026&section=agent-core&question=drustz-78ebf691851b815a7d)） |
| prompt injection | context 中 source/trust level 标记 + adversarial eval | 权限在 executor 层，注入无法提权 | 撤销未审批 proposal，审计 trace | security 控制清单（见 [./06_eval_security.md](?book=drustz-interview-2026&section=agent-core&question=drustz-4e50f8e0f483daa35c)） |
| worker crash | lease 过期 | fencing token 拒绝过期 worker 的迟到写 | 重新 claim，retry 前查 operation status | lease + attempt 机制（见 [./02_state_and_memory.md](?book=drustz-interview-2026&section=agent-core&question=drustz-027e90f708cef5244f)） |





> 高分句：「再问模型一次」不是完整 recovery strategy——四问缺一个，答案就不完整。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/01_core/05_reliability.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/05_reliability.md)。作者整理资料；许可和第三方来源范围见阅读指南。

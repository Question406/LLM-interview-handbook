---
id: byte-harness-engineering
section: agent
order: 200
level: S
title: 字节 Agent 实习一面：什么是 Harness Engineering？和只调 LLM API 差在哪？
quick: >-
  Harness 是模型外的操作系统：权限、工具执行、状态、日志、校验与重试。调 API
  只负责生成文本。复杂任务能完成，是因为每步被约束、可观测、失败可回放，不是模型更会聊天。
tags:
  - ByteDance
  - Harness
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 字节跳动-Agent开发实习生 一面（45分钟）
    url: https://www.nowcoder.com/feed/main/detail/931a8a935a5e4b4f8d0b71cd4e818604
    type: candidate-first-hand
  - title: 字节实习 agent开发一面
    url: https://www.nowcoder.com/feed/main/detail/075c06bf50a143a785c039f9951624f6
    type: candidate-first-hand
---

## 真题记录

- 公司：字节跳动
- 岗位：Agent 开发实习；一面
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“什么是Harness Engineering”**；**“Harness的五个核心模块”**；**“你对 Agent Harness 怎么理解？它和单纯调用 LLM API 的区别是什么？”**

错法：把 Harness 讲成「更好的 system prompt」或「SDK 再包一层 chat API」。模型只产出意图文本；复杂任务能跑完，是因为每一步被约束、可观测、失败可回放。同一权重换一套工具错误码和重试策略，成功率可以差一截。测的是 model + harness，不是「模型更会聊天」。概念总览见 `agent-harness`。

## 五个控制面怎么切

划法不唯一，我会覆盖模型外职责，不背五个英文词。常用切法：

- **感知 / 上下文组装**：当前任务、仓库切片、工具观察、权限可见范围，决定窗口里放什么。
- **规划**：把目标拆成可验证子步骤；规划仍是模型，但步数、终止、是否允许改计划由 Harness 卡死。
- **受控工具执行**：schema 解析、鉴权、沙箱、超时、幂等；模型说「删文件」不等于真删。
- **记忆**：短记忆服务本轮，长记忆跨会话；写入要带来源和失效条件，见 `byte-short-long-memory`。
- **观测与策略**：日志、trace、超时、重试、审批。失败按错误码分类，而不是一律再问一遍模型，见 `byte-tool-fail-retry`。

Coding Agent 里「只有 shell」和「repo 检索 + 测试 + patch 回滚 + 结构化状态」是两套 Harness。权限与审计是执行层的一部分，不是 prompt 附录，见 `byte-team-agent-security`。

## 和只调 LLM API 差在哪

只调 API：无权限边界、无确定性回放、失败只能重问。Harness 决定能不能跑、跑在哪、结果怎么验。模型产出 tool call 文本；Harness 校验参数、查 ACL、在沙箱执行、把结构化 Observation 写回。没有 executor，所谓 Agent 只是多轮聊天。

可回放要求：同一输入、同一工具版本、同一工作区快照，应得到同一执行图。这依赖工具副作用可记录、观察规范化，而不是温度调到 0。预算与终止（最大步数、token、墙钟）也必须在环外，否则模型会把「再试一次」写成无限循环。

## Spec 是校验器，不是又一段 prompt

规格、单测、禁止改的路径是判定「这一步对不对」的预言机。Harness 负责跑测试、比 diff、失败按策略重试或升级。Spec 解决可判定，Harness 解决判定之后谁执行，二者配合见 `byte-spec-sdd-openspec`。没有规格时 Agent 只能靠观感，只调 API 也做不了长任务。

## 追问

- **五个模块必须是哪五个？** 不必背死。能讲清上下文、规划约束、受控执行、记忆、观测恢复，并指出权限与评测落在哪一层即可。
- **换模型为什么成绩差很多？** 工具 schema、错误文案、Observation 格式变了，等于策略分布偏移。训练要锁 harness 版本，并做 cross-harness 对照。
- **Harness 和 Skills 什么关系？** Skill 是按需展开的程序化知识；Harness 决定何时加载、如何隔离不可信输出。Skill 写在仓库里不等于已经有执行与权限系统。
- **最小可上线集是什么？** 解析器、鉴权沙箱、步数预算、结构化日志、失败分类。缺这几项，演示能跑、生产会把副作用写进真实环境。

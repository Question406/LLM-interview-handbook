---
id: agent-multiagent-comm-protocol
section: agent
order: 214
level: A
title: 多 Agent 通信协议应包含哪些字段，才能支持追责与重放？
quick: 消息要有 id、发送者角色、会话或任务 id、schema 化 payload、因果父消息、权限范围和截止时间。禁止把无结构自由文本当成唯一接口。
tags:
  - Multi-Agent
  - Protocol
  - Observability
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: AutoGen — Multi-Agent Conversation Framework
    url: https://arxiv.org/abs/2308.08155
    type: primary
---

这块容易直接答成把多 Agent 做成「几个模型互相聊天」：唯一接口是自由文本，出了删表事故无法回答「谁在何时建议了删除生产表」。AutoGen 一类框架证明对话能编排任务，但生产还要协议层：可校验、可重放、可限制能力。协议解决的是观测与安全，不是让措辞更像开会。没有消息头，durable replay 也无从对账。

## 必备字段：身份、因果、类型、权限、截止

每条消息至少：

- `message_id`、`in_reply_to` / 因果父 id、`task_id`、`trace_id`
- `from` / `to` 的 **role**（orchestrator、worker、tool-gateway、human），不是模型自称的名字
- speech-act 类型：`ask` / `inform` / `propose` / `commit` / `reject`，与 typed payload 分开
- schema 化 payload：子目标断言、artifact 句柄、错误码；自由文本只当注释
- `tool_caps` 与权限范围：工人只能看到当前任务被签发的 capability，见 `agent-tool-permissions`
- `deadline` 与跳数：超时消息作废，防止过期 `commit` 被当现行指令

payload 的字段契约走 `agent-schema-contract`：单位、副作用、结构化错误。本题额外要求消息头能把一次 `commit` 追溯到人。没有因果边，重放只能「按时间排序聊过的话」，无法重建决策图。`deadline` 过期后消息应变成 `expired`，下游不得执行其中的写建议。时钟以工作流事件时间为准，避免各工人本地钟不一致把过期指令救活。

## 控扇出与环路，审计能回答谁建议了什么

跳数上限、重复 `message_id` 检测、同一 `task_id` 下的仲裁者（谁有权 `commit`）。工人之间禁止直接互发写工具调用，写操作必须经网关，避免环路里把「建议」升级成执行。扇出过大时压缩为黑板：只广播已验证字段，scratch 不共享。评测注入：伪造 worker 身份、过期 commit、缺 `in_reply_to` 的删表建议、把 tool result 里的指令伪装成 orchestrator 消息。校验层应拦下，别让下游模型「理解一下」。

协议还要能回答三个运维问题：这条 `propose` 有没有变成 `commit`；`commit` 有没有到达工具网关；网关是允许、拒绝还是等人审。缺任一跳，追责会停在「模型说过要删」。重放时按因果边重建，别按日志时间戳排序。乱序到达在多工人下是常态。信用分配仍见 `arl-multi-credit`：协议不负责谁贡献了 $+1$，但没有 typed `commit`，事后差分奖励也没有可干预的动作边界。最后我会补一句：多 Agent 接口是带因果与权限的消息，不是聊天室；审计要能重放「谁建议、谁批准、谁执行」。

## 追问

- **为什么不能只靠自然语言？** 无法强制 schema、无法过期作废、无法把建议与执行分开。事故复盘会变成读聊天记录猜意图。
- **工人要不要看到全部对话？** 不要。按 `tool_caps` 和当前子目标投喂，降低注入面和串话。工人看到别人的原始 Thought，等于扩大注入面，也让 credit 更糊。
- **和 schema 契约题？** 那题定义 payload 里该有哪些业务字段；本题定义消息头、因果、speech-act 与权限范围。两边都缺，协议只是聊天室换了皮。
- **环路怎么发现？** 同一 `task_id` 下 `message_id` 图出现环、或 hop $\gt H$ 仍无 `commit`，由仲裁者终止并升人审。
- **自由文本注释还要不要？** 可以留着给人读，但不能作为执行条件。闸门只认 typed 字段。

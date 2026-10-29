---
id: agent-multiagent-comm-protocol
section: agent
order: 214
level: A
title: 多 Agent 通信协议应包含哪些字段，才能支持追责与重放？
quick: >-
  每条消息至少带 id、发送者角色、任务 id、因果父消息、speech-act 类型、符合 schema 的
  payload、权限范围和截止时间。自由文本只当注释，执行只认 typed 字段，出了事才能顺着因果边查清谁建议、谁批准、谁执行。
tags:
  - Multi-Agent
  - Protocol
  - Observability
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: AutoGen — Multi-Agent Conversation Framework
    url: 'https://arxiv.org/abs/2308.08155'
    type: primary
---

每条消息至少要有消息 id 和因果父 id、任务和 trace id、收发双方的角色、speech-act 类型、符合 schema 的 payload、权限范围和截止时间。自由文本可以留着当注释，但执行只认这些 typed 字段，这样出了事故才能顺着因果链查清谁建议、谁批准、谁执行。

设想几个 Agent 只靠自由文本聊天，某天一张生产表被删了。翻聊天记录只能看到「这张表可以清掉」「好的」，谁在什么时候提的、有没有人批准、哪个工人真正调了删除，都说不清。AutoGen 一类框架证明了对话能编排任务，可生产系统还需要能校验、能重放、能限制权限的通信协议，它解决的是观测和安全。没有消息头，持久化重放时也没法核对每一步的决策。

## 必备字段

- `message_id`、`in_reply_to` / 因果父 id、`task_id`、`trace_id`
- `from` / `to` 写 role（orchestrator、worker、tool-gateway、human），不用模型自称的名字
- speech-act 类型 `ask` / `inform` / `propose` / `commit` / `reject`，和 typed payload 分开
- 符合 schema 的 payload，装子目标断言、产物句柄、错误码，自由文本只用于注释
- `tool_caps` 和权限范围，工人只能看到当前任务签发给它的 capability，见 `agent-tool-permissions`
- `deadline` 和跳数，超时消息作废，免得一个过期的 `commit` 被当成现行指令

payload 里的业务字段契约走 `agent-schema-contract`，单位、副作用、结构化错误都在那边；这题额外要求消息头能把一次 `commit` 追溯到人。没有因果边，重放只能把聊过的话按时间排一遍，重建不出决策图。`deadline` 过期的消息变成 `expired`，下游不得执行里面的写建议。时钟以工作流的事件时间为准，免得各个工人的本地时钟不一致，把过期指令又救活了。

## 限制扩散与环路

接着要防消息扩散和环路。设跳数上限，检测重复的 `message_id`，同一个 `task_id` 下指定一个仲裁者，只有它有权 `commit`。工人之间禁止直接互发写工具调用，写操作必须经过网关，免得在环路里把「建议」一步步升级成执行。扇出太大时改成黑板，只广播验证过的字段，scratch 不共享。

协议还要能回答三个运维问题：这条 `propose` 有没有变成 `commit`；`commit` 有没有到达工具网关；网关是允许、拒绝还是在等人审。缺任何一跳，追责就停在「模型说过要删」。重放时按因果边重建，别按日志时间戳排序，多工人场景下乱序到达是常态。评测可以注入几种攻击：伪造 worker 身份、过期的 commit、缺 `in_reply_to` 的删表建议、把 tool result 里的指令伪装成 orchestrator 消息。这些都应该在校验层被明确拒绝，不交给下游模型去判断。

## 追问

**为什么不能就用自然语言？**
自然语言没法强制 schema，没法让过期消息作废，也没法把建议和执行分开，事故复盘会变成读聊天记录猜意图。自由文本注释可以留给人读，但不能当执行条件，acceptance checks 只认 typed 字段。

**工人要不要看到全部对话？**
不要。按 `tool_caps` 和当前子目标喂信息，能减少注入面和串话。工人看到别人的原始 Thought，等于扩大注入面，credit 也更难分清。

**这和 schema 契约那题怎么分？**
那题定义 payload 里该有哪些业务字段；这题定义消息头、因果、speech-act 和权限范围。缺了哪部分，执行都控不住，决策也重建不出来。

**环路怎么发现？**
同一个 `task_id` 下 `message_id` 图出现环，或者 hop $\gt H$ 还没有 `commit`，就由仲裁者终止并升级给人审。

**协议和多 Agent 的 credit assignment 有关系吗？**
有间接关系。credit assignment 见 `arl-multi-credit`，协议不负责算谁贡献了 $+1$；但没有 typed `commit`，事后做差分奖励时也找不到可以干预的 action boundaries。

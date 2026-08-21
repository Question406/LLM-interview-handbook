---
id: arl-retry
section: agentrl
order: 12
level: S
title: Tool Timeout 能不能自动 Retry？
quick: >-
  先判断 side effect 与 idempotency。GET/search 一般可重试；send_money/send_email/delete
  等非幂等操作在不知道第一次是否成功时不能直接重复。
tags:
  - Failure Recovery
  - Idempotency
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: A practical guide to building AI agents
    url: >-
      https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
    type: primary
---

Timeout 只说明「没在时限内听到回音」，不说明服务器没做成。对 `send_email` / 转账 / 删除，盲目 replay 会双发。陷阱是把 HTTP 超时当成「没执行，再来一次」。Agent 实践指南把工具失败恢复写成状态机问题，而不是「模型再试一次」的生成问题。

## 先问副作用与幂等，超时先查状态

只读（GET、search、拉状态）通常可重试，配合退避。写操作必须先问：是否幂等、有没有 idempotency key / 事务 id。安全状态机：PARSE → VALIDATE → AUTHORIZE → EXECUTE → $\{SUCCESS,\ TIMEOUT,\ ERROR\}$。TIMEOUT 且可能有副作用时，下一跳是 **query status**，不是再调 `send_email`。状态查询本身应只读、可重复。分布式里严格 exactly-once 很难，工程上靠幂等接口 + 持久去重（同一 key 只落地一次）达到等效。没有 key 就不要让模型发明「再发一遍」。

Schema 必须把「超时后查单」写成契约，并给出 `status_url` / `UNKNOWN_SIDE_EFFECT`，见 `agent-schema-contract`。训练数据若把「超时后重发邮件」标成成功 recovery，会强化危险策略。

## 按错误类分流，禁止盲放

- **429 / 瞬时网络：** 指数退避，可对幂等读重试。
- **INVALID_ARGUMENT：** 回给模型改参，不要原样重放。
- **PERMISSION_DENIED：** 停，走授权，不重试。
- **TIMEOUT + 未知副作用：** 查单；查单也失败则保持 pending，延迟再查或请用户确认，绝不自动再发送。

Retry 是同一意图下确认状态或改参；re-plan 是目标分解变了（见 `agent-when-to-replan`）。把两者混成「模型自己看着办」，高风险动作会在超时循环里被执行多次。评测应注入「第一次其实已成功但响应丢失」，看 Agent 是否去查而不是再发。

训练标签也要按此切：幂等读超时后重试可以标正；`send_email` 超时后不查直接再发应标危险负例。Harness 应提供 `get_status(idempotency_key)`，否则模型没有合法下一跳。产品上超时默认 pending 而不是失败重放——用户看到「发送中」比收到两封同样的信便宜得多。把 retry 写进系统提示而不做幂等键，等于没做。面试收口：超时 ≠ 没执行。只读可退避重试；`send_email` 先查状态。没有幂等键就不要自动 replay。评测要注入「其实已成功但回包丢了」，看它查单还是再发一封。

## 追问

- **Exactly-once 真能做到吗？** 分布式里严格语义很难。工程上用幂等接口 + 持久 dedup/事务做等效：同一 key 只落地一次，超时先查再决定。
- **Status query 自己也失败？** 保持 pending，不自动重复副作用。延迟重查或转人工/用户确认。查单失败不是「当作没做过」的许可证。
- **和 re-plan 的差别？** Retry 是同一意图下确认状态或改参；re-plan 是目标分解或约束变了。见 `agent-when-to-replan`。超时循环里重规划仍不能盲放 `send_email`。
- **训练里怎样标超时？** 幂等读超时后重试可标正；写操作超时不查直接再发应标危险负例。Harness 若不提供查单接口，模型没有合法下一跳。
- **429 和权限错误能同一套重试吗？** 不能。429 退避；权限拒绝要停。混用会把越权打成瞬时故障，扩大爆炸半径。

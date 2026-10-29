---
id: arl-retry
section: agentrl
order: 12
level: S
title: Tool Timeout 能不能自动 Retry？
quick: >-
  要看操作有没有副作用、重复调用是否幂等。GET、search 这类只读调用一般可以退避重试；send_money、send_email、delete 这种非
  idempotent operation，不知道第一次成没成功时不能直接再发，要先查状态。
tags:
  - Failure Recovery
  - Idempotency
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: A practical guide to building AI agents
    url: >-
      https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
    type: primary
---

能不能重试，先看这个操作有没有副作用、重复调用是不是幂等。只读的 GET、search 超时了，退避重试就行；`send_email`、转账、删除这种写操作超时了，下一步应该是去查状态，不能直接再调一遍。

原因在于 timeout 只说明没在时限内收到回音，服务器可能已经做完了。比如 Agent 调 `send_email`，邮件其实发出去了，只是响应在路上丢了，它要是当成没执行再来一次，用户就会收到两封一样的邮件。OpenAI 那份 Agent 实践指南也把工具失败恢复当成状态机问题处理，让模型自己再生成一次解决不了。

所以我会把一次工具调用写成状态机：PARSE → VALIDATE → AUTHORIZE → EXECUTE → $\{SUCCESS,\ TIMEOUT,\ ERROR\}$。遇到 TIMEOUT 而且可能有副作用，下一跳是 query status，状态查询本身要只读、可重复。写操作要先问有没有 idempotency key 或事务 id。分布式里严格 exactly-once 很难，工程上靠 idempotent API 加持久去重，同一个 key 只落地一次，效果上就等价了。没有 key，就别让模型自己发明「再发一遍」。这些要写进 schema 当契约，给出 `status_url` 或 `UNKNOWN_SIDE_EFFECT`，见 `agent-schema-contract`。

不同错误走不同的路。429 或瞬时网络问题，对幂等读做指数退避重试；INVALID_ARGUMENT 要把错误回给模型改参数，原样重放没用；PERMISSION_DENIED 就停下来走授权，不重试；TIMEOUT 加上未知副作用就去查单，查单也失败，就保持 pending，延迟再查或者请用户确认，绝不自动再发送。产品上超时默认显示 pending，用户看到的是「发送中」，也就不会收到重复的同一封邮件。

训练和评测也按这个切。幂等读超时后重试，可以标成正例；`send_email` 超时后不查直接再发，要标成危险负例。训练数据要是把「超时后重发邮件」标成成功的 recovery，就是在强化危险策略。Harness 要提供 `get_status(idempotency_key)`，不然模型根本没有合法的下一跳。评测要专门注入「第一次其实成功了、只是响应丢了」，看 Agent 会不会先去查。只在系统提示里写 retry 规则、不做 idempotency key，等于没做。

## 追问

**Exactly-once 真能做到吗？**
严格语义很难。工程上用 idempotent API 加持久 dedup 或事务做到等效：同一个 key 只落地一次，超时先查再决定。

**状态查询自己也失败了怎么办？**
保持 pending，不自动重复副作用，延迟重查，或者转人工、找用户确认。查单失败不能当成「没做过」的许可证。

**Retry 和 re-plan 有什么区别？**
Retry 是同一个意图下确认状态或者改参数；re-plan 是目标分解或约束变了，见 `agent-when-to-replan`。两者混成「模型自己看着办」，高风险动作会在超时循环里被执行好几次。就算在重规划，也不能盲放 `send_email`。

**429 和权限错误能用同一套重试吗？**
不能。429 退避，权限拒绝要停。混在一起，会把越权当成瞬时故障，扩大爆炸半径。

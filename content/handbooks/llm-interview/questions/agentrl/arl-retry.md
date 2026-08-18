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
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-17'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>先判断 side effect 与 idempotency。GET/search 一般可重试；send_money/send_email/delete 等非幂等操作在不知道第一次是否成功时不能直接重复。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><p>一个安全 state machine：PARSE → VALIDATE → AUTHORIZE → EXECUTE → {SUCCESS, TIMEOUT, ERROR}。遇到 timeout 时，若 action 有 side effect，应先 query status / transaction ID。</p><p>常用机制：idempotency key、transaction ID、at-most-once / exactly-once semantics、dedup store。</p><p>Retry policy 也要按 error class：429/temporary network → exponential backoff；invalid arguments → 让模型修参数；permission denied → 不重试；unknown side-effect status → query status / ask user。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Exactly-once 真能做到吗？</summary><div class="follow-answer"><p>分布式系统里严格 exactly-once 很难，常通过 idempotent operation + durable dedup/transaction 达到等效语义。</p></div></details><details class="followup"><summary>Status query 自己也失败怎么办？</summary><div class="follow-answer"><p>保持 operation pending，不自动重复 side effect；可延迟重查、转人工/用户确认。</p></div></details></div>

---
id: code-retry
section: coding
order: 8
level: S
title: 实现 Tool Retry + Idempotency：Timeout 后为什么不能直接重试？
quick: >-
  Timeout 只说明客户端没看到结果，不代表服务端没执行。对有副作用的操作必须用 idempotency key 或 transaction
  ID，先查状态或让 server 去重。retry policy 按 error class 分类。
tags:
  - Agent
  - Distributed Systems
realInterview: false
status: published
format: legacy-html
provenance: legacy-handbook-v2
updatedAt: '2026-08-21'
sources: []
---
<div class="quick"><div class="mini-title">30 秒回答</div><p>Timeout 只说明客户端没看到结果，不代表服务端没执行。对有副作用的操作必须用 idempotency key 或 transaction ID，先查状态或让 server 去重。retry policy 按 error class 分类。</p></div>
          <div class="full-answer"><div class="mini-title">完整答案</div><pre><code data-lang="python">async def safe_execute(tool, args, client, max_attempts=3):
    key = make_idempotency_key(tool, args)
    for attempt in range(max_attempts):
        try:
            return await client.call(tool, args, idempotency_key=key)
        except TimeoutError:
            status = await client.get_status(key)
            if status == &quot;SUCCEEDED&quot;:
                return await client.get_result(key)
            if status == &quot;RUNNING&quot;:
                continue
            if status == &quot;FAILED_RETRYABLE&quot;:
                await backoff(attempt)
                continue
            raise
    raise RuntimeError(&quot;retry budget exhausted&quot;)</code></pre><p>GET、search 这类幂等 read 通常可以安全重试。send_money、send_email、delete 或 create resource，可能产生重复副作用。理想 API 在服务端用 idempotency key 建唯一执行记录，客户端重复请求拿到同一结果。</p><p>错误至少要分成：4xx invalid argument 或 permission，通常不该重试；429/5xx/transient，可以退避；unknown outcome，先查状态；semantic failure，需要模型改 action，而不是把原调用再打一遍。</p></div>
          <div class="followups"><div class="mini-title">常见追问与答案</div><details class="followup"><summary>Exactly-once 真能严格做到吗？</summary><div class="follow-answer"><p>跨分布式系统里所谓 exactly once，常常是靠幂等的 side effect 加可持久化的 transaction state，做成可观察上的一次。网络层仍可能是 at-least-once delivery。我会把 transport 和业务语义分开讲。</p></div></details></div>

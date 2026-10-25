---
id: slime-router-session
section: systems
order: 264
level: A
title: 多轮 Agent 在 slime 里为什么要把 router 改成 session affinity？
quick: "多轮请求要用同一 `session_id` 回到同一 worker，才能复用 history 的 KV；可以用 `consistent_hashing` 固定路由。PD 分离时还要保证 decode worker 拿到对应 KV，否则会重算或失败。"
tags:
  - slime
  - Agent RL
  - SGLang
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: slime SGLang Config
    url: https://thudm.github.io/slime/advanced/sglang-config.html
    type: primary
  - title: slime Agentic RL Roadmap
    url: https://thudm.github.io/slime/get_started/agent.html
    type: primary
---

多轮 Agent 要把同一个 session 的后续请求送回同一 worker，复用已经算好的 history KV。默认 `cache_aware` 可能换 worker，让每轮重新 prefill 整段历史，工具史变长后实际耗时可能翻倍。PD 分离时，请求送错逐 token 生成（decode）机器还会找不到对应 KV。

自定义 `generate` 打 router 不打单机。slime 给每条 `Sample` 分配 `session_id`；`consistent_hashing` 用这个 key（请求头 `X-SMG-Routing-Key`）钉住同一 worker，前缀 KV 才能命中。写多轮循环时要保持 id，经过 router 路由；每轮换 id 或随机直连 engine，会让每轮都冷启动。

单轮、没有共享前缀时，固定 worker 的收益有限。多轮工具调用或 PD 分离中，若 KV 在 A 机、下一请求发到 B 机，就需要重算，甚至直接失败，路由也就关系到请求能否正确执行。

- `round_robin`：调试、无前缀可复用。
- `cache_aware`（默认）：单轮、按缓存水位切流，谁热去谁。
- `consistent_hashing`：多轮 / 工具史 / PD，按 `session_id` 钉住。

`cache_aware` 会把同一会话的下一轮作为新请求，按当时水位换机。别的会话可能命中了公共模板，让全局命中率仍然很高，但本会话的 history 物理页在另一张卡上，这一轮还是冷启动。和 vLLM sticky routing + prefix cache 是同一类问题，见 `sys-prefix-cache`。验收看同一 `session_id` 是否连续打到同一 worker，不要只看全局 prefix hit。

veRL 的 SGLang multi-turn 同样吃 session；若用 vLLM 则靠 prefix cache + sticky，能力取决于后端。`loss_mask` 决定训练图是否对观测结果（observation）计算梯度，router 的 session 粘性决定推理 KV 留在哪张卡。这两项需要分别配置：掩码正确但路由仍是 round-robin，依然会付出反复 prefill 的时间。

## 追问

**每轮换新 `session_id` 会怎样？**
哈希换机，history KV 全废，每轮整段 prefill。多轮 Agent 的长尾往往出在这里，不是模型变慢。
**PD 不开 affinity 呢？**
prefill 机算出的 KV 不在 decode 机上，要么重传失败，要么当新请求重算。PD 和 affinity 是配套。
**`cache_aware` 为什么单轮够用？**
单轮没有「下一跳还必须回同一页」的约束，按水位切流能提高前缀命中。
**和 `loss_mask` 能互相替代吗？**
不能。一个管不算梯度，一个管 KV 在哪。两个都要配。
**绕过 router 直连 engine 图省事？**
多轮会丢 affinity，PD 时 KV 也对不上。调试可以，生产必须走 router。

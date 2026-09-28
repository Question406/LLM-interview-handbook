---
id: slime-router-session
section: systems
order: 264
level: A
title: 多轮 Agent 在 slime 里为什么要把 router 改成 session affinity？
quick: >-
  默认 `--router-policy cache_aware` 按前缀缓存切流，单轮够用。多轮必须让同一
  `sample.session_id` 打到同一 worker，否则每轮 prefill 重算整段 history。设
  `--router-policy consistent_hashing`，请求头 `X-SMG-Routing-Key`。PD 分离时更要开，否则 decode
  机没有你的 KV。
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

错法：多轮 Agent 仍用默认 `cache_aware`，或把「router 粘 session」和「`loss_mask` 掩 observation」说成一件事。前者是 KV / 前缀缓存落在哪张卡；后者是梯度算不算这段 token。政策错了，每轮把整段 history 重 prefill，工具史一长墙钟翻倍。PD 分离时更致命：decode 机上没有你的 KV。

## 为什么必须钉住 worker

自定义 `generate` 打 router 不打单机。slime 给每条 `Sample` 分配 `session_id`；`consistent_hashing` 用这个 key（请求头 `X-SMG-Routing-Key`）钉住同一 worker，前缀 KV 才能命中。自己写多轮循环时不要每轮换新 id，也不要绕过 router 随机挑 engine。看起来在「负载均衡」，其实每轮冷启动。

单轮、无共享前缀时，粘不粘差别不大。多轮、工具返回、PD 拆开之后，粘性是正确性而不只是加速：KV 在 A 机，请求打到 B 机，不是慢，是要重算或直接失败。

## 三种政策

- `round_robin`：调试、无前缀可复用。
- `cache_aware`（默认）：单轮、按缓存水位切流，谁热去谁。
- `consistent_hashing`：多轮 / 工具史 / PD，按 `session_id` 钉住。

`cache_aware` 会把「同一会话的下一轮」当成新请求，按当时水位换机。前缀看起来能 share，物理页却在另一张卡上，命中率统计仍可能很好看（别的会话的公共模板命中了），本会话 history 却在冷启动。和 vLLM sticky routing + prefix cache 是同一类问题，见 `sys-prefix-cache`。验收看同一 `session_id` 是否连续打到同一 worker，不要只看全局 prefix hit。

## 和 veRL、梯度掩码分开说

veRL 的 SGLang multi-turn 同样吃 session；若用 vLLM 则靠 prefix cache + sticky，能力取决于后端。面试把两句话拆开：`loss_mask` 掩 observation 是训练图；router 粘 session 是推理 KV。只做掩码、路由是 round-robin，采样已经贵了，梯度再正确也救不了墙钟。

## 追问

- **每轮换新 `session_id` 会怎样？** 哈希换机，history KV 全废，每轮整段 prefill。多轮 Agent 的长尾往往出在这里，不是模型变慢。
- **PD 不开 affinity 呢？** prefill 机算出的 KV 不在 decode 机上，要么重传失败，要么当新请求重算。PD 和 affinity 是配套。
- **`cache_aware` 为什么单轮够用？** 单轮没有「下一跳还必须回同一页」的约束，按水位切流能提高前缀命中。
- **和 `loss_mask` 能互相替代吗？** 不能。一个管不算梯度，一个管 KV 在哪。两个都要配。
- **绕过 router 直连 engine 图省事？** 多轮会丢 affinity，PD 时 KV 也对不上。调试可以，生产必须走 router。

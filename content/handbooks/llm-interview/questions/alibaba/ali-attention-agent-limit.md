---
id: ali-attention-agent-limit
section: alibaba
order: 12
level: A
title: Agent 多轮对话里，Attention 的局限性体现在哪？
quick: 上下文长度与噪声、长程依赖被稀释、工具结果和历史混在一起会 distraction、计算/显存随序列平方或线性涨。它替代不了显式状态和记忆系统。
tags:
  - Alibaba
  - Agent
  - Attention
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
---

这块容易直接答成「上下文已经 128k，记忆问题解决了」。多轮 Agent 里，Attention 只是窗口内的软检索，不是外部状态机。局限是：上下文长度与噪声、长程依赖被稀释、工具结果与历史混杂导致 distraction、计算/显存随序列平方（或线性注意力下的线性）增长。它无法替代显式状态、记忆、权限和终止条件。公式底盘见 `ali-attention-math`。

## 窗口内软寻址 vs 显式状态

$\mathrm{softmax}(QK^{\top}/\sqrt{d})$ 把质量分给当前序列里的所有位置。轮次少、证据短、约束都在当前窗口时够用。工具 observation 变长、跨会话偏好、或需要审计「当时依据是什么」时，必须上 Memory / State / Skill / Harness（见 `ali-skill-memory-rag`）。这不是把 Transformer 换掉，而是系统层补偿：Attention 便宜但不可靠；RAG/Memory 是显式寻址，可审计、可过期。新旧记忆冲突时还要有取舍策略（`ali-memory-conflict`）。

## 工具日志如何把关键约束冲淡

多轮 tool observation 堆积后，真正关键证据被冲淡。第 1 轮用户说「别改价格」；第 12 轮工具回了三页商品 JSON，Attention 更容易对齐到最新字段，把早先约束稀释掉，Agent 开始改价。正确做法是把「禁止改价」写入结构化 state，每轮强制注入，而不是指望 softmax 还记得第 1 轮。跨很早之前的约束/用户偏好，纯 attention 不可靠。也无法天然提供可审计的外部状态、权限与终止条件。这些必须在编排层，见 `ali-guardrail`。

## 复杂度与「加长上下文硬扛」

朴素注意力是 $O(T^{2}d)$；即便线性注意力/SSM 把二次项换掉，distraction 还在：更长窗口意味着更多噪声 token 来抢权重。靠加长上下文硬扛多轮工具日志，p95 延迟和走神一起升。工程上应对：observation 摘要与截断、只把本轮决策需要的字段注入、会话状态外置、热点路径缓存。双十一流量下这会变成容量问题（`ali-double11-scale`）。

KV cache 只避免重算历史 $K,V$，不提供「按 key 取约束、过期、权限」的记忆 API。Agent 若把整段 trace 当 prompt，softmax 会把质量分给最新、最长的 JSON 字段，而不是分给第 1 轮的业务红线。Skill 解决的是可复用程序；Memory 解决的是跨会话可寻址事实；RAG 解决的是外部知识。三者都是显式寻址，和 Attention 的软寻址互补，不要互相替代（对照 `ali-skill-memory-rag`）。最后我会补一句：Attention 是窗口内可微检索；多轮 Agent 的状态机必须外置。

## 追问

- **和 RAG 的关系？** RAG/Memory 是显式寻址，Attention 是窗口内软寻址；前者可审计、可过期，后者便宜但不可靠。
- **KV cache 能当记忆吗？** Cache 只避免重算 $K,V$，不提供可查询、可过期、可权限控制的记忆 API。
- **线性注意力就解决了吗？** 只换复杂度，不换「没有显式状态」这个缺口。

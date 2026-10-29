---
id: ali-attention-agent-limit
section: agent
order: 12
level: A
title: Agent 多轮对话里，Attention 的局限性体现在哪？
quick: >-
  Attention 只是窗口内的软检索：上下文越长噪声越多，早先的约束容易被后面的工具结果冲淡，计算和显存还随序列长度增长，普通 attention
  平方增长，线性 attention 线性增长。所以多轮 Agent 仍需要显式状态和记忆系统。
tags:
  - Alibaba
  - Agent
  - Attention
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: ↗ 淘天大模型 Agent 校招面经
    url: 'https://www.nowcoder.com/discuss/911218249889480704'
    type: legacy-reference
---

多轮 Agent 里 Attention 的局限，在于它只是窗口内的软检索，当不了外部状态机。上下文越长噪声越多，长程依赖会被稀释，工具结果和历史混在一起会分散 attention（distraction），计算和显存还随序列长度增长，普通 attention 是平方，线性 attention 是线性。所以「上下文已经 128k，记忆问题解决了」这个说法站不住，显式状态、记忆、权限和终止条件它都替代不了。

最直观的例子是约束被冲淡。第 1 轮用户说「别改价格」，第 12 轮工具回了三页商品 JSON，Attention 更容易对齐到最新的字段，早先那条约束被稀释，Agent 开始改价。正确做法是把「禁止改价」写进结构化 state，每轮强制注入，别指望 softmax 还记得第 1 轮。

从机制上看，$\mathrm{softmax}(QK^{\top}/\sqrt{d})$ 只是把 attention 权重分给当前序列里的各个位置。轮次少、证据短、约束都在当前窗口里时够用。工具 observation 变长、有跨会话偏好，或者需要审计「当时依据的是什么」，就得上 Memory / State / Skill / Harness，见 `ali-skill-memory-rag`。这些是系统层的补偿，Transformer 不用换。Skill 管可复用的程序，Memory 管跨会话可寻址的事实，检索增强生成（RAG）管外部知识，三者都是显式寻址，可审计、可过期，和 Attention 的软寻址互补，谁也替代不了谁。新旧记忆冲突时还要有取舍策略（`ali-memory-conflict`）；权限和终止条件放在编排层，见 `ali-guardrail`。

复杂度上，朴素 attention 是 $O(T^{2}d)$。线性 attention 或 SSM 能把二次项换掉，distraction 还在，窗口越长，越多无关 token 分走 attention 权重。靠加长上下文硬扛多轮工具日志，p95 延迟可能升高，模型也更容易忽略关键约束。工程上的办法是对 observation 做摘要和截断，只注入本轮决策需要的字段，会话状态外置，热点路径加缓存。双十一流量下，这就成了容量问题（`ali-double11-scale`）。相关公式见 `ali-attention-math`。

## 追问

**Attention 和 RAG 是什么关系？**
RAG / Memory 是显式寻址，Attention 是窗口内的软寻址。前者可审计、可过期，后者便宜但不可靠。

**KV cache 能当记忆用吗？**
不能。Cache 只是避免重算历史的 $K,V$，不提供按 key 取事实、过期和权限控制的记忆 API。Agent 把整段 trace 当 prompt 时，softmax 还可能把更多权重分给最新、最长的 JSON 字段。

**换成线性 attention 就解决了吗？**
只换了复杂度，「没有显式状态」这个缺口还在。

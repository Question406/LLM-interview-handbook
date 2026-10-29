---
id: ali-hitl-risk
section: agent
order: 31
level: A
title: 闪购面经：Human-in-the-Loop 与高风险异常管控怎么做？
quick: >-
  高风险工具调用前由服务端强制用户确认，判断不可靠时暂停，连续失败就熔断转人工。工具按只读、可逆、不可逆分级，沙箱和生产隔离，调用和确认都留审计；STOP_CONDITION
  要写进指令，更要由编排状态机和工具网关的代码执行。
tags:
  - Alibaba
  - HITL
  - Agent
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: ↗ 淘宝闪购 Agent 算法一面
    url: 'https://www.nowcoder.com/discuss/879393838081597440'
    type: legacy-reference
---

Human-in-the-Loop 我会在编排层用代码强制执行：关键工具调用前插确认，判断不可靠就暂停，连续失败就熔断转人工。只把 STOP_CONDITION 写在 prompt 里，用户一催，模型就可能直接调不可逆 API。闪购的履约、改地址、取消订单、赔付，错了都是资损，所以这道面经题的核心是高风险异常靠代码路径兜住，不靠模型自觉。

比如用户连发「快点取消这单」。Agent 查到订单已经出餐，就必须停在确认页，展示「出餐后取消可能扣违约金」，等人点了确认才调取消工具。如果工具连续超时三次，就熔断。

权限分三级：只读、可逆写入、不可逆。查商家、查配送这类只读操作可以自动；出餐后取消、改送达地址、赔付属于不可逆。连续失败 $N$ 次就熔断转人工，别让模型换参数死循环；低置信或连续失败时暂停，比让模型「再试一次」安全。工具结果互相矛盾、金额超过阈值，或者意图分类熵较高、难以确定用户意图时，都可以触发暂停。

确认本身不能被注入跳过。确认 UI 不能被工具返回的文本改成「已确认」，session 里的确认状态由服务端签发；用户催促、工具返回「已为你取消」这类文本，都不能把服务端的确认标志翻成已确认。所以 STOP_CONDITION 要同时出现在三处：prompt 里复述、编排状态机、工具网关，只写第一处等于没写。权限分级的总则见 `ali-guardrail`。

沙箱和生产要隔离，密钥、订单库、支付通道都分开，免得评测 agent 打到真单。缺少线上 feedback loop 时，用任务成功率做 DPO/PPO，在沙盒里用 ELO 选优；生产写操作照样走 HITL。Agent 的 RL 如果只看最终成功，会学到绕过确认的捷径，过程约束要把「没确认就调用」当硬失败（`ali-agent-final-reward`）。高峰降级时也不能摘掉 HITL（`ali-double11-scale`）。长周期记忆分层压缩，冷启动时靠检索关键事件（`ali-skill-memory-rag`、`ali-memory-conflict`）。

审计要记谁在什么时候确认了哪个 tool、参数哈希、下游单据号。没有审计，资损没法追责，评测也没法把越权从 hallucination 里拆出来（`ali-agent-eval-dims`）。

## 追问

**STOP_CONDITION 写在 prompt 里够不够？**
不够。不可逆 API 要在代码层拦截，prompt 只是复述。

**人会不会成为瓶颈？**
只对不可逆动作和高金额操作要求确认，读路径全自动，再用熔断阈值控制升级量。

**沙箱里选出的策略怎么上生产？**
沙箱用成功率和 ELO 选策略；上了生产，写路径仍走 HITL，工具身份和沙箱密钥隔离。

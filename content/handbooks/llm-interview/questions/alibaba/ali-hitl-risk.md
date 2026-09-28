---
id: ali-hitl-risk
section: alibaba
order: 31
level: A
title: 闪购面经：Human-in-the-Loop 与高风险异常管控怎么做？
quick: 关键 tool 前插入确认；低置信暂停；工具分级+熔断；沙箱与生产隔离；结构化审计。指令里写清 STOP_CONDITION，并在代码层强制执行。
tags:
  - Alibaba
  - HITL
  - Agent
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 淘宝闪购 Agent 算法一面
    url: 'https://www.nowcoder.com/discuss/879393838081597440'
    type: legacy-reference
---

错法：把 STOP_CONDITION 只写在 prompt。用户一催，模型就直接调不可逆 API。闪购履约、改地址、取消订单、赔付等错了有资损的动作，Human-in-the-Loop 必须在编排层强制。关键 tool 前插入确认；低置信暂停；工具分级加熔断；沙箱与生产隔离；结构化审计。指令里写清停止条件，并在代码层执行。权限分级总则见 `ali-guardrail`。

## 三级权限 + 熔断，确认不能被注入跳过

只读 / 可逆写入 / 不可逆 三级权限。只读查商家、查配送可以自动。不可逆：出餐后取消、改送达地址、赔付。连续失败 $N$ 次熔断，转人工，而不是换参数死循环。低置信或连续失败时暂停，比让模型「再试一次」更安全。确认 UI 不能被工具返回文本注入成「已确认」；session 里的确认状态由服务端签发。

例子：用户连发「快点取消这单」。Agent 查到订单已出餐后，必须停在确认页，展示「出餐后取消可能扣违约金」，等人点确认才调取消工具。工具连续超时三次则熔断。人会不会成瓶颈：只对不可逆和高金额闸门，读路径全自动，并用熔断阈值控制升级量。

## 沙箱与生产隔离，RL 不要在真单上探索

长周期记忆分层压缩，冷启动靠检索关键事件（`ali-skill-memory-rag`、`ali-memory-conflict`）。承认缺闭环时，用任务成功率做 DPO/PPO 与沙盒 ELO 选优；生产写操作仍走 HITL。Agent RL 若只靠最终成功，会学到绕过确认的捷径，过程约束必须把「未确认就调用」当硬失败（`ali-agent-final-reward`）。高峰降级不能摘掉 HITL（`ali-double11-scale`）。

审计：谁在何时确认了哪个 tool、参数哈希、下游单据号。没有审计，资损无法追责，评测也无法把越权从 hallucination 里拆开（`ali-agent-eval-dims`）。

STOP_CONDITION 要同时出现在三处：prompt 复述、编排状态机、工具网关。只写第一处等于没有。用户催促、工具返回「已为你取消」这类文本，都不能把服务端确认标志翻成已确认。低置信暂停可以用：工具结果互相矛盾、金额超阈值、意图分类熵高。沙箱与生产密钥、订单库、支付通道必须隔离，避免评测 agent 打到真单。闪购面经的核心是：高风险异常靠代码路径，不靠模型自觉。

## 追问

- **STOP_CONDITION 写在 prompt 够不够？** 不够。代码层拦截不可逆 API；prompt 只是复述。
- **人会不会成瓶颈？** 只对不可逆和高金额闸门；读路径全自动；熔断阈值控制升级量。
- **沙箱策略怎么上生产？** 沙箱用成功率/ELO 选策略；生产写路径仍 HITL，且工具身份与沙箱密钥隔离。

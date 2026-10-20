---
id: ali-guardrail
section: agent
order: 28
level: S
title: 如何控制 Agent 自主性边界？Safety Guardrail 怎么设计？
quick: 规则引擎负责强制执行约束，LLM 负责理解和推理。工具按只读、可逆、不可逆分级，不可逆操作执行前需要人工确认。输出要过滤，实际动作也要经过策略引擎检查。
tags:
  - Alibaba
  - Safety
  - Agent
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 淘天 Agent 开发技术面
    url: 'https://www.nowcoder.com/feed/main/detail/4c8da8a740e64eb5827fb1b962928eda'
    type: legacy-reference
  - title: ↗ 淘宝闪购 Agent 算法一面
    url: 'https://www.nowcoder.com/discuss/879393838081597440'
    type: legacy-reference
---

常见误区是：把 Guardrail 写进 system 输入提示（prompt） 的「不要越权」。规则引擎强制执行约束，LLM 负责理解和推理。工具分级为只读 / 可逆 / 不可逆；不可逆前人工确认。输出过滤与策略引擎是双闸门，自主性随风险升高而降低。边界必须写在编排和工具服务端。HITL 细节见 `ali-hitl-risk`，幻觉拦截见 `ali-hallucination-intercept`。

## 分层：输入 → 工具权限 → 执行确认 → 输出 → 审计

退换货、赔付、改地址等规则明确、出错会造成资金损失的场景，优先规则/工作流，LLM 负责理解与填槽，不负责改规则。开放闲聊、低风险推荐可以给更高自主性。分层：输入安全（注入、越权指令）→ 工具权限矩阵 → 不可逆执行确认 → 输出合规检查 → 审计日志。prompt 可以复述规则，但不能当唯一闸门：模型在用户催促下会「灵活通融」。

例子：用户说「帮我把这单直接退了并原路赔付」。Agent 可以填槽、查订单、解释政策，但「发起退款」属于不可逆，必须命中规则（七天无理由、未拆封）且弹出确认；规则不满足则拒执行。只读查物流不需要确认。失败模式：把赔付金额交给模型「看着办」，或 prompt 写了「不要越权」却把退款 API 暴露给任意会话。

## 和内容安全不是同一道闸

内容安全拦违禁输出；Guardrail 还要拦错误动作（错退、错改地址、越权查单）。两者都要审计，但动作闸门更靠策略引擎和工具服务端鉴权。高并发下降级不能把写路径闸门摘掉（`ali-double11-scale`）。编排若用开源自动重试，必须在服务端做幂等，否则确认过的写操作会被重放（`ali-framework-choice`）。

强化学习（RL） 训练时若最终成功包含「绕过确认」，过程奖励会强化越权，必须把权限失败当硬负例（`ali-agent-final-reward`、`ali-reward-hacking`）。评估要单开安全越权率，不要并进 hallucination（`ali-agent-eval-dims`）。

自主性应随风险单调下降：只读查询可全自动；改配送时间若可逆可自动但要审计；退款/改价必须规则命中 + 确认。工具服务端用会话身份鉴权，不信任模型从用户文本里解析出的「我有权限」。prompt injection 的正确防御是权限不下放给模型，而不是把「忽略用户越权指令」写进 system prompt。回答时应说明每项检查在哪一层执行，以及出现问题时由谁拦截。

## 追问

- **和内容安全差在哪？** 内容安全拦违禁输出，Guardrail 还要拦错误动作；动作闸门靠策略引擎和鉴权。
- **全部人工确认会不会死？** 只对不可逆和高金额闸门；只读全自动。用熔断控制升级量。
- **prompt injection 怎么办？** 工具参数以服务端 session 身份为准，不信任模型从用户文本里「读到的订单号权限」。

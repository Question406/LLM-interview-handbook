---
id: ali-guardrail
section: agent
order: 28
level: S
title: 如何控制 Agent 自主性边界？Safety Guardrail 怎么设计？
quick: "规则引擎负责强制执行约束，LLM 只负责理解和推理。工具按只读、可逆、不可逆分级，自主性随风险降低，不可逆动作要命中规则并经人工确认；输入、工具权限、执行确认、输出合规和审计分层把关，闸门写在编排和工具服务端。"
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

我会让规则引擎来强制执行约束，LLM 只负责理解和推理，自主性随风险升高而降低。把「不要越权」写进 system 输入提示（prompt）算不上 Guardrail，用户一催，模型就可能「灵活通融」，所以边界必须落在编排层和工具服务端。

举个例子，用户说「帮我把这单直接退了并原路赔付」。Agent 可以填槽、查订单、解释政策，但「发起退款」是不可逆动作，必须命中规则，比如七天无理由、未拆封，并弹出确认；规则不满足就拒绝执行。只读的查物流不需要确认。常见的失败是把赔付金额交给模型「看着办」，或者 prompt 里写了「不要越权」，退款 API 却对任意会话开放。

分层是这样走的：先做输入安全，拦注入和越权指令；再过工具权限矩阵；不可逆动作做执行确认；然后检查输出合规；最后留审计日志。工具分成只读、可逆、不可逆三级：只读查询可以全自动；改配送时间如果可逆，可以自动但要审计；退款、改价必须规则命中加确认。退换货、赔付、改地址这类规则明确、出错就会造成资金损失的场景，优先走规则或工作流，LLM 负责理解和填槽，不负责改规则；开放闲聊、低风险推荐可以给更高的自主性。prompt 可以复述规则，但不能当唯一的闸门。

工具服务端用会话身份鉴权，模型从用户文本里解析出的「我有权限」不算数。防 prompt injection 的办法是不把权限下放给模型，往 system prompt 里加一句「忽略用户越权指令」挡不住它。

周边还有几处要配合。高并发降级时不能把写路径的闸门摘掉（`ali-double11-scale`）。编排层用了开源的自动重试，服务端就必须做幂等，否则确认过的写操作会被重放（`ali-framework-choice`）。强化学习（RL）训练时，如果最终成功里包含「绕过确认」，过程奖励会强化越权，所以权限失败要当硬负例（`ali-agent-final-reward`、`ali-reward-hacking`）。评估时安全越权率要单独报，不并进 hallucination（`ali-agent-eval-dims`）。

面试回答时，我会把每项检查在哪一层执行、出了问题由谁拦下来说清楚。HITL 的细节见 `ali-hitl-risk`，幻觉拦截见 `ali-hallucination-intercept`。

## 追问

**Guardrail 和内容安全有什么区别？**
内容安全拦违禁输出；Guardrail 还要拦错误动作，比如错退、错改地址、越权查单。两者都要审计，动作闸门主要靠策略引擎和工具服务端鉴权。

**全部人工确认，系统会不会被拖死？**
只对不可逆和高金额的动作设确认闸门，只读全自动，再用熔断控制升级量。

**prompt injection 具体怎么防？**
工具参数以服务端 session 身份为准，模型从用户文本里「读到的订单号权限」不作数。

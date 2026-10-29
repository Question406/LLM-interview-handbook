---
id: amazon-guardrails
section: amazon
order: 3
level: A
title: Amazon Bedrock Guardrails：拦截应发生在生成前还是后，和模型对齐的分工？
quick: >-
  输入和输出都要检查：生成前拦越狱、拒答主题、有害内容和输入 PII，生成后查泄密、违规与证据支持。SFT / RLHF
  改变模型行为倾向，Guardrails 执行应用策略，两层需要配合。
tags:
  - Amazon
  - Bedrock
  - Guardrails
  - Safety
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Amazon Bedrock Guardrails
    url: 'https://aws.amazon.com/bedrock/guardrails/'
    type: primary
  - title: Detect and filter harmful content by using Amazon Bedrock Guardrails
    url: 'https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html'
    type: primary
  - title: How Amazon Bedrock Guardrails works
    url: 'https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-how.html'
    type: primary
---

## 可以这样回答

输入和输出都要设检查。生成前能识别的违规请求先拒绝，可以省下推理费用；生成后再检查模型新写出来的有害内容、PII 和缺乏证据的论断。比如用户输入没有身份证号，模型仍可能在回复里编出一个，输入过滤就查不到。

Bedrock 文档的流程是先评估输入，违规时返回预置拒答，不调用基础模型；通过后才生成，再评估输出，必要时拒答或打码。`ApplyGuardrail` 也能单独调用，接到 SageMaker 端点或 Agent 框架里。Seller Support、客服摘要和内部知识库都需要明确谁定政策、谁审计拦截、漏拦时谁 oncall，这对应 Ownership。

## 技术备查

输入和输出都要设检查。生成前能识别的违规请求先拒绝，可以省下推理费用；生成后再检查模型新写出来的有害内容、PII 和缺乏证据的论断。比如用户输入没有身份证号，模型仍可能在回复里编出一个，输入过滤就查不到。

Bedrock 文档的流程是先评估输入，违规时返回预置拒答，不调用基础模型；通过后才生成，再评估输出，必要时拒答或打码。`ApplyGuardrail` 也能单独调用，接到 SageMaker 端点或 Agent 框架里。Seller Support、客服摘要和内部知识库都需要明确谁定政策、谁审计拦截、漏拦时谁 oncall，这对应 Ownership。

## 输入输出分别查什么

输入侧把 source 设为 INPUT，检查有害内容、拒答主题、vocabulary、提示攻击和输入 PII。RAG 还可以在检索前拒绝敏感 query，避免它访问索引。官方支持用标签只评用户段；system、检索块和 few-shot 若一起送内容过滤器，可能误杀正常上下文。

输出侧的 source 是 OUTPUT。模型可能新生成脏话、医疗建议或身份证号。Contextual grounding 要对照检索源和用户问题，看回答是否有证据、是否答非所问；Automated Reasoning 也检查输出。输入阶段还没有答案，做不了这些判断。

六类策略各有用途：内容分类和拒答主题判断类别，vocabulary 做精确匹配，敏感信息结合 PII 概率检测与正则，grounding 对照来源，Automated Reasoning 用形式规则核对事实。精确 vocabulary 拦不住改写后的竞品名，需要主题分类或模型侧配合。

流式输出还要决定何时检查。vocabulary 和 PII 可以边流边打码；完整的 grounding 和 Automated Reasoning 往往要等一段内容或结束。输入同步拦截后，输出可以先流、再校验高风险段，或在结束时检查 grounding，但产品必须说明如何处理校验失败。这会影响 `amazon-p99-stream` 的 TTFT 和尾延迟预算。

费用也随位置变化：输入被拦只收 Guardrail 费用，输出被拦则已发生模型推理和两次评估。因此可以在输入识别的问题尽量提前处理。

## 对齐负责倾向，应用层负责策略

SFT、RLHF 和宪法式反馈通过权重让模型更愿意拒绝有害请求、提供帮助，但换 decoding 温度或越狱措辞，行为仍可能变化。Guardrails 则让 Titan、Claude 和自建模型共用应用规则，不绑定某次 `InvokeModel`。

两层可以分别调整。模型 over-refusal 时，应用可以放宽拒答主题，同时收紧 PII；应用禁止投资建议，也需要显式策略。Automated Reasoning 补的是规则核对能力，不能等同于把 reward model（RM）训到 100 分。评测应拆开漏拦和误拦，见 `amazon-titan-eval`。

检索块是 grounding 的来源。源里有 PII 时输出仍要打码，用户把别人的账号贴进工单则由输入侧处理。过期条款和 PII 泄漏是不同事故，需要不同 acceptance checks，见 `amazon-bedrock-rag`、`amazon-lp-ml`。

```python
def guarded_generate(user, apply_guardrail, generate):
    inn = apply_guardrail(source="INPUT", text=user)
    if inn.intervened:
        return inn.blocked_message
    out = generate(user)
    outg = apply_guardrail(source="OUTPUT", text=out)
    if outg.intervened:
        return outg.blocked_or_masked
    return out
```

这段骨架只表达调用顺序。做 grounding 时还要分别标出 grounding source、query 和 guard content，不能把整段 prompt 当成输出评估。

## 追问

**只检查输出行不行？**
技术上可以，但越狱和必拒主题已经占用了模型与预算，prompt injection 也可能污染检索，应在输入侧先查。

**只检查输入呢？**
不够。生成过程会产生新的有害内容和 PII，hallucination 也要等答案出来后对照来源判断。

**模型做过 RLHF 为什么还需要策略层？**
应用规则需要在换模型、温度和主题后保持一致。跨账号统一策略也需要应用层来管理。

**怎样避免流式检查拖慢体验？**
输入检查计入 TTFT，输出检查按风险决定边流过滤还是等待整段。高风险场景要接受额外 E2E 时间，不能为 TTFT 关闭整段输出检查，见 `amazon-p99-stream`。

---
id: amazon-guardrails
section: amazon
order: 3
level: A
title: Amazon Bedrock Guardrails：拦截应发生在生成前还是后，和模型对齐的分工？
quick: >-
  两边都要。输入侧在调用模型前拦越狱、拒答主题、明显有害和可正则的 PII，省一次推理。输出侧拦幻觉、泄密、模型自己编出来的违规。对齐改的是模型倾向；Guardrails
  是策略层，不替代 RLHF，也别指望模型自己当政策引擎。
tags:
  - Amazon
  - Bedrock
  - Guardrails
  - Safety
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Amazon Bedrock Guardrails
    url: https://aws.amazon.com/bedrock/guardrails/
    type: primary
  - title: Detect and filter harmful content by using Amazon Bedrock Guardrails
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html
    type: primary
  - title: How Amazon Bedrock Guardrails works
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-how.html
    type: primary
---

Bedrock / AGI 应用岗会把安全问成系统题，官方文档写得很直：评估用户输入和模型回复。`ApplyGuardrail` 还可以脱离模型、单独跑。和 Seller Support、客服摘要、内部知识库同一类约束。按 Ownership 收：政策谁拍板、拦了怎么审计、漏拦谁 oncall。

## 生成前拦什么，生成后拦什么

文档里的推理路径是：先评输入；输入违规就返回预置拒答，**不再调用基础模型**；输入过了才生成；再评输出，违规就改成拒答或打码。所以正确答案不是「只在前」或「只在后」。

**生成前（source 为 INPUT）。** 有害内容、拒答主题、词表、提示攻击、输入里的 PII。目的有两个：用户不该把模型当越狱玩具；以及别为注定要拒的请求付钱、占 p99。RAG 里还可以在检索前就拦，避免敏感 query 去打索引。官方也说可以用标签只评用户段，别把 system、检索块、few-shot 一起送进内容过滤器，否则误杀检索上下文。

**生成后（source 为 OUTPUT）。** 模型可能把输入里没有的脏话、医疗建议、身份证号编出来。上下文接地（contextual grounding）和 Automated Reasoning 检查**只对输出有意义**：要对照检索源和用户问题，判断是不是胡编、是不是答非所问。输入阶段没有「答案」可接地。流式更烦：完整接地要等一段或等结束，和 `amazon-p99-stream` 的首 token 预算会打架。工程上常见是输入同步拦、输出先流后校验高风险段，或流结束再做 grounding，用产品文案换尾延迟。

六类策略不要混成一句「安全过滤」：内容分类、拒答主题、词表精确匹配、敏感信息（PII / 正则）、接地检查、Automated Reasoning。词表是精确匹配；PII 是概率检测加正则；接地是对照源。面试要能指出：精确词表拦不掉改写后的竞品名，得靠主题分类或模型侧。

收费也暴露分工：输入被拦，只收 Guardrail，不收模型推理；输出被拦，模型和两次评估都收。所以「能在输入拦的不要拖到输出」既是安全也是成本。

## 和对齐怎么切

对齐（SFT / RLHF / 宪法式反馈）改的是权重：模型更倾向拒有害、更倾向有帮助。它是概率的，换一个解码温度、换一句越狱，行为会漂。Guardrails 是应用策略：同一套规则可挂 Titan、Claude、自建模型，官方卖点就是跨模型一致。`ApplyGuardrail` 可以在 SageMaker 端点、Agent 框架里用，不绑定某次 `InvokeModel`。

不要答「有了 Guardrails 就不用对齐」或「对齐好了就不用拦」。模型拒答会过度，政策层可以放宽拒答主题但收紧 PII；反过来，对齐没有把「本应用禁止投资建议」写进梯度里。Automated Reasoning 用形式规则核对事实，这是策略层补幻觉，不是把 RM 训到 100 分。评测见 `amazon-titan-eval`：漏拦 / 误拦要拆开报，不能只报有害分类准确率。

和 `amazon-bedrock-rag` 叠：检索块是 grounding 的源，不是可以乱回的上下文。源里若已有 PII，输出过滤器要打码；输入过滤器拦的是用户把别人的账号贴进工单。Seller 场景漏一条过期条款是事故，漏一条 PII 也是事故，门禁不同，见 `amazon-lp-ml`。

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

这是骨架。接地还要把 grounding source、query、guard content 三段标上，别把整段 prompt 当输出评。

## 追问

- **只拦输出行不行？** 行但不该。越狱和拒答主题会先占满模型，账单和 GPU 白烧；提示注入也可能污染检索。输入拦是第一道。
- **只拦输入行不行？** 不行。有害和 PII 可以在补全里新出现；幻觉只能对照源在输出查。
- **模型已经 RLHF 过了为什么还要 Guardrails？** 对齐是倾向，政策是合同。换模型、换温度、换应用主题，合同还在。跨账号统一策略也只能放在 Guardrails 这一层。
- **流式输出怎么拦？** 词表和 PII 可以边流边打码；接地和 Automated Reasoning 往往要等一段或等结束。别为了 TTFT 把输出侧整段关掉，见 `amazon-p99-stream`。

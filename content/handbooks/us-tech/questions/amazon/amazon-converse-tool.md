---
id: amazon-converse-tool
section: amazon
order: 16
level: A
title: Amazon：Converse tool use，toolConfig、并行工具和 Guardrail 怎么接？
quick: "你自建循环：toolConfig 给出 schema，模型回 toolUse，你跑完再回 toolResult。一次可以多块并行，只读才并行，写要幂等。Guardrail 默认不评工具定义、参数和结果，别以为开了护栏 JSON 就安全。和托管 Agents 的差别是编排所有权在你。"
tags:
  - Amazon
  - Bedrock
  - Tool Use
  - Guardrails
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Use a tool to complete an Amazon Bedrock model response
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html
    type: primary
  - title: Use a guardrail with the Converse API
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-use-converse-api.html
    type: primary
  - title: Converse API
    url: https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html
    type: primary
  - title: Detect and filter harmful content with Amazon Bedrock Guardrails
    url: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html
    type: primary
---

Bedrock 应用岗把 function calling 问成 Converse，而不是「你会不会 ReAct」。公开文档：client-side 模式下模型 **不执行** 工具；你在 `toolConfig` 里给 `toolSpec`（名、描述、JSON Schema），响应里 `stopReason` 为 `tool_use`，content 里一块或多块 `toolUse`。你执行后用同一 `toolUseId` 回 `toolResult`。托管循环见 `amazon-bedrock-agents`。

## 调用约定：schema、并行和停止

`toolChoice` 可以 auto / any / 指定某个工具。`auto` 不等于安全：把退款和搜政策放同一列表，是在请误调。根 schema 要是 object，必填写清。

并行：一轮多个 `toolUse` 时，必须一次带回全部 `toolResult`，缺一块对话非法。只读（查库存、查条款）可并行；有依赖（先查订单再退款）要串。写操作默认不自动重试，除非幂等键。模型并行点两次 `create_ticket` 没有幂等就是两张单。

```python
def handle_tool_use(msg, run_tool):
    uses = [b["toolUse"] for b in msg["content"] if "toolUse" in b]
    results = []
    for u in uses:
        try:
            out = run_tool(u["name"], u["input"])
            results.append({"toolResult": {"toolUseId": u["toolUseId"], "content": [{"text": out}]}})
        except Exception as e:
            results.append({
                "toolResult": {
                    "toolUseId": u["toolUseId"],
                    "status": "error",
                    "content": [{"text": str(e)}],
                }
            })
    return {"role": "user", "content": results}
```

失败不要丢。文档建议 `status: error` 让模型改参或问人，而不是你在客户端吞掉再让它幻觉「已经办了」。步数、实际耗时、总 token 用量都要设硬上限，见 `amazon-p99-stream`。

## Guardrail 盖不住工具 JSON

官方 Converse + Guardrails 表写得很直：评用户 / 系统 / 模型文本；**不评** `toolConfig` 定义、模型生成的 `toolUse.input`、你回的 `toolResult`。早期还有「工具和护栏不能同开」的报错；现在即使同开，政策层仍有洞。

所以面试要主动加应用层：

- 工具名允许名单、参数校验（金额上限、marketplace）。
- 不可逆动作 return control 或人工确认，不要因为 Guardrail 过了就打生产 Lambda。
- `toolResult` 当不可信输入截断，防检索块 / 网页注入，见 `amazon-guardrails`、`amazon-bedrock-rag`。
- 流式时完整参数没闭合不能执行。首个 token 的等待时间（TTFT） 好看执行不了，E2E 才是工具 SLO。

评测：选对工具、参数合法、误调、写操作重复、工具失败后的幻觉率。不要报「对话像客服」。换 Nova 档位契约不动，见 `amazon-nova`。

常见误区是：把 OpenAPI 一贴当 IAM；并行写库；以为 Contextual grounding 会检查 tool JSON。

## 追问

- **和 Agents 怎么选？** 工具少、要 trace、能接受托管编排 → Agents / AgentCore。要事务、补偿、精细重试 → Converse 自建。混合很常见。
- **toolChoice 指定工具就安全吗？** 只保证会调，不保证参数对、用户同意。
- **并行和 p99？** 并行只读能降实际耗时；尾部往往是最慢那个工具。按最慢依赖报，不要报平均值。
- **为什么 Guardrail 不评 toolResult？** 结果可能很长、结构化、含业务 PII 策略不同。所有权在应用，Bar Raiser 要听这句话。

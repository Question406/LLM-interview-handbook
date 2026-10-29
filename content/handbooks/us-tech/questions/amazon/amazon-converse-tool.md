---
id: amazon-converse-tool
section: amazon
order: 16
level: A
title: Amazon：Converse tool use，toolConfig、并行工具和 Guardrail 怎么接？
quick: >-
  Converse 的工具循环由应用执行：toolConfig 描述接口，模型返回 toolUse，应用执行后按 toolUseId 回传
  toolResult。无依赖的只读工具可以并行，写操作要处理幂等和确认；Guardrail 不覆盖工具定义、参数和结果，这些还得应用检查。
tags:
  - Amazon
  - Bedrock
  - Tool Use
  - Guardrails
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23T00:00:00.000Z
sources:
  - title: Use a tool to complete an Amazon Bedrock model response
    url: 'https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html'
    type: primary
  - title: Use a guardrail with the Converse API
    url: >-
      https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-use-converse-api.html
    type: primary
  - title: Converse API
    url: >-
      https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html
    type: primary
  - title: Detect and filter harmful content with Amazon Bedrock Guardrails
    url: 'https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html'
    type: primary
---

Converse 的 client-side tool use 由应用负责执行循环，模型只提出调用请求。比如查库存和查政策可以并行，先查订单再退款则有依赖，要串行。应用在 `toolConfig` 中给出 `toolSpec` 的名称、描述和 JSON Schema；响应 `stopReason` 为 `tool_use` 时，执行 content 里的 `toolUse`，再用同一个 `toolUseId` 回传 `toolResult`。

## 调用怎样执行，失败怎样返回

`toolChoice` 可以是 `auto`、any 或指定工具；它决定选工具的方式，不保证权限和参数正确。退款与搜政策放在同一列表时，要额外检查误调。根 schema 设为 object，并写清必填项。

一轮有多个 `toolUse`，就要一次带回全部 `toolResult`，漏一个会导致对话非法。只读且无依赖的请求可以并行。写操作只有具备 idempotency key 时才自动重试；否则两次 `create_ticket` 就可能建出两张单。

```python
def handle_tool_use(msg, run_tool):
    uses = [b["toolUse"] for b in msg["content"] if "toolUse" in b]
    results = []
    for u in uses:
        try:
            out = run_tool(u["name"], u["input"])
            results.append(
                {
                    "toolResult": {
                        "toolUseId": u["toolUseId"],
                        "content": [{"text": out}],
                    }
                }
            )
        except Exception as e:
            results.append(
                {
                    "toolResult": {
                        "toolUseId": u["toolUseId"],
                        "status": "error",
                        "content": [{"text": str(e)}],
                    }
                }
            )
    return {"role": "user", "content": results}
```

失败也要回传。用 `status: error` 让模型看到错误，再改参或向用户澄清；客户端吞掉错误，模型就可能声称已经完成。循环还要给步数、实际耗时和总 token 用量设硬上限。

## 工具参数和结果还要应用检查

原文所引 Converse + Guardrails 表说明，它检查用户、系统和模型文本，不检查 `toolConfig` 定义、模型生成的 `toolUse.input` 或回传的 `toolResult`。早期还有工具和护栏不能同开的报错；即使两者可以同时开，也需要应用实现这些 safeguards。

所以应用层还要做这些检查：

- 工具名允许名单、参数校验（金额上限、marketplace）。
- 不可逆动作 return control 或人工确认，不要因为 Guardrail 过了就打生产 Lambda。
- `toolResult` 当不可信输入截断，防检索块 / 网页注入，见 `amazon-guardrails`、`amazon-bedrock-rag`。
- 流式时完整参数没闭合不能执行。首个 token 的等待时间（TTFT） 好看执行不了，E2E 才是工具 SLO。

评测看工具选择、参数合法性、误调、写操作重复，以及工具失败后声称成功的比例。换 Nova 档位时，这些契约仍然固定。

OpenAPI 不能替代 IAM，Contextual grounding 也不检查 tool JSON；写库并行执行前仍要处理依赖和幂等。

相关：`amazon-bedrock-agents`、`amazon-p99-stream`、`amazon-nova`。

## 追问

**和 Agents 怎么选？**
工具少、要 trace、能接受托管编排 → Agents / AgentCore。要事务、补偿、精细重试 → Converse 自建。混合很常见。
**toolChoice 指定工具就安全吗？**
只保证会调，不保证参数对、用户同意。
**并行和 p99？**
并行只读能降实际耗时；尾部往往是最慢那个工具。按最慢依赖报，不要报平均值。
**为什么 Guardrail 不评 toolResult？**
结果可能很长、结构化、含业务 PII 策略不同。所有权在应用，Bar Raiser 要听这句话。

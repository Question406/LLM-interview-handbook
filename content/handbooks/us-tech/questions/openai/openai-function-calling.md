---
id: openai-function-calling
section: openai
order: 20
level: A
title: OpenAI：tool / function calling 的 schema、失败、并行，和 JSON mode 差在哪
quick: >-
  Schema 是宿主合同，模型只提议调用。JSON mode 只保证 content 是合法 JSON 对象，不路由、不校验字段。Function
  calling 走 `tool_calls`；Structured Outputs 再用约束解码把参数钉在 schema 上。并行只适用于无依赖的多调用；失败要回传错误而不是让模型直接碰凭证。
tags:
  - OpenAI
  - Function calling
  - Tools
  - JSON mode
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Function calling and other API updates
    url: https://openai.com/index/function-calling-and-other-api-updates/
    type: primary
  - title: Function calling
    url: https://platform.openai.com/docs/guides/function-calling
    type: primary
  - title: Introducing Structured Outputs in the API
    url: https://openai.com/index/introducing-structured-outputs-in-the-api/
    type: primary
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
---

## 题怎么来的

2023 年 OpenAI 把 function calling 做成 Chat Completions 的一等能力，后来补了并行调用和 Structured Outputs。LLM 团队问这题，不是让你背 API 字段名，是看你是否把 **模型当不可信的调用方**。产品设计对照见 `design-chat-tools`；Anthropic 把同一件事叫 tool use，见 `anthropic-tool-use`。我会按 OpenAI 的三条通道答：JSON mode、function calling、带 schema 的约束解码。

## 三条通道不要并成一句「会输出 JSON」

**JSON mode**（`response_format` 为 json object）：模型在 **助手 content** 里吐一个能 `json.loads` 的对象。文档写明 prompt 里还得要求 JSON，否则可能空转。它不选工具、不保证有哪些键、不保证类型。适合「抽字段进对象」。不适合「去查天气」。

**Function calling：** 你提供一组工具，每项有 `name`、`description`、`parameters`（JSON Schema）。模型若要行动，返回的是 `tool_calls`：名字加 **参数字符串**，不是最终用户可见的答案。宿主解析、校验、执行，再把工具结果贴回对话。`tool_choice` 可以放权（auto）、强迫用工具、或钉死某一个。这是路由，不只是语法。

**Structured Outputs：** 在 json schema 或 `strict` 工具上做约束解码，合法前缀才允许下一步 token。它消灭「参数不是 JSON / 少字段」这一类，**消灭不了**「字段合法但用户 id 是别人的」。政策检查仍在宿主。

Schema 要让错误形状难出现：枚举代替自由字符串、数字带范围、副作用工具把「预览」和「提交」拆开。一个自由字符串命令字段等于把 shell 交给模型。描述里写何时 **不要** 调，和相近工具的差别；模型是靠 docstring 做 ACI，不是靠你心里想的语义。

## 并行、失败、循环

并行调用：同一助手步里多个 `tool_calls`，适用于互相不依赖的读，比如三个城市的天气。第二个调用需要第一个的返回值时，不能并行，要走「调一次 → 结果进上下文 → 再调」。API 上的并行开关管的是「允许模型一次提议多个」，不是自动拆依赖图。依赖拆错的签名是：第二个工具吃到空 id 或幻觉 id。

失败分三类，回传方式不同：

1. **解析 / schema 失败。** 参数不是对象、缺必填、类型错。没上约束解码时很常见。把校验错误当工具结果贴回去，让模型改，不要自己猜着补字段。
2. **工具执行失败。** 超时、404、权限。用错误标记加可读原因。只读工具可有限次重试；扣款、发邮、删数据默认不重试，要幂等键。
3. **模型不该调却调 / 该调不调。** 这是策略，不是 JSON 坏了。用 eval：该调的黄金工具名、不该调的拒答集。别拿 MMLU 代替，指令遵循见 `openai-if-eval`。

循环：最大步数、重复同一调用的熔断、以及「已经有结果还在调」。没有步数上限的 agent 会在 5xx 上烧完预算。凭证、内网 URL、文件系统根目录不进工具参数空间，模型连提议都应当被宿主拦下。

```python
def dispatch(call, registry, policy):
    fn = registry.get(call.name)          # 白名单，禁止幻觉工具名
    if fn is None:
        return error("unknown_tool", call.name)
    args = parse_json(call.arguments)     # 失败则回传，不要 eval 字符串
    schema_check(args, fn.schema)
    policy_check(args, policy)            # 资源所有权、副作用
    return fn(args)
```

和 JSON mode 的一句话对照：JSON mode 是 **content 语法**；function calling 是 **侧信道上的行动提议**；strict schema 是 **解码器帮你做类型检查**。三者可以叠，但叠完仍要把执行权留在自己手里。

## 追问

- **为什么参数当初是字符串？** 早期生成不一定是合法 JSON，字符串让 API 能先把 token 收回来再 parse。strict 之后可以当对象看，宿主仍要 parse 失败分支。
- **强迫 `tool_choice` 某函数？** 抽取型任务可以。对话助手用 auto，否则模型不能直接用自然语言收尾。
- **并行会打乱顺序吗？** 执行可并发，写回对话时要带 tool call id 对齐，不要按结束时间乱序张冠李戴。
- **和 JSON mode 能互替吗？** 抽结构用 JSON mode 或 json schema；要执行副作用必须走工具加宿主。

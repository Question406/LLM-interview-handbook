---
id: openai-function-calling
section: openai
order: 20
level: A
title: OpenAI：tool / function calling 的 schema、失败、并行，和 JSON mode 差在哪
quick: "JSON mode 约束输出是 JSON，function calling 让模型提议工具名与参数，执行仍由宿主负责。Structured Outputs 可约束 schema，但资源权限和副作用还要校验；多个调用只有在互不依赖时才适合并行。"
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

我会先说清输出格式与执行权限的边界：模型可以提议调用，宿主解析、校验后才执行。比如查三个城市的天气可以并行；第二个工具要用第一个返回的 id，就必须等结果进上下文再调，否则容易用到空 id 或编造的 id。

OpenAI 2023 年把 function calling 加进 Chat Completions，后来增加并行和 Structured Outputs。这三类能力分别控制输出语法、行动路由和参数形状，设计时需要分开讲。

## 先确认返回内容代表什么

JSON mode（`response_format` 为 json object）：模型在助手 content 里吐一个能 `json.loads` 的对象。文档写明 输入提示里还得要求 JSON，否则可能空转。它不选工具、不保证有哪些键、不保证类型。适合「抽字段进对象」。不适合「去查天气」。

Function calling：你提供一组工具，每项有 `name`、`description`、`parameters`（JSON Schema）。模型若要行动，返回的是 `tool_calls`：名字加参数字符串，不是最终用户可见的答案。宿主解析、校验、执行，再把工具结果贴回对话。`tool_choice` 可以放权（auto）、强迫用工具、或明确固定下来某一个。这是路由，不只是语法。

Structured Outputs：在 json schema 或 `strict` 工具上做约束解码，只允许生成能延续合法前缀的 token。它消灭「参数不是 JSON / 少字段」这一类，消灭不了「字段合法但用户 id 是别人的」。政策检查仍在宿主。

Schema 要让错误形状难出现：枚举代替自由字符串、数字带范围、副作用工具把「预览」和「提交」拆开。一个自由字符串命令字段等于把 shell 交给模型。描述里写何时不要调，和相近工具的差别；模型通过工具说明理解如何调用工具接口（ACI），不是靠你心里想的语义。

## 再处理执行和恢复

API 的并行开关只允许模型在同一步提议多个 `tool_calls`，依赖图仍由系统处理。解析失败、缺字段或类型错时，把校验错误作为工具结果回填，让模型修改，宿主不要猜着补参数。

超时、404、权限等执行失败，回传错误标记和可读原因。只读工具可以有限重试，扣款、发邮件、删数据这类副作用默认不重试，先做幂等键。JSON 合法但工具选错、该调未调，属于策略错误：要用黄金工具名和不该调用的拒答集评测，MMLU 测不到这些。

循环还要有最大步数、重复调用熔断，以及已有结果仍继续调用的检查，避免在 5xx 上耗完预算。凭证、内网 URL、文件系统根目录排除在可提议的参数范围外，由宿主拦截。下面的顺序就是先白名单、再解析、schema 和 policy，最后执行。

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

这几层可以一起使用，执行前的资源所有权和副作用检查仍留在宿主。

相关：`design-chat-tools`、`anthropic-tool-use`、`openai-if-eval`

## 追问

**为什么参数当初是字符串？**
早期生成不一定是合法 JSON，字符串让 API 能先把 token 收回来再 parse。strict 之后可以当对象看，宿主仍要 parse 失败分支。
**强迫 `tool_choice` 某函数？**
抽取型任务可以。对话助手用 auto，否则模型不能直接用自然语言收尾。
**并行会打乱顺序吗？**
执行可并发，写回对话时要带 工具调用 id 对齐，不要按结束时间乱序张冠李戴。
**和 JSON mode 能互替吗？**
抽结构用 JSON mode 或 json schema；要执行副作用必须走工具加宿主。

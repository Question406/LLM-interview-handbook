---
id: anthropic-json-schema
section: anthropic
order: 18
level: A
title: Anthropic：structured output 约束解码和事后再解析，各挡哪类错误？
quick: >-
  约束解码把 schema 编成文法，非法 token 抽不出来，JSON 不会烂。它不保证数字落在业务区间、URL
  不越权、枚举语义对。范围、PII、授权仍要宿主再校验。Prompt 里求「只输出 JSON」然后正则捞，是在赌采样。
tags:
  - Anthropic
  - Structured output
  - JSON Schema
  - Decoding
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Structured outputs (Claude Docs)
    url: https://platform.claude.com/docs/en/build-with-claude/structured-outputs
    type: primary
  - title: Strict tool use (Claude Docs)
    url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use
    type: primary
---

应用岗会把「Claude 偶发把 JSON 包进代码围栏」问到解码层。官方 structured outputs 有两条：整段回答走 `output_config.format` 的 `json_schema`；工具参数走 `strict: true`。两者都是文法约束采样，不是再跑一次评委模型。题不是某一场 OA，是你能不能把「形状正确」和「语义正确」拆开。

## 约束解码保证的是形状

Schema 编译成文法。每一步合法续写集合被 mask 掉，模型抽不到会破坏括号、类型、`required` 的 token。于是 `json.loads` 和缺字段这一类循环可以去掉。对象必须 `additionalProperties: false`，否则文法不知道能不能多键。首次用某 schema 要编译，有一截 TTFT；编译结果大约缓存一天，改结构或工具集才失效。改 `description` 通常不使文法失效。

官方子集：基本类型、`enum` / `const`、有限的 `anyOf`、内部 `$ref`。**不吃**：递归 schema、`minimum` / `maximum`、`minLength`、复杂正则（反向引用、lookahead）。SDK 常把这些约束删掉写进 description——模型可能遵守，文法不强制。

它**不**保证：数字在业务范围里；字符串是合法订单号；路径不指向系统目录；枚举选了合法值但是用错工具。`anthropic-tool-use` 里写过：schema 过了还要政策检查。constraining ≠ validating 产品不变量。

## 再解析挡什么、什么时候还需要

旧路径：prompt 要求 JSON → 从围栏里切片 → `json.loads` 失败就 `is_error` 重试。它挡的是「模型爱说人话」。代价是尾延迟、重试烧输出 token、错误提示本身又占窗口。约束解码把这层几乎删掉。

仍要宿主校验：

- Schema 表达不了的：金额 $a + b = c$、互斥字段、时区。
- SDK 删掉的数值 / 长度约束。
- 下游强类型服务要的是你自己的 Pydantic / Zod 键名，不是模型自说自话的字段。

Agent 循环里用 strict tool；抽取 / 分类 / 要落库的最终回答用 JSON outputs。不要两个同时当同一层合同：工具参数进执行器，面向用户的 JSON 进产品。Computer use 那类服务端工具集文档写明不接受 `strict: true`，见 `anthropic-computer-use`。约束解码还会在请求里注入一小段格式说明，输入 token 会略增；这和「prompt 里求 JSON」不是同一层，后者没有 mask。

```python
# 文法保证能 loads；区间仍要自己查
data = json.loads(block.text)
if not (0 <= data["score"] <= 1):
    raise ValueError("score out of range")
```

## 和 XML 提示、MCP、缓存的分工

给模型看的长资料用 `anthropic-xml-prompt` 的标签边界；给运行时执行的用 JSON Schema。MCP server 的 `inputSchema` 仍是 JSON Schema，但远程 server 必须自己再校验一遍，不能信 client 已经约束过，见 `anthropic-mcp`。换 `output_config.format` 会让对话前缀失效，打爆 `anthropic-prompt-cache`。

错法：schema 写成自由字符串 `cmd`；打开 `additionalProperties`；把约束解码当越权防护。

文法第一次编译会加一截 TTFT，之后大约缓存一天。评测延迟时要把冷编译和热请求分开报。数值区间、字符串长度这类官方文法不吃的约束，写进 description 只是提示，宿主校验才是合同。

## 追问

- **文法会不会逼模型胡填 required 字段？** 会。宁可用可选字段 + 宿主默认，也不要把「必须有 URL」写进 schema 却没有合法值。
- **和 tool_choice 强制调用？** `tool_choice` 决定调不调；`strict` 决定参数合不合文法。强制调用加宽 schema，等于强迫执行一次可能无意义的副作用。
- **流式怎么 parse？** 约束下前缀始终是合法 JSON 前缀，可以边收边喂增量解析器。不要等闭合再正则。
- **失败了还要不要重试？** 语法失败应接近 0。语义失败回传具体校验错误，最多两三次，和非幂等工具的重试政策一致。

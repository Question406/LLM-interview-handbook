---
id: anthropic-json-schema
section: anthropic
order: 18
level: A
title: Anthropic：structured output 约束 decoding 和事后再解析，各挡哪类错误？
quick: >-
  约束 decoding 把 schema 编成文法，每一步屏蔽非法 token，保证 JSON
  结构合法；它解决不了金额范围、PII、授权和枚举语义。我的做法是用 strict tool 约束工具参数、用 JSON outputs
  约束最终回答，再由宿主校验业务条件。
tags:
  - Anthropic
  - Structured output
  - JSON Schema
  - Decoding
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Structured outputs (Claude Docs)
    url: 'https://platform.claude.com/docs/en/build-with-claude/structured-outputs'
    type: primary
  - title: Strict tool use (Claude Docs)
    url: >-
      https://platform.claude.com/docs/en/agents-and-tools/tool-use/strict-tool-use
    type: primary
---

## 可以这样回答

我会用约束 decoding 保证结构，再由宿主程序检查业务语义。例如金额字段可以是合法数字，却仍超出允许区间。官方 structured outputs 中，最终回答用 `output_config.format` 的 `json_schema`，工具参数用 `strict: true`；两条路径都在 sampling 时施加文法约束。

Schema 编译成文法。每一步不合法的续写候选被 mask 掉，模型抽不到会破坏括号、类型、`required` 的 token。于是 `json.loads` 和缺字段这一类循环可以去掉。对象必须 `additionalProperties: false`，否则文法不知道能不能多键。首次使用某个 schema 时需要编译，会增加TTFT；编译结果大约缓存一天，改结构或工具集才失效。改 `description` 通常不使文法失效。

## 技术备查

我会用约束 decoding 保证结构，再由宿主程序检查业务语义。例如金额字段可以是合法数字，却仍超出允许区间。官方 structured outputs 中，最终回答用 `output_config.format` 的 `json_schema`，工具参数用 `strict: true`；两条路径都在 sampling 时施加文法约束。

## 结构在哪一步得到保证

Schema 编译成文法。每一步不合法的续写候选被 mask 掉，模型抽不到会破坏括号、类型、`required` 的 token。于是 `json.loads` 和缺字段这一类循环可以去掉。对象必须 `additionalProperties: false`，否则文法不知道能不能多键。首次使用某个 schema 时需要编译，会增加首个 token 的等待时间（TTFT）；编译结果大约缓存一天，改结构或工具集才失效。改 `description` 通常不使文法失效。

官方子集：基本类型、`enum` / `const`、有限的 `anyOf`、内部 `$ref`。不吃：递归 schema、`minimum` / `maximum`、`minLength`、复杂正则（反向引用、lookahead）。SDK 常把这些约束删掉写进 description——模型可能遵守，文法不强制。

它不保证：数字在业务范围里；字符串是合法订单号；路径不指向系统目录；枚举选了合法值但是用错工具。`anthropic-tool-use` 里写过：schema 过了还要政策检查。约束输出格式不等于校验产品必须满足的业务条件。

## 宿主还要检查什么

旧路径是在 prompt 里要求 JSON，收到回复后从围栏中切片，再用 `json.loads` 解析，失败就通过 `is_error` 重试。这能补救模型夹带说明文字的问题，但重试会增加尾延迟、输出 token 和错误提示占用的窗口。约束 decoding 可以省去这类语法补救的大部分工作。

仍要宿主校验：

- Schema 表达不了的：金额 $a + b = c$、互斥字段、时区。
- SDK 删掉的数值 / 长度约束。
- 下游强类型服务要的是你自己的 Pydantic / Zod 键名，不是模型自说自话的字段。

Agent 循环里用 strict tool；抽取 / 分类 / 要落库的最终回答用 JSON outputs。不要两个同时当同一层合同：工具参数进执行器，面向用户的 JSON 进产品。Computer use 那类服务端工具集文档写明不接受 `strict: true`，见 `anthropic-computer-use`。约束 decoding 还会在请求里注入一小段格式说明，输入 token 会略增；这和「prompt 里求 JSON」不是同一层，后者没有 mask。

```python
# 文法保证能 loads；区间仍要自己查
data = json.loads(block.text)
if not (0 <= data["score"] <= 1):
    raise ValueError("score out of range")
```

给模型看的长资料用 `anthropic-xml-prompt` 的 label boundaries；给运行时执行的用 JSON Schema。MCP server 的 `inputSchema` 仍是 JSON Schema，但远程 server 必须自己再校验一遍，不能信 client 已经约束过，见 `anthropic-mcp`。换 `output_config.format` 会让对话前缀失效，降低 `anthropic-prompt-cache` 的命中率。

常见误区是：schema 写成自由字符串 `cmd`；打开 `additionalProperties`；把约束 decoding 当越权防护。评测延迟时要把冷编译和热请求分开报。数值区间、字符串长度写进 description 只是提示，这些条件仍要由宿主程序校验。

## 追问

**文法会不会逼模型胡填 required 字段？**
会。宁可用可选字段 + 宿主默认，也不要把「必须有 URL」写进 schema 却没有合法值。

**和 tool_choice 强制调用？**
`tool_choice` 决定调不调；`strict` 决定参数合不合文法。强制调用加宽 schema，等于强迫执行一次可能无意义的副作用。

**流式怎么 parse？**
约束下前缀始终是合法 JSON 前缀，可以边收边喂增量解析器。不要等闭合再正则。

**失败了还要不要重试？**
语法失败应接近 0。语义失败回传具体校验错误，最多两三次，和非幂等工具的重试政策一致。

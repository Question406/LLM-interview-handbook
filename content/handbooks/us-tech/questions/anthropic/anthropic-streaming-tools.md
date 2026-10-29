---
id: anthropic-streaming-tools
section: anthropic
order: 32
level: A
title: Anthropic：流式 tool 调用怎么处理 partial JSON、用户取消和幂等？
quick: >-
  我会按块累积 partial_json，等块结束、JSON
  合法且校验通过后再执行一次。默认模式按完整字段缓冲，细粒度模式可能收到非法半截参数；用户取消就丢弃未执行调用，已发出的写入靠 idempotency key
  确认状态，不能把取消当成回滚。
tags:
  - Anthropic
  - Streaming
  - Tool use
  - Serving
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Streaming Messages (Claude Docs)
    url: 'https://platform.claude.com/docs/en/build-with-claude/streaming'
    type: primary
  - title: Fine-grained tool streaming (Claude Docs)
    url: >-
      https://platform.claude.com/docs/en/agents-and-tools/tool-use/fine-grained-tool-streaming
    type: primary
  - title: Tool use overview (Claude Docs)
    url: 'https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview'
    type: primary
---

## 可以这样回答

我会把流式预览和工具执行分开：参数可以边收边展示，执行要等整个块结束、JSON 合法并完成校验。比如收到半截转账参数就取消，宿主不能据此转账。官方 SSE 的 `content_block_start` 中 `tool_use.input` 是空对象，真正参数来自 `input_json_delta` 的 `partial_json` 碎片，循环如何执行见 `anthropic-tool-use`。

默认（缓冲）：服务端攒完一个完整的键值再发出碎片。当前模型常常一次只发完一对 key-value，所以工具流里会有停顿。你仍应把碎片拼成字符串，在 `content_block_stop` 时 `json.loads`。最终 `tool_use.input` 是对象；中间 delta 是字符串。

## 技术备查

我会把流式预览和工具执行分开：参数可以边收边展示，执行要等整个块结束、JSON 合法并完成校验。比如收到半截转账参数就取消，宿主不能据此转账。官方 SSE 的 `content_block_start` 中 `tool_use.input` 是空对象，真正参数来自 `input_json_delta` 的 `partial_json` 碎片，循环如何执行见 `anthropic-tool-use`。

## 先把参数完整收齐

默认（缓冲）：服务端攒完一个完整的键值再发出碎片。当前模型常常一次只发完一对 key-value，所以工具流里会有停顿。你仍应把碎片拼成字符串，在 `content_block_stop` 时 `json.loads`。最终 `tool_use.input` 是对象；中间 delta 是字符串。

细粒度（`eager_input_streaming` 或旧 beta 头 `fine-grained-tool-streaming-2025-05-14`）：不缓冲、不校验，大字段（代码、长文档）的首字节来得早，UI 可以边收边渲染。代价是累积串可能非法，`max_tokens` 截在参数中间时尤其如此。官方要求你自己 guard parse，非法则当错误回传，不要执行。

```python
buf = ""


def on_event(ev):
    global buf
    if ev.type == "content_block_start" and ev.content_block.type == "tool_use":
        buf = ""
        pending[ev.index] = ev.content_block  # id、name 此时已有；input 是 {}
    elif ev.type == "content_block_delta" and ev.delta.type == "input_json_delta":
        buf += ev.delta.partial_json
        ui.preview(try_parse_prefix(buf))  # 只预览，不执行
    elif ev.type == "content_block_stop":
        try:
            args = json.loads(buf)
        except json.JSONDecodeError:
            return error_result("incomplete json")
        dispatch(pending[ev.index], args)  # 唯一执行点
```

`stop_reason` 在 `message_delta` 才出现。`tool_use` 表示该停下来执行工具；`max_tokens` 表示生成被切段，工具 JSON 可能半截。不要用 `message_start` 里的 `stop_reason: null` 当完成。

约束 decoding 的 structured output（`anthropic-json-schema`）前缀更接近合法 JSON 前缀，可以喂增量解析器。细粒度工具流没有这个保证。Computer use 那类服务端工具集文档写过不接受 `strict: true`，更不能假设碎片合法。

## 取消后如何保留执行状态

用户点停止 = 客户端拆掉 HTTP / SSE。你可能已经收到 `content_block_start`（有 `tool_use_id` 和 name）和若干 `partial_json`，但没有 `content_block_stop`，也没有最终 `stop_reason`。这时未执行的副作用调用直接放弃，半截 `{"to": "alice", "amount": 1` 不能发起转账。已经发出的只读请求可以丢弃结果，比如天气预览作废；已经发出的写入则要靠 idempotency key 查明状态，取消 HTTP 不能保证对端没有收到，也不能靠再发一次反向操作来补救。

下一轮不要假装工具已跑完。要么不贴 `tool_result`（等于这轮作废，从用户新消息开始），要么贴 `is_error`：「aborted by user」。缺 `tool_result` 却保留 `tool_use` 块，API 会拒。

取消要能打断正在跑的宿主工具，不只是停 逐 token 生成（decode）。工具进程设超时和取消令牌，见生产 tool 的超时讨论。占着 decode slot 空等下游，会和 `anthropic-rate-limit` 打架。

`tool_use_id` 在 `content_block_start` 就分配。宿主应立刻登记 `(user_id, conversation_id, tool_use_id)`，但执行放在合法 JSON 齐了之后。网络重试、用户连点、模型说「再试一次」，必须落到同一键。

读工具可以重试。写工具默认不自动重试，除非工具声明幂等并接受你的键。付款、发信、删文件没有键就禁止「流断了再放一遍」。键不要只用参数哈希：同一金额改收款人必须是新键。取消后重试，若第一次其实已经成功，第二次要命中同一执行并返回第一次的收据，而不是再转一笔。

和 `anthropic-tool-roundtrip` 衔接：执行完的结果仍要截断、仍不能破坏 cache 前缀。流式预览可以暂时不完整；落库的 `tool_result` 必须是你校验过的最终对象。

常见误区是：每来一个 delta 就 `eval`；`max_tokens` 切断后用正则补全 JSON 然后下单；取消后对非幂等工具自动重放；用模型散文里的「已取消」当执行层状态。

## 追问

**细粒度一定更快吗？**
大参数的首字节更快。小参数、且你必须等合法 JSON 才能动副作用，体感差不多，还多一类非法 JSON。

**并行多个 tool_use 怎么流？**
按 `index` 分组统计拼串。一批里有敏感动作，确认打在每一块执行前，见 `anthropic-computer-use`。

**thinking 块和 tool 块一起流？**
`anthropic-extended-thinking` 的 thinking 配置编进缓存前缀，不要和工具流的 delta 搞混。用户取消时 thinking 半截可以丢，工具副作用不能半截执行。

**partial JSON 能当 ACI 吗？**
不能。ACI 是完整 字段和类型规范（schema） 校验之后的合同。预览只服务 UI。

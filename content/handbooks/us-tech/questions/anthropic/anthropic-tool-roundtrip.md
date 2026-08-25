---
id: anthropic-tool-roundtrip
section: anthropic
order: 30
level: A
title: Anthropic：tool 往返结果过大、截断、cache 前缀被破坏，怎么处理？
quick: >-
  工具结果是下一轮前缀的一部分。过大要截断并标明截断，不要 silently 丢尾巴。截断长度、错误包装、时间戳只要抖一下，prompt cache 从那一块起全 miss。静态的是 tools 和 system，结果当可变后缀。
tags:
  - Anthropic
  - Tool use
  - Prompt caching
  - Serving
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Prompt caching (Claude Docs)
    url: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
    type: primary
  - title: Tool use overview (Claude Docs)
    url: https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
    type: primary
  - title: Building effective agents
    url: https://www.anthropic.com/engineering/building-effective-agents
    type: primary
---

Agent serving 岗会从 `anthropic-tool-use` 追到「结果太大怎么办」。Messages API 的往返是：模型出 `tool_use`，宿主执行，把 `tool_result` 当 user 块贴回去。下一次请求把这段历史整段再送。所以结果既是模型的观察，也是缓存前缀的一部分。题来自产品和 `anthropic-prompt-cache`，不是隐藏面经。

## 过大：截断是合同，不是静默丢

一次 `cat`、一次网页、一张未压缩截图，都能把窗口打满。我会在宿主设硬顶：字符数或 token 估计，超了就切，并在结果里写明「truncated, kept first N chars, original M」。模型才能决定再 `grep` 或换工具，而不是以为文件只有这么长。

三条路：

1. **头尾保留。** 日志、HTML 常把头和尾拼起来，中间写省略。比只留开头更不容易丢掉报错。
2. **外置。** 大文件写到沙箱路径，结果只回路径和前几行，逼模型按需读。这是 Claude Code 那类 agent 的默认。
3. **摘要。** 只在结果确定是自然语言散文时用。代码、JSON、表格摘要会丢键，下一轮参数就编。

截图更狠：每张按 `anthropic-vision` 的 $T_{\mathrm{vis}}$ 计，二十步不丢历史，视觉 token 能到三万。只留最近 1–2 张，旧的改成文本动作记录。`is_error` 的结果不要再塞半截 HTML；给错误码和可修的字段。

不要把堆栈、密钥、Set-Cookie 回灌进上下文。结果当不可信数据，边界见 `anthropic-prompt-injection` 和 `anthropic-xml-prompt`。

```python
MAX = 8000
def pack_result(text, tool_use_id):
    if len(text) <= MAX:
        body = text
    else:
        body = text[:MAX] + f"\n[truncated {len(text) - MAX} chars]"
    return {"type": "tool_result", "tool_use_id": tool_use_id, "content": body}
```

截断阈值要固定。这一轮 8k、下一轮 6k，缓存从 `tool_result` 那一块起全部作废。

## 前缀：结果一变，后面全 miss

`anthropic-prompt-cache` 的命中条件是字节级前缀：`tools` → `system` → `messages`。`tool_result` 在 messages 里。你若把 breakpoint 打在「含最新工具结果」的那一块，每次结果不同就等于每次重写缓存，付写溢价还不命中。

正确切法：

- **工具定义、系统提示、长文档** 打 breakpoint，跨请求不变。
- **本轮 `tool_result`、检索片段、时间戳** 放在点后面，当可变后缀。
- 文档允许在 `tool_result` 上打点，只适合「同一结果会被立刻再读很多次」的预热，不适合每步都变的 agent。

破坏前缀的常见手法：

| 动作 | 为什么 miss |
| --- | --- |
| 压缩历史时改写旧 `tool_result` | 中间一块变了，后面全断 |
| 并行工具结果按完成时间乱序回贴 | 块顺序进哈希 |
| 同一错误有时包 `is_error` 有时只写文本 | 字节不同 |
| 截图有时 JPEG 有时 PNG | 视觉块字节不同 |
| 为 compaction 另开无工具的总结请求 | 从 tools 起就分叉 |

并行 `tool_use` 必须按模型给出的块顺序回传，缺一块请求会拒。Computer use 一批多个动作，更要按序贴结果，见 `anthropic-computer-use`。

## 和流式、MCP、窗口

流式还没拼完 JSON 就执行，结果形状会漂，见 `anthropic-streaming-tools`。MCP 服务器返回的资源当数据，描述进上下文等于可执行 prompt，见 `anthropic-mcp`。窗口预算：文本结果按 tokenizer 计，图按 $T_{\mathrm{vis}}$ 计，两者抢同一条 $T$，见 `anthropic-long-context`。

错法：结果超过窗口就静默丢最后一轮；截断不标注；把「本次检索时间」写进要缓存的 system；为了省 token 把旧工具结果改写成摘要却仍指望命中旧 cache。

## 追问

- **截断了模型会不会编尾巴？** 会。所以标注必须在结果里，不在只有你看得见的日志里。评测加「文件后半段有针、截断后不应答出」的 case，手法同 `anthropic-needle`。
- **tool_result 能不能当 citations 源？** 先把命中段做成 document 再开 `anthropic-citations`。裸工具输出没有页码指针。
- **重试同一 tool_use_id 吗？** 读工具可以。写工具看幂等，见 `anthropic-streaming-tools`。结果回贴必须仍挂同一个 id。
- **和 Batch 一起用？** 离线往返走 `anthropic-batch-api`。前缀仍要稳，否则批处理的写缓存全浪费。

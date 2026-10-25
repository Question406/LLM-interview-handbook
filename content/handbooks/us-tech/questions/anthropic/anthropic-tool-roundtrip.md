---
id: anthropic-tool-roundtrip
section: anthropic
order: 30
level: A
title: Anthropic：tool 往返结果过大、截断、cache 前缀被破坏，怎么处理？
quick: "我会给工具输出设固定上限，超限时明确告诉模型截掉了什么，再让它按需读剩余内容。tools 和 system 保持稳定，最新结果放在缓存点之后；改写旧结果、改变截断长度或回贴顺序，都会让后面的缓存失效。"
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

我会在宿主侧限制工具结果的大小，并把变化的结果放在缓存前缀之后。Messages API 里，模型先给出 `tool_use`，宿主执行后把 `tool_result` 作为 user 块回传；下一轮还会发送这段历史。因此，结果过大会挤满窗口，结果的字节或位置变化也会破坏缓存。工具循环本身见 `anthropic-tool-use`。

## 输出过大时怎么处理

一次 `cat`、一次网页、一张未压缩截图，都能把窗口打满。我会在宿主设硬顶：字符数或估计的 token 数，超了就切，并在结果里写明「truncated, kept first N chars, original M」。模型才能决定再 `grep` 或换工具，而不是以为文件只有这么长。

日志和 HTML 可以保留头尾，在中间注明省略，这样比只留开头更容易保住报错。大文件可以写到沙箱路径，先回路径和前几行，让模型按需读取，Claude Code 那类 agent 默认就采用这种方式。

如果结果是自然语言散文，还可以做摘要。代码、JSON 和表格不适合这么做：摘要可能漏掉键，模型下一轮就可能编出不存在的参数。

截图的占用更大：每张按 `anthropic-vision` 的 $T_{\mathrm{vis}}$ 计，二十步不丢历史，视觉 token 能到三万。只留最近 1–2 张，旧的改成文本动作记录。`is_error` 的结果不要再塞半截 HTML；给错误码和可修的字段。

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

## 怎么保持缓存前缀稳定

`anthropic-prompt-cache` 的命中条件是字节级前缀：`tools` → `system` → `messages`。`tool_result` 在 messages 里。你若把 breakpoint 打在「含最新工具结果」的那一块，每次结果不同就等于每次重写缓存，付写溢价还不命中。

我会把 breakpoint 放在跨请求不变的工具定义、系统提示和长文档上。本轮 `tool_result`、检索片段和时间戳放到点后面，作为可变后缀。文档也允许在 `tool_result` 上打点，但适合的是同一个结果马上会被反复读取的预热场景；每步结果都变的 agent 很难从中获益。

破坏前缀的常见手法：

| 动作 | 为什么 miss |
| --- | --- |
| 压缩历史时改写旧 `tool_result` | 中间一块变了，后面全断 |
| 并行工具结果按完成时间乱序回贴 | 块顺序进哈希 |
| 同一错误有时包 `is_error` 有时只写文本 | 字节不同 |
| 截图有时 JPEG 有时 PNG | 视觉块字节不同 |
| 为 compaction 另开无工具的总结请求 | 从 tools 起就分叉 |

并行 `tool_use` 必须按模型给出的块顺序回传，缺一块请求会拒。Computer use 一批多个动作，更要按序贴结果，见 `anthropic-computer-use`。

流式、MCP 和窗口预算也会影响结果处理。

流式还没拼完 JSON 就执行，结果形状会漂，见 `anthropic-streaming-tools`。MCP 服务器返回的资源当数据，描述进上下文等于可执行 输入提示（prompt），见 `anthropic-mcp`。窗口预算：文本结果按 tokenizer 计，图按 $T_{\mathrm{vis}}$ 计，两者抢同一条 $T$，见 `anthropic-long-context`。

常见误区是：结果超过窗口就静默丢最后一轮；截断不标注；把「本次检索时间」写进要缓存的 system；为了省 token 把旧工具结果改写成摘要却仍指望命中旧 cache。

## 追问

- **截断了模型会不会编尾巴？** 会。所以标注必须在结果里，不在只有你看得见的日志里。评测加「文件后半段有针、截断后不应答出」的 case，手法同 `anthropic-needle`。
- **tool_result 能不能当 citations 源？** 先把命中段做成 document 再开 `anthropic-citations`。裸工具输出没有页码指针。
- **重试同一 tool_use_id 吗？** 读工具可以。写工具看幂等，见 `anthropic-streaming-tools`。结果回贴必须仍挂同一个 id。
- **和 Batch 一起用？** 离线往返走 `anthropic-batch-api`。前缀仍要稳，否则批处理的写缓存全浪费。

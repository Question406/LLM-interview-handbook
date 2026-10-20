---
id: anthropic-prompt-cache
section: anthropic
order: 16
level: A
title: Anthropic：prompt caching 为什么要求前缀稳定，breakpoint 该打在哪？
quick: >-
  缓存的是从请求开头到 breakpoint 的字节级前缀，顺序固定是 tools → system → messages。前缀里改一个时间戳，后面全 miss。写缓存 5
  分钟 TTL 约 1.25 倍输入价，1 小时约 2 倍；命中约 0.1 倍。Breakpoint 打在跨请求不变的最后一块，不要打在每轮都变的 user 消息上。
tags:
  - Anthropic
  - Prompt caching
  - Serving
  - Latency
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Prompt caching (Claude Docs)
    url: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
    type: primary
  - title: Lessons from building Claude Code — Prompt caching is everything
    url: https://claude.com/blog/lessons-from-building-claude-code-prompt-caching-is-everything
    type: primary
---

Agent / serving 岗会把 输入提示（prompt） caching 当系统设计题，不是「记得开个开关」。官方机制是前缀缓存：同一条前缀反复进模型，KV 不用从头算。Claude Code 那篇工程文把教训收成一句：整个系统都要围着前缀稳定性转。

## 命中条件是字节级前缀

请求渲染顺序是 `tools` → `system` → `messages`。Cache key 是到某个 `cache_control` breakpoint 为止的整段前缀哈希。位置 $N$ 改一个字节（工具列表重排、JSON 键顺序、时间戳、thinking / effort 配置），$N$ 及之后的 breakpoint 全部作废。

两套打点：

1. 顶层自动缓存。请求上挂一个 `cache_control`，系统把点打在最后一个可缓存块，对话变长时点跟着走。适合多轮、每轮只在末尾追加。
2. 显式 breakpoint。打在具体 content block 上。静态系统提示、工具定义、长文档用这个。最多 4 个点。读取时从你的点往回看最多约 20 个块，找以前写过的条目，不是「自动发现后面还有稳定内容」。

最短可缓存长度按模型而变，不够长会静默不缓存：`cache_creation_input_tokens` 和 `cache_read_input_tokens` 都是 0。不要当成报错。看 `usage` 里这两个字段，不要只看 HTTP 200。

```python
# 点打在静态前缀的最后一块；user 消息放在点后面
system = [
    {"type": "text", "text": SYSTEM},
    {
        "type": "text",
        "text": TOOLS_AND_DOCS,
        "cache_control": {"type": "ephemeral"},  # 默认约 5 分钟
    },
]
```

1 小时 TTL 写成 `{"type": "ephemeral", "ttl": "1h"}`。混合 TTL 时，长 TTL 必须排在短 TTL 前面。

## 价格和延迟要能算

公开倍率：5 分钟写缓存约 $1.25\times$ 基线输入，1 小时写约 $2\times$，读约 $0.1\times$。输出价不变。同一前缀要被读很多次才划算；只打一次、立刻换前缀，等于付溢价预填。和 Batch 折扣可以叠，见 `anthropic-batch-api`。

延迟上，命中省的是 输入预填充（prefill，即处理输入并建立缓存），不是 逐 token 生成（decode）。长系统提示 + 工具 字段和类型规范（schema） + 仓库摘要这类输入主导的请求，首个 token 的等待时间（TTFT） 掉得最明显。输出很长、输入很短，缓存帮不上。

预热：对共享前缀发一次 `max_tokens: 0`，breakpoint 必须打在后续真请求也共享的那一块。自动缓存会把点打在占位 user 消息上，预热条目永远对不上线流量。Thinking 配置也要一致，它会编进前缀，见 `anthropic-extended-thinking`。

## Breakpoint 放哪

静态工具和系统提示在最前，长文档次之，每轮用户话、检索片段、时间戳放后缀。点打在静态前缀的最后一块。对话增长时，末尾那个点只要每轮新增块数小于 lookback 窗口，就能接到上一轮的写。窗口滑脱就加第二个点钉住旧前缀，不要把四个名额全堆在会变的块上。

常见误区是：工具集每请求按字母重排；system 里塞当前时间；为了 compaction 另开一条「无工具、另一套系统提示」的总结请求，前缀从第一个 token 就分叉，长对话越需要压缩越贵。侧路任务必须复用主对话的 tools / system / thinking。和 `anthropic-rate-limit` 一起讲：缓存命中仍占请求配额，只是 token 账记在 read 桶。

## 追问

- **多租户能共享 cache 吗？** 按官方隔离，不要设计成跨 API key 复用 KV。同组织内靠稳定前缀命中，不靠「把别人的 prompt 当热缓存」。
- **1 小时 TTL 什么时候买？** 流量有间隙、5 分钟会冷，且前缀真稳定。批处理经常超过 5 分钟，共享前缀用 1 小时。
- **工具结果能不能缓存？** 可以打在 `tool_result` 块上，但结果一变前缀就断。只缓存工具定义，结果当可变后缀。
- **换 structured output 的 schema 会 miss 吗？** 会。`output_config.format` 编进前缀，见 `anthropic-json-schema`。

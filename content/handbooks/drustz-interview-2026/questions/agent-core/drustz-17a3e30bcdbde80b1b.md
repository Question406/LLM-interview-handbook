---
id: drustz-17a3e30bcdbde80b1b
section: agent-core
order: 5
level: A
title: 01 · Agent Loop 与 Tool 契约 · 3. Claude tool-use 协议（7 步）⭐⭐⭐
quick: 作者文档章节 · 01 · Agent Loop 与 Tool 契约 · 3. Claude tool-use 协议（7 步）⭐⭐⭐
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - Agent · Core、Gaps 与 Benchmarks
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/01_loop_and_tools.md
    type: primary
---
## 3. Claude tool-use 协议（7 步）⭐⭐⭐

1. 发送 user message 和 tool schemas。
2. assistant 返回一个或多个 `tool_use` block，响应停止原因表明需要工具。
3. 把完整 assistant content 加入 history。
4. 执行每个工具。
5. 下一条 user message 中放所有对应 `tool_result`，每个匹配 `tool_use_id`。
6. 工具异常作为带 error 标记的 result 回传，给模型观察后决定新策略。
7. 外层仍强制 max steps/deadline/cost。

并行规则：同一 turn 的多个结果一起回传；只读且独立的调用可以有界并行，写操作默认不并行。

> 高分句：工具异常是 observation，不是 exception——回传给模型让它改策略，但是否允许重试由外层 policy 决定。






**深潜：并行 tool call 与流式参数解析的工程实现**



【技术机制 · 并行调用】

- 协议：一条 assistant message 可以含多个 `tool_use` block，`stop_reason="tool_use"`。API 不规定执行顺序——`asyncio.gather` 并发、顺序执行、按 §4 的 `parallel_safe/risk` 分组混合执行都是合法的，执行策略完全是 harness 的决定。
- 结果回传的硬规则：该 turn 所有 `tool_result` 必须放在**紧跟着的同一条 user message** 里，每个用 `tool_use_id` 配对，且 `tool_result` block 必须排在该消息 content 的最前面。
- 最隐蔽的坑：把多个结果拆成多条 user message **不报错**，但等于在 history 里给模型演示「一次只调一个工具」——几轮之后模型就不再并行了。history 即 few-shot，格式错误会被模型学走（官方 docs 明确警告这一点）。
- 关停/强制开关：`tool_choice` 四种取值 `auto` / `any`（必须调某个工具）/ `tool`（必须调指定工具）/ `none`；`auto` 下可设 `disable_parallel_tool_use: true` → 每轮最多一个 tool call。写操作多的 agent 常直接关并行换确定性。

【技术机制 · 流式参数（partial JSON）】

- 标准 streaming 下，`tool_use` block 的 `content_block_start` 事件里 `input` 是空对象占位，参数以一串 `input_json_delta` 事件到达，payload 是 `partial_json` 字符串片段，**不按 JSON 边界切**；客户端拼接后在 `content_block_stop` 时 parse。默认服务端会缓冲并校验完整 JSON 后才下发。
- 加 beta header `fine-grained-tool-streaming-2025-05-14` 则去掉服务端缓冲，片段随生成直接下发：首字节延迟大幅下降（适合流式展示长代码/长文档参数），代价是可能收到非法 JSON——尤其 `max_tokens` 把参数拦腰截断时。

```python
buf = {}
async for ev in stream:
    if ev.type == "content_block_start" and ev.content_block.type == "tool_use":
        buf[ev.index] = {
            "id": ev.content_block.id,
            "name": ev.content_block.name,
            "json": "",
        }
    elif ev.type == "content_block_delta" and ev.delta.type == "input_json_delta":
        buf[ev.index]["json"] += ev.delta.partial_json
        maybe_render(
            best_effort_parse(buf[ev.index]["json"])
        )  # 进度 UI 用宽容前缀的 partial-JSON parser
    elif ev.type == "content_block_stop" and ev.index in buf:
        try:
            args = json.loads(buf[ev.index]["json"] or "{}")
        except json.JSONDecodeError:
            args = None  # fine-grained + 截断：当 validation error 回传模型，绝不带半截参数执行
```



【失败模式】

- `tool_use_id` 配对错/漏一个 result → 下一次 API 调用直接 400。
- 截断的 JSON 拿去执行写操作 = 半参数副作用，最危险的一类 bug；guard parse 是必须的。
- 用严格 `json.loads` 做逐片段进度展示会一直抛异常——进度展示要用容忍不完整前缀的 parser，最终执行仍用严格 parse。

来源：[Parallel tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use) ｜ [Fine-grained tool streaming](https://docs.claude.com/en/docs/agents-and-tools/tool-use/fine-grained-tool-streaming)

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/01_core/01_loop_and_tools.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/01_loop_and_tools.md)。作者整理资料；许可和第三方来源范围见阅读指南。

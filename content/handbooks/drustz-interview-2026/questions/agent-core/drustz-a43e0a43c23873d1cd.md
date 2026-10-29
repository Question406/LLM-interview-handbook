---
id: drustz-a43e0a43c23873d1cd
section: agent-core
order: 89
level: A
title: Streaming 与可中断 UX · 现有系统怎么做
quick: 作者文档章节 · Streaming 与可中断 UX · 现有系统怎么做
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/streaming.md
    type: primary
---
## 现有系统怎么做

| 系统/方法 | 核心机制一句话 | 适用场景 | 链接 |
|---|---|---|---|
| SSE / EventSource 协议本体 | `id:`/`retry:` 帧 + 浏览器自动重连时回报 `Last-Event-ID`，replay 语义协议内建 | 一切下行流的传输底座 | [MDN](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) |
| Anthropic Messages streaming | 嵌套状态机：`message_start` → 按 `index` 的 `content_block_start/delta/stop` → `message_delta/stop`；tool args 走 `input_json_delta` 累积 | provider 侧事件模型的参照实现 | [docs](https://platform.claude.com/docs/en/build-with-claude/streaming) |
| OpenAI Responses streaming | 扁平 semantic events（`response.output_text.delta` 等），每事件带全局 `sequence_number` 游标；background mode = 官方 durable 流 | 对照事件建模差异；服务端可恢复流的官方版 | [docs](https://developers.openai.com/api/docs/guides/streaming-responses) |
| Vercel resumable-stream（AI SDK resume） | Redis pubsub + producer 侧 buffer：重连带 `resumeAt` 字符偏移，先补发 buffer 再接 live | Next.js/serverless 快速补上"刷新不丢流" | [GitHub](https://github.com/vercel/resumable-stream) |
| 自建 durable event log（LibreChat/Netclode 模式） | 事件全量 `XADD` 进 Redis Stream，连接只是 log 上的 cursor：`XREAD` 补历史 → `XREAD BLOCK` 续实时 | 多设备/多实例/审计要求的产品级方案 | [Ably 分析](https://ably.com/blog/ai-chat-stream-resumption) |
| partial-json 增量解析 | 对前缀 JSON 补全未闭合括号/按 `Allow` mask处理截断字面量，解析出"目前为止"的对象 | 流式 tool args 的展示层渲染 | [GitHub](https://github.com/promplate/partial-json-parser-js) |





**SSE 协议 + 服务端 replay 伪码（event buffer + Last-Event-ID）**



【技术机制】wire format 是行协议：`event:`（事件名）、`data:`（payload，多行拼接）、`id:`（设置客户端 `lastEventId`）、`retry:`（重连等待 ms），空行分隔事件。连接断开后浏览器自动重连并带 `Last-Event-ID` 请求头——replay 是服务端的责任，协议只负责把 cursor 送回来。

```python
buffers: dict[run_id, list[tuple[int, str, dict]]]  # 生产用 Redis Stream，内存版示意


async def sse_endpoint(req, run_id):
    # Last-Event-ID 与 ?after= 是同一 cursor 的两种拼法
    cursor = int(req.headers.get("Last-Event-ID") or req.query.get("after", -1))
    resp = start_response(
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # 关 nginx buffering，否则整段攒着不发
        }
    )
    resp.write("retry: 3000\n\n")
    sub = subscribe(run_id)  # 1) 先订阅，避免 replay 与 live 之间丢事件
    for seq, etype, payload in buffers[run_id]:  # 2) replay backlog
        if seq > cursor:
            resp.write(f"id: {seq}\nevent: {etype}\ndata: {json.dumps(payload)}\n\n")
            cursor = seq
    async for seq, etype, payload in sub:  # 3) 接 live，按 seq 去重（订阅早于 replay）
        if seq <= cursor:
            continue
        resp.write(f"id: {seq}\nevent: {etype}\ndata: {json.dumps(payload)}\n\n")
    # 4) 心跳：每 15s 写 ": ping\n\n"（注释行，不触发 onmessage），防 LB idle timeout
```



- 关键参数：heartbeat 周期必须 < LB idle timeout（常见 60s → 用 15s）；`retry` 只是建议值，浏览器默认 ~3s。
- 设计理由：先订阅再补历史 + 按 seq 去重 = 至少一次投递、恰好一次渲染；id 必须用 log 序号（单调），挂钟时间戳不单调会导致去重失败。
- 坑：EventSource 只支持 GET 且不能带自定义 header（要带 Authorization 得用 fetch + ReadableStream 手动解析 SSE，即 fetch-event-source 模式）；HTTP/1.1 每域 6 条连接上限（HTTP/2 才解）；buffer 无 TTL/截断策略会内存爆。









**Anthropic streaming 事件状态机 + 中断语义**



【技术机制】嵌套三层：message → content block（按 `index` 寻址，支持并行多 block）→ delta。完整序列：

```text
message_start                          # 空 message 壳（id/model/usage 初值）
  content_block_start (index=0, type)  # text | tool_use | thinking
  content_block_delta (index=0)*       # delta 子类型见下
  content_block_stop  (index=0)
  ...（index=1, 2 重复）
message_delta                          # 顶层增量：stop_reason + 最终 usage
message_stop
```



delta 子类型：`text_delta`（append 文本）、`input_json_delta`（tool args 的**字符串片段** `partial_json`，需累积）、`thinking_delta`、`signature_delta`。另有 `ping`（可随时出现，保活）和 `error` 事件（如 mid-stream `overloaded_error`——要重试而不是当作正常结束）。

```ts
const blocks: Block[] = [];
for await (const ev of stream) {
  switch (ev.type) {
    case "content_block_start":
      blocks[ev.index] = init(ev.content_block);
      break;
    case "content_block_delta": {
      const b = blocks[ev.index];
      if (ev.delta.type === "text_delta") b.text += ev.delta.text;
      if (ev.delta.type === "input_json_delta") b.partialJson += ev.delta.partial_json;
      break;
    }
    case "content_block_stop":
      if (blocks[ev.index].type === "tool_use")
        blocks[ev.index].input = JSON.parse(blocks[ev.index].partialJson); // 此刻才合法、才可执行
      break;
    case "message_delta":
      stopReason = ev.delta.stop_reason;
      usage = ev.usage;
      break;
  }
}
```



- 设计理由：`index` 寻址让并行 blocks（text + 多个 tool_use + thinking 交错）能在同一条流里复用同一套 start/delta/stop 生命周期；SDK 的 accumulator（Python `stream.get_final_message()`、Go `message.Accumulate(event)`）就是上面这段的官方实现。
- 中断语义：client 侧 AbortSignal / `stream.close()` → 断 HTTP 连接 → 服务端停止生成。**没有撤回**：已生成 token 照常计费，所以 turn 状态机里 partial 必须显式落 `aborted` 并记 usage。
- 坑：对 `input_json_delta` 逐 chunk `JSON.parse`（必炸，见 partial-json 块）；忽略 `ping` 把长间隔误判为断流；漏处理 `message_delta` 里的 `stop_reason=max_tokens`（截断被当完整回复进 history）。









**OpenAI Responses streaming：扁平事件 + background 可恢复流**



【技术机制】与 Anthropic 的嵌套模型相反，OpenAI Responses API 用**扁平 semantic events**——路径编码在事件名里，定位靠字段：

```text
response.created → response.in_progress
  response.output_item.added (output_index)
    response.content_part.added (content_index)
      response.output_text.delta {item_id, output_index, content_index, delta, sequence_number}*
      response.output_text.done
  response.output_item.done
response.completed | response.failed | error
```



- 工具参数走 `response.function_call_arguments.delta`（同样是字符串片段，`...done` 事件才是完整 JSON）；另有 `response.refusal.delta`、`response.reasoning_text.delta`——只订 `output_text.delta` 会漏内容。
- **每个事件带全局递增 `sequence_number`**：这是官方内建的重连游标。background mode（请求带 `background: true`）把生成变成服务端任务：断连不杀生成，可 `GET /v1/responses/{id}` 轮询、带 `starting_after=<sequence_number>` 重挂 stream，`POST /v1/responses/{id}/cancel` 显式取消——等于官方托管版"durable log + cursor"，与自建方案是同构的。
- normalization（自建 harness 最难点）：内部统一事件 `{run_id, seq, kind: text_delta | tool_args_delta | lifecycle, block_ref}`——Anthropic 的 `(event.type, index, delta.type)` 与 OpenAI 的 `(type 字符串, output_index/content_index)` 各写一个 mapper 收敛到这一层，UI 与持久化只认内部模型。
- 坑：把旧 chat.completions 的 chunk 模型（`choices[].delta`，无 lifecycle 事件）和 Responses 语义事件混在一个 handler 里；忽略 `response.failed` / `error` 事件只等 `completed`。









**Vercel resumable-stream：Redis pubsub + buffer 的 resume 实现**



【技术机制】一个 `streamId` 对应一个活跃 producer。fast path（无人重连）只花一个 `INCR` + `SUBSCRIBE`，几乎零开销；producer 把每个 chunk 追加进自己的 buffer 并 publish 到 Redis channel。重连时 consumer 调 `resumeExistingStream(streamId, resumeAt)`，producer 收到信号后把 buffer 里的内容补发（跳过前 `resumeAt` 个字符）再接 live。

```ts
const ctx = createResumableStreamContext({ waitUntil }); // serverless 里靠 waitUntil 保活 producer

// POST /api/chat —— 生成侧
const stream = await ctx.resumableStream(`chat-${chatId}`, () => llmSseStream());

// GET /api/chat/[id]/stream —— 重连侧（useChat({ resume: true }) 挂载时自动打）
const resumed = await ctx.resumeExistingStream(`chat-${chatId}`, resumeAt);
if (!resumed) return new Response(null, { status: 204 }); // 无活跃流；已完成流返回 422
```



- 设计理由：为 serverless（无 sticky LB、函数随时被回收）优化——不做全量持久化，只在"producer 还活着"的窗口内提供 resume，把常态成本压到最低。
- 与自建 durable log 的本质区别：**cursor 是字符偏移不是事件 id**；buffer 挂在 producer 上而非独立存储——producer 死了流就没了；已完成的流 resume 返回 422（要靠落库的最终消息兜底）。所以它解决"刷新/闪断不丢流"，不解决多设备、跨实例、审计。
- 坑：abort 与 resume 的交互（[vercel/ai#6502](https://github.com/vercel/ai/issues/6502)：客户端 stop 后 resumable stream 不停，服务端继续烧钱）；partial 消息默认无标记进 history；换 Redis 客户端要用 `resumable-stream/ioredis` 或 `/generic` 入口。









**自建 durable event log：Redis Streams + after= cursor（对应 02_playbook）**



【技术机制】每个 run 一个 stream key（`run:{id}:events`）。写侧 orchestrator 把**全部**事件 `XADD`（lifecycle 逐条写；text delta 先合帧——如每 50ms 或 20 token 一条——再写，否则每 token 一条 XADD 打爆 Redis）。`XADD` 自动 ID 是 `<ms>-<seq>`，单调且免费解决"别用挂钟"问题。读侧：

```python
async def stream_events(run_id, cursor="0-0"):
    key = f"run:{run_id}:events"
    # 1) catch-up：非阻塞读 backlog 直到追平
    while batch := await redis.xread({key: cursor}, count=500):
        for id_, ev in batch[0][1]:
            yield sse_frame(id_, ev)
            cursor = id_
    # 2) live：阻塞等新事件；超时窗口顺便当心跳
    while await run_active(run_id):
        batch = await redis.xread({key: cursor}, block=15_000)
        if not batch:
            yield ": ping\n\n"
            continue
        for id_, ev in batch[0][1]:
            yield sse_frame(id_, ev)
            cursor = id_
```



- `GET /runs/{id}/events?after={cursor}` 与 SSE 的 `Last-Event-ID` 是同一 cursor 的两种拼法——一套 log 同时服务流式 UI、轮询客户端和 webhook 补偿。
- 投递语义：catch-up 与 live 的边界可能重复 → 至少一次投递 + 客户端按 id 去重 = 恰好一次渲染。
- 保留策略：`XTRIM MAXLEN ~10000` 截断 + run 完成后把最终 message 落主库、事件转冷存 + key TTL——三层兜底防内存爆。
- 多实例：状态在 Redis 不在进程内，任意 API 副本可服务重连，rolling deploy 不掉流（LibreChat 即此模式）。Ably 给出的边界：单区域 + 短 TTL 内 Redis 够用；跨区域接管、长离线、agent handoff 才需要 durable session 产品（offset-based resumption 的托管版）。
- 坑：用 Redis pub/sub 代替 Stream（无 backlog，断线即丢）；lifecycle 事件与 delta 不分级，降级时把 `item/completed` 一起丢掉导致客户端状态机错乱。









**partial JSON 解析 + 流式渲染管线（delta→缓冲→markdown 安全渲染）**



【技术机制·parser】`partial-json`（[JS](https://github.com/promplate/partial-json-parser-js) / [Python](https://github.com/promplate/partial-json-parser)）的思路：解析到输入结尾时不报错，而是补全未闭合的容器（`}` `]`），截断的字面量按 `Allow` bitmask决定保留还是丢弃——`parse('{"a": "hel', Allow.STR)` → `{a: "hel"}`；不允许 `STR` 时 → `{}`（防止把半截 URL 当完整 URL 用）。注意每个 chunk 重解析整个 buffer 是 O( $n^{2}$ )——参数大或频率高时用维护活对象的增量 parser（`feed()` 只扫新字节）或降频到渲染帧。

铁律：**partial 结果只做展示**（灰显参数预览）；执行必须等 `content_block_stop` / `...arguments.done` 之后的完整 JSON——绝不 eval 补全产物。

【技术机制·渲染管线】

````ts
let buf = "",
  dirty = false;
onTextDelta((d) => {
  buf += d;
  dirty = true;
}); // 1) delta 只进缓冲，不直接触发渲染
setInterval(() => {
  // 2) 30–60ms 一拍合并渲染（或 rAF）
  if (!dirty) return;
  dirty = false;
  const md = closeDangling(buf); // 3) 临时闭合未完的 ``` 和 * ，防整页闪成代码块
  el.innerHTML = sanitize(renderMarkdown(md)); // 4) DOMPurify——流内容是不可信输入
}, 33);
````



- 设计理由：按帧合并把渲染成本从 O(tokens) 降到 O(帧率)；markdown 按 block 级 memoize（未变段落不重 parse）解决长回复卡顿。
- 坑：每 delta 全量重 parse markdown → 几千 token 后 UI 卡死；sanitize 只在最终消息做、流式路径裸 `innerHTML` → 半截 `<img onerror=` 也会执行，流式 XSS；未闭合 code fence 不做假闭合 → 后续正文全被吞进代码块再"弹回来"，视觉闪烁。生产案例见 [Aha! 的截断 JSON 处理实践](https://www.aha.io/engineering/articles/streaming-ai-responses-incomplete-json)。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/streaming.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/streaming.md)。作者整理资料；许可和第三方来源范围见阅读指南。

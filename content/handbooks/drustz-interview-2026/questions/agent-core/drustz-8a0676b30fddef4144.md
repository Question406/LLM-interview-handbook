---
id: drustz-8a0676b30fddef4144
section: agent-core
order: 86
level: A
title: Streaming 与可中断 UX · 核心概念
quick: 作者文档章节 · Streaming 与可中断 UX · 核心概念
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
## 核心概念

### 传输选型：SSE vs WebSocket ⭐⭐⭐

| 维度 | SSE | WebSocket |
|---|---|---|
| 方向 | server→client 单向 | 全双工 |
| 断线恢复 | 浏览器自动重连 + `Last-Event-ID` 协议内建 | 自己造：心跳、重连、resume token |
| 基础设施 | 纯 HTTP，LB/proxy/HTTP2 友好（需关 buffering） | 需 LB 支持 upgrade，企业代理常掐长连接 |
| 客户端→服务端控制 | 走独立 POST（stop/steer 是普通请求） | 同连接发 cancel/steer 帧 |
| 适用 | 90% 场景：下行 token/事件流（ChatGPT 即 SSE） | 高频双向：语音、协作编辑、server 发起的 blocking approval |

第三选项：**双向 JSON-RPC**（Codex app-server：默认 stdio-JSONL，WS 标注 experimental；approval 是 server 发起的 blocking request，client 回 `accept/decline`；控制有 `turn/steer` 与 `turn/interrupt`）。

> 高分句：先问方向性——只有下行流就 SSE + POST 控制通道；真正需要 server 主动 blocking request 时才上 WS 或双向 JSON-RPC，Codex app-server 就是这个取舍。

### 五个机制 ⭐⭐⭐

| 机制 | 设计要点 |
|---|---|
| 可恢复流 | 生成先写 durable log，event id 单调递增（Redis Stream ID，别用挂钟）；重连带 `Last-Event-ID`/`lastStreamId`，server 从 cursor replay backlog 再接 live（`XREAD` → `XREAD BLOCK`）；至少一次投递 + 客户端按 id 去重 = 恰好一次渲染 |
| token streaming | append-only text delta，直接渲染；持久化与 usage 记在 turn 边界（`onFinish`），不按 chunk 落库 |
| tool-call streaming | 结构化 **partial JSON**：增量 parser 或等参数完整再动作；状态机 `input-streaming → input-available → output-available \| output-error`（AI SDK 5）；各家 SDK 事件序不同，自建 harness 最难的就是normalization这层 |
| 中断语义 | `cancel_requested` ≠ 停止：链路是 flag → abort provider stream → 向 tool 发协作取消（SIGTERM + grace timeout）；cancel 幂等；区分 interrupt（终止）与 steer（注入输入不终止） |
| partial 标注 + 背压 | 被中断消息带终态 `status ∈ {complete, aborted, failed}`，UI 显式"已中断"，进 history 须标注；背压：慢消费者各自拉 log 不反压生成，连接侧队列超限先合帧（coalesce text deltas）再断开 |





**可恢复流实现细节（Netclode / LibreChat / Ably 模式）**



- Netclode：单条双向流（Connect RPC），所有事件持久化 Redis Streams；客户端带 `lastStreamId` 重连，服务端从该 cursor `XREAD` 补历史再 `XREAD BLOCK` 续实时。take-home 可用 SQLite/内存 ring buffer 复刻。
- LibreChat：chunk 实时写入按 `chat_id:message_id` 键的 Redis stream，后端订阅转发为 SSE；Redis 共享使多实例部署下"A 实例开始的生成可在 B 实例恢复"，rolling deploy 不掉流。
- Ably 总结的坑：Redis 够用的边界是单区域 + 短 TTL；跨设备接管、agent handoff 需要 durable session（持久可寻址、offset-based resumption）。
- buffer 要有 TTL/截断策略（如保留最近 N 事件 + 完成后转冷存储），否则长对话内存爆。









**中断链路时序（Stop 按钮到真正停止）**



- UI 乐观置灰 → `POST /turns/{id}/cancel`（幂等，重复点无副作用）→ orchestrator 置 `cancel_requested`。
- 传播：abort provider HTTP stream（SDK 的 AbortSignal）→ running tool 协作取消（cancellation token / SIGTERM，grace timeout 后 SIGKILL）。
- 窗口期 $\Delta t = t_{\text{stopped}} - t_{\text{requested}}$ 内仍有 delta 到达：给每个 turn 一个 epoch，迟到事件按 epoch 丢弃，否则"停了还在打字"。
- 终态落库：`status=aborted`，partial 内容保留；已发生副作用的 tool（邮件已发）不能假装没发生——记录并在 UI 展示。
- usage：中断的 turn 仍计已消耗 token（计费与限流都要）。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/streaming.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/streaming.md)。作者整理资料；许可和第三方来源范围见阅读指南。

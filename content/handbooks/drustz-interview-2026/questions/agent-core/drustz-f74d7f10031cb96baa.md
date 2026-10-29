---
id: drustz-f74d7f10031cb96baa
section: agent-core
order: 85
level: A
title: Streaming 与可中断 UX · 30 秒版本（3 句话）⭐⭐⭐
quick: 作者文档章节 · Streaming 与可中断 UX · 30 秒版本（3 句话）⭐⭐⭐
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
## 30 秒版本（3 句话）⭐⭐⭐

1. Agent 产品的 streaming 本质是 **durability 问题而非 transport 问题**：token 先写 durable event log（Redis Streams / ring buffer），HTTP 连接只是 log 上的一个 cursor——断线重连、多设备、水平扩展全靠这一层解耦。
2. **中断是异步协作协议**：`cancel_requested` 只是意向标记，到 in-flight LLM call / running tool 真正停止有一个窗口期 $\Delta t$，期间到达的 delta 要按 turn epoch 丢弃，partial 结果必须落显式终态（`aborted`）。
3. 传输选型只问一件事：是否需要 server 主动向 client 发起 blocking request（如 approval）——不需要就 SSE + POST 控制通道，需要才升级 WebSocket 或双向 JSON-RPC（Codex app-server 模式，见 [mirendil 整理](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/projects/takehome_mirendil/03_option2_cloud_agent_chat.md)）。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/streaming.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/streaming.md)。作者整理资料；许可和第三方来源范围见阅读指南。

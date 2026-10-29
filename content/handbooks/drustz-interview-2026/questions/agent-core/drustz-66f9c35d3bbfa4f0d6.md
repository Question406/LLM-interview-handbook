---
id: drustz-66f9c35d3bbfa4f0d6
section: agent-core
order: 87
level: A
title: Streaming 与可中断 UX · 面试常问 3 题
quick: 作者文档章节 · Streaming 与可中断 UX · 面试常问 3 题
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
## 面试常问 3 题

**Q1. 设计 ChatGPT backend：SSE streaming + context assembly**（真题：hack2hire 题库 🤖 未交叉验证，[本地](?book=drustz-interview-2026&section=collections&question=drustz-f3ed1fbf85836ee5c7)；OpenAI 前端/全栈轮 2026 也反复考 streaming chat UI + SSE 断流恢复）





**参考打法**



- 先画三层解耦：inference worker（生成）→ durable event log → SSE gateway（按 cursor 转发）；连接死了生成不死，这是全题的锚。
- context assembly 在 turn 开始一次完成：system prompt + memory + token-budget 截断的 history；流式期间上下文不可变，写回在 turn 边界。
- 断线恢复：event id 单调，重连带 `Last-Event-ID`，replay 后接 live；多副本下任意实例可服务重连。
- fan-out 顺带答掉多设备：同一 chat 的多个 tab = 同一 stream 上多个 cursor。
- 主动提 proxy 坑（见常见坑第 5 条）——OpenAI 前端轮明确把"主动讨论边界情况"当评分项。





> 高分句：streaming 层的核心决策是 generation–connection decoupling——连接只是 durable log 上的一个 cursor，重连、多设备、水平扩展三个问题被同一个机制化解。

**Q2. 用户点 Stop 之后，系统里到底发生了什么？**





**参考打法**



- 先分语义两级：interrupt（终止 turn）vs steer（不停止、向进行中 turn 追加输入）——Codex 协议里是两个独立方法 `turn/interrupt` / `turn/steer`。
- 按时序讲全链路：幂等 cancel API → `cancel_requested` flag → abort provider stream → tool 协作取消 + grace timeout。
- 点出窗口期 $\Delta t$ 和 turn epoch 丢弃迟到 delta——这是区分"背过题"和"踩过坑"的细节。
- partial 终态：`aborted` 状态 + UI 标注 + 进 history 时不冒充完整回复；副作用型 tool 的结果要如实保留。
- 收尾提 usage 记账：中断不免单。





> 高分句：中断不是 kill 而是异步协作协议——系统必须显式定义 cancel 意向到真正停止之间事件的处置规则，以及 partial 结果的可信标注。

**Q3. tool-call 怎么流式渲染？慢消费者会把系统拖垮吗？**





**参考打法**



- text delta append-only 直接渲染；tool call 是 partial JSON——用增量 parser 只做展示，**执行必须等 `input-available`**，绝不 eval 半截参数。
- 状态机化：`input-streaming → input-available → (approval 门) → executing → output-available | output-error`；approval 插在 available 与 executing 之间（blocking request）。
- 各 SDK（Claude Agent SDK / Codex / OpenAI）tool 事件排序不同，normalization事件模型是自建 harness 公认最难点。
- 背压：生成写 log、各连接自拉，慢消费者永不反压生成；连接侧队列超限 → 合并 text deltas → tool 参数以完整快照替代增量 → 仍超限则断开让其走 resume 路径。
- lifecycle 事件（`item/started`/`item/completed`）与 delta 分通道对待：降级时 delta 可丢可合，lifecycle 一条不能丢。





> 高分句：背压降级的分界线是——delta 可以合帧或丢弃（可由快照重建），lifecycle 事件必须逐条送达，否则客户端状态机直接错乱。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/streaming.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/streaming.md)。作者整理资料；许可和第三方来源范围见阅读指南。

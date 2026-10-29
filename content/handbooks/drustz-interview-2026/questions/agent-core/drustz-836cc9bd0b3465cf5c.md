---
id: drustz-836cc9bd0b3465cf5c
section: agent-core
order: 88
level: A
title: Streaming 与可中断 UX · 常见坑 checklist
quick: 作者文档章节 · Streaming 与可中断 UX · 常见坑 checklist
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
## 常见坑 checklist

- [ ] stream 生命周期绑死 HTTP 连接：关 tab = 生成中止、刷新 = 丢回复——解耦 + resume 是第一优先级
- [ ] 只做前端 `AbortController`：server 侧 LLM call 与 tool 继续跑，烧钱且状态漂移
- [ ] partial assistant message 无标记进 history（Vercel `useChat` 默认行为），下一轮被当完整回复拼进 context
- [ ] event id 用挂钟时间戳：不单调、重放去重失败——用 log 序号（Redis Stream ID）
- [ ] 反向代理没调：nginx `proxy_buffering off`、LB idle timeout 短于生成时长、无 heartbeat 帧——用户看到"卡死"而非流

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/streaming.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/streaming.md)。作者整理资料；许可和第三方来源范围见阅读指南。

---
id: drustz-8f48d8fa36a92c5e97
section: agent-core
order: 49
level: A
title: Cost / Latency 工程 · 30 秒版本（3 句话）
quick: 作者文档章节 · Cost / Latency 工程 · 30 秒版本（3 句话）
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/cost_latency.md
    type: primary
---
## 30 秒版本（3 句话）

1. Agent 成本由重复 resend 的 history 主导（N 轮循环 input 累积近似 $O(N^2)$），第一杠杆是 prompt caching：前缀字节级稳定（渲染顺序 `tools→system→messages` 固定，breakpoint 前任何 byte 变化使其后全失效），Anthropic 现行价：读 0.1×、5min 写 1.25×、1h 写 2×，命中即省 ~90% input 成本。
2. 第二杠杆是模型分级 + batch：轻量分诊器把简单请求给小模型、大模型兜底（RouteLLM ICLR'25：14% 流量给强模型即保 95% GPT-4 质量、省 85% 成本）；一切不需要人在等的调用走 Batch API 直接 -50%。
3. 延迟拆成 TTFT（交互体验，目标 <500ms 级）和 TPOT（流式throughput，人读速 20–50ms/token 即够）分别归因；工程上用逐层 timeout 预算（SLA 自顶向下递减）+ 有界并行（$cost \le K \cdot B \cdot p$）同时给尾延迟和账单封顶。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/cost_latency.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/cost_latency.md)。作者整理资料；许可和第三方来源范围见阅读指南。

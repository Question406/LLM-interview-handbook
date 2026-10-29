---
id: drustz-5028afbffcebb15710
section: agent-core
order: 52
level: A
title: Cost / Latency 工程 · 常见坑 ⭐⭐⭐
quick: 作者文档章节 · Cost / Latency 工程 · 常见坑 ⭐⭐⭐
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
## 常见坑 ⭐⭐⭐

- [ ] system prompt 插时间戳/uuid/用户名 → 前缀每请求都变，cache 永不命中；`cache_read == 0` 是第一诊断信号
- [ ] 会话中途增删 tool 或换 model → tools 渲染在前缀最前，整条 cache 报废；动态工具用 append，换模型走 subagent
- [ ] 成本核算只看 `input_tokens`：总 input = input + cache_read + cache_creation，多轮 agent 下 cache_read 占大头，漏算会严重低估流量
- [ ] 全部轮次用旗舰模型：summarize/分类/format 类子任务分诊到小模型基本无质量损失——但先 eval 再全量
- [ ] 各层 timeout 拍同一个数（全 30s）：内层重试必撞外层超时；自顶向下递减、给重试留量，且重试本身也烧钱要计入预算

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/cost_latency.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/cost_latency.md)。作者整理资料；许可和第三方来源范围见阅读指南。

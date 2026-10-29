---
id: drustz-1b8a4d83a6cd6b1658
section: agent-core
order: 18
level: A
title: 02 · State、Durable Execution 与 Memory · 9. 自学资料
quick: 作者文档章节 · 02 · State、Durable Execution 与 Memory · 9. 自学资料
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/02_state_and_memory.md
    type: primary
---
## 9. 自学资料

按优先级排序，前 4 条是面试前必读：

1. [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic 官方框架：compaction / structured note-taking / sub-agent 三板斧，长任务 context 管理的最佳总纲 · 预计 20 min
2. [Context Engineering for AI Agents: Lessons from Building Manus](https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus) — 生产 agent 的六条实战经验：KV-cache、file system as context、recitation、保留错误，全是面试可直接引用的细节 · 预计 15 min
3. [Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents) — Cognition 的 context 完整性论证，single-thread vs multi-agent 争论的一极，必须能复述并反驳 · 预计 10 min
4. [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — initializer / feature_list.json / progress 文件 / git checkpoint 的完整配方 · 预计 15 min
5. [MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560) — memory 分层 + self-editing 的原始论文，后续所有 memory 系统都在回应它 · 预计 30 min
6. [Zep: A Temporal Knowledge Graph Architecture for Agent Memory](https://arxiv.org/abs/2501.13956) — bitemporal 边 + 时间失效的冲突处理，看 §2 架构即可 · 预计 25 min
7. [Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory](https://arxiv.org/abs/2504.19413) — extraction→update 两阶段 pipeline 和 LOCOMO 成本数字，读 §3 方法 + §5 结果 · 预计 25 min
8. [Temporal: Workflow Execution Events](https://docs.temporal.io/workflow-execution/event) — event history / replay / determinism 的官方定义，durable execution 面试题的标准出处 · 预计 15 min
9. [Claude Code: How Claude remembers your project](https://code.claude.com/docs/en/memory) — CLAUDE.md 层级 + auto memory 的完整机制，文件式 memory 的参考实现 · 预计 10 min
10. [LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory](https://arxiv.org/abs/2410.10813) — 5 项 memory 能力的评测框架，聊「memory 怎么评」时的引用 · 预计 15 min

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/01_core/02_state_and_memory.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/02_state_and_memory.md)。作者整理资料；许可和第三方来源范围见阅读指南。

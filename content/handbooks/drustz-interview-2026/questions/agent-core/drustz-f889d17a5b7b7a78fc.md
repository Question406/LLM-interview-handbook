---
id: drustz-f889d17a5b7b7a78fc
section: agent-core
order: 8
level: A
title: 01 · Agent Loop 与 Tool 契约 · 6. 自学资料
quick: 作者文档章节 · 01 · Agent Loop 与 Tool 契约 · 6. 自学资料
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
## 6. 自学资料

1. [Building Effective AI Agents](https://www.anthropic.com/engineering/building-effective-agents) — workflow 五模式（chaining/routing/parallelization/orchestrator-workers/evaluator-optimizer）vs agent 的选型框架；回答「什么时候不该用 agent」的标准出处 · 20 min
2. [Writing effective tools for AI agents—using AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents) — §4 checklist 的官方展开：token 效率（分页/截断/默认值）、error 消息的 prompt 工程、用 agent 评测工具 · 20 min
3. [mini-swe-agent（GitHub）](https://github.com/SWE-agent/mini-swe-agent) — 通读 ~100 行 agent 源码建立「最小 harness」心智基线；README 三条设计声明（bash-only / 线性历史 / subprocess.run）可直接引用 · 30 min
4. [Parallel tool use — Claude Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/parallel-tool-use) — 结果消息格式如何反过来训练模型的并行行为；`disable_parallel_tool_use` · 10 min
5. [Executable Code Actions Elicit Better LLM Agents（CodeAct）](https://arxiv.org/abs/2402.01030) — code-as-action 的论证与 up-to-20% 数据，读方法与实验设置即可 · 30 min
6. [OpenAI Agents SDK docs](https://openai.github.io/openai-agents-python/) — 重点读 Running agents（loop 语义）、Handoffs、Guardrails 三页，对照 Claude SDK 找结构差异 · 30 min
7. [Streaming Input mode — Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/streaming-vs-single-mode) — 两种输入模式的能力差异，为什么长驻 agent 必须用 streaming input · 10 min
8. [Fine-grained tool streaming — Claude Docs](https://docs.claude.com/en/docs/agents-and-tools/tool-use/fine-grained-tool-streaming) — 无缓冲流式参数的取舍与 invalid JSON 防御 · 10 min
9. [SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering](https://arxiv.org/abs/2405.15793) — ACI 设计原则（lint 守卫 edit、窗口化 viewer、限量 search），「界面影响 agent 性能」的量化证据 · 30 min
10. [Introducing advanced tool use on the Claude Developer Platform](https://www.anthropic.com/engineering/advanced-tool-use) — 工具规模化的下一步：tool search、programmatic tool calling；回答「几百个 tool 怎么办」 · 15 min

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/01_core/01_loop_and_tools.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/01_loop_and_tools.md)。作者整理资料；许可和第三方来源范围见阅读指南。

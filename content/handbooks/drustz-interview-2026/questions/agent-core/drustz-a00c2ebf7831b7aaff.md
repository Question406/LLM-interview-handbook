---
id: drustz-a00c2ebf7831b7aaff
section: agent-core
order: 37
level: A
title: 06 · Evaluation 与 Security · 8. 现有系统怎么做 ⭐⭐⭐
quick: 作者文档章节 · 06 · Evaluation 与 Security · 8. 现有系统怎么做 ⭐⭐⭐
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/06_eval_security.md
    type: primary
---
## 8. 现有系统怎么做 ⭐⭐⭐

| 系统/方法 | 核心机制一句话 | 适用场景 | 链接 |
|---|---|---|---|
| Inspect AI (UK AISI) | Task = Dataset + Solver + Scorer 组合式抽象；agent 与不可信代码跑在 per-sample Docker/K8s sandbox | 严肃、可复现的 agent eval 基建 | [docs](https://inspect.aisi.org.uk/) |
| τ-bench (Sierra) | LLM user simulator 多轮对话 + DB 终态比对判定 +  $\mathrm{pass}^k$  unbiased estimate | 客服型 tool-agent 的可靠性评测 | [repo](https://github.com/sierra-research/tau-bench) |
| LLM-as-judge calibration (MT-Bench) | pairwise 判两次、交换顺序消 position bias；与人

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/01_core/06_eval_security.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/01_core/06_eval_security.md)。作者整理资料；许可和第三方来源范围见阅读指南。

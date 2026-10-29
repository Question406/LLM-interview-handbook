---
id: drustz-bafc0a559f42978ec7
section: agent-core
order: 83
level: A
title: Agent Self-Improvement：现有实现方法（面试口径版） · 自学资料
quick: 作者文档章节 · Agent Self-Improvement：现有实现方法（面试口径版） · 自学资料
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/self_improvement.md
    type: primary
---
## 自学资料

1. [Demystifying evals for AI agents（Anthropic Engineering）](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — 生产闭环的 eval 侧：失败案例如何变 eval case，Claude Code/Chrome 实例 · 20 min
2. [Remember, Refine, Retrieve（Applied Compute）](https://www.appliedcompute.com/research/remember-refine-retrieve) — Contextbase 三段式 + refinery 闭环 + SME 人审，面 Applied Compute 必读 · 15 min
3. [GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning](https://arxiv.org/abs/2507.19457) — ICLR'26 Oral，反思式 prompt 进化对 RL 的样本效率论证 · 25 min
4. [Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798) — 反面证据：intrinsic self-correction 不 work，定义整个领域的边界 · 15 min
5. [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) — verbal RL 原型：evaluator + self-reflection + episodic buffer · 15 min
6. [Darwin Gödel Machine（Sakana AI 博客）](https://sakana.ai/dgm/) — 自改 harness + archive 树 + objective hacking 实录，博客比论文好读 · 15 min
7. [Voyager: An Open-Ended Embodied Agent with Large Language Models](https://arxiv.org/abs/2305.16291) — 技能库=可执行代码 + 自动 curriculum 的原型 · 15 min
8. [AlphaEvolve（DeepMind 博客）](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) — 进化式代码优化 + automated evaluator 级联 · 10 min
9. [Equipping agents for the real world with Agent Skills（Anthropic）](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — 技能库思想的生产形态：SKILL.md + progressive disclosure · 10 min
10. [DSPy（GitHub）](https://github.com/stanfordnlp/dspy) — prompt 当参数的框架抽象，GEPA 是其 optimizer 之一，扫 README 即可 · 10 min

补充：Self-Refine（无外部信号的自反馈基线，读 2310.01798 时对照）：[arxiv 2303.17651](https://arxiv.org/abs/2303.17651)；DGM 论文全文：[arxiv 2505.22954](https://arxiv.org/abs/2505.22954)。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/self_improvement.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/self_improvement.md)。作者整理资料；许可和第三方来源范围见阅读指南。

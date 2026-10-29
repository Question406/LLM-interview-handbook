---
id: drustz-f08cc94e3ca239031c
section: agent-core
order: 79
level: A
title: Agent Self-Improvement：现有实现方法（面试口径版） · 30 秒版本（3 句话）⭐⭐⭐
quick: 作者文档章节 · Agent Self-Improvement：现有实现方法（面试口径版） · 30 秒版本（3 句话）⭐⭐⭐
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
## 30 秒版本（3 句话）⭐⭐⭐

1. Self-improvement 有几条**正交轴**，区别在于"改进写进了哪个持久物"：**推理时反思**（只改本次 episode 的 context，Reflexion/Self-Refine）、**记忆积累**（改 episodic/semantic memory，见 [02_state_and_memory.md](?book=drustz-interview-2026&section=agent-core&question=drustz-027e90f708cef5244f)）、**技能库**（把成功行为固化成可执行代码复用，Voyager / Claude Code skills）、**提示与代码进化**（把 prompt/程序当可优化参数，DSPy/GEPA/AlphaEvolve/DGM）、**权重更新**（RL/SFT，见 [agentic_rl.md](?book=drustz-interview-2026&section=agent-core&question=drustz-ecc62e136df467a25f)）。
2. 最重要的实证边界：**没有外部信号的"自我反思"基本不 work**——[Cannot Self-Correct](https://arxiv.org/abs/2310.01798)（ICLR'24）证明 intrinsic self-correction 去掉 oracle label 后增益消失甚至变差；所以所有靠谱方法都由**外部 verifier**（单测、环境反馈、benchmark 分数、生产失败信号）驱动。
3. 工程上分**三档**记：① test-time——不改任何持久物，episode 结束即丢；② 数据与提示层——改 prompt/memory/skills，**可 diff、可回滚、可人审**，是生产系统的主战场；③ 权重层——RL/SFT，收益最持久但回滚与审计成本最高。生产闭环 = traces → failure taxonomy → eval case → 修（②或③）→ 过 eval gate + 人审。

---

来源：[DrustZ / Mingrui Zhang · agentic_prep/03_gaps/self_improvement.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/agentic_prep/03_gaps/self_improvement.md)。作者整理资料；许可和第三方来源范围见阅读指南。

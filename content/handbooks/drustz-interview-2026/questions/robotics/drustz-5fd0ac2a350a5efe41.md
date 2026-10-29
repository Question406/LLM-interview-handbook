---
id: drustz-5fd0ac2a350a5efe41
section: robotics
order: 49
level: A
title: 06 — System Design Playbooks：四道 Robotics ML 高频题 · 0. 45 分钟答题节奏模板
quick: 作者文档章节 · 06 — System Design Playbooks：四道 Robotics ML 高频题 · 0. 45 分钟答题节奏模板
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - Robotics · Data、Learning 与 System Design
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/06_system_design_playbooks.md
    type: primary
---
## 0. 45 分钟答题节奏模板

| 时间 | 阶段 | 要点 |
|---|---|---|
| 0–5 min | 需求澄清 | 问 4–6 个问题锁 scope（用途优先级、规模、延迟/安全约束、现有资源）。主动说 "Let me assume X for now — happy to revisit."。**robotics 题必问：What's the physical cost of failure?** |
| 5–10 min | 数量级估算 | 现场算带宽/存储/trial 数/GPU-hours，**用估算结论驱动设计决策**（"450 TB/day is infeasible, so we must go trigger-based"）。 |
| 10–22 min | 高层架构 | 画端到端框图（边缘 → 传输 → 云端 → 训练 → 部署 → 监控闭环），先讲数据流再讲组件，每个箭头标协议/数据量级。robotics 题的通用骨架就是数据飞轮。 |
| 22–37 min | 深挖 1–2 个组件 | 主动说 "I think X and Y are the hardest parts — which would you like to go deeper on?" 把选择权给面试官，同时展示你知道难点在哪。深挖给**具体机制**（状态机、检验公式、缓冲策略），不是更多框图。 |
| 37–42 min | Tradeoff / 失败模式 / 演进 | 每个关键决策给出被否掉的替代方案及理由；2–3 个失败模式及降级路径；一句话讲 10 倍规模后什么先崩。 |
| 42–45 min | 收尾 | 30 秒总结 + 明说残留风险，留提问时间。 |

贯穿技巧：
- 每 10 分钟对齐一次："Does this direction work for you, or should I pivot to X?"
- 安全层与 ML 层解耦，四题通用，随时可以掏出来。
- 你练过的 LLM pipeline 直觉大部分可迁移（immutable data + manifest、registry 状态机、金丝雀放量）——面试时可以一句带过 "this part is standard data-infra"，把时间花在 robotics delta 上。

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/06_system_design_playbooks.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/06_system_design_playbooks.md)。作者整理资料；许可和第三方来源范围见阅读指南。

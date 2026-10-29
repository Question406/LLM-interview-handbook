---
id: drustz-0c9fd6c5f84a80b283
section: mlsd
order: 72
level: A
title: 09 · ML System Design 题库 · G. Evaluation / Production（7 题）
quick: 作者文档章节 · 09 · ML System Design 题库 · G. Evaluation / Production（7 题）
companies: []
tags:
  - DrustZ
  - 作者文档章节
  - ML System Design · 全流程
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/09_question_bank.md
    type: primary
---
## G. Evaluation / Production（7 题）

### G1. Offline 指标提升多少才上线？

答题锚点：没有固定百分点；pre-registered minimum effect + CI、guardrails、slice、cost/SLO；shadow/canary 验证 transfer。

### G2. 如何估计需要多少 GPU？

答题锚点：peak QPS、service time、tokens/image distribution、batch/utilization、memory/KV、headroom；用真实 shadow profile，不拿峰值 FLOPs 直接除。

### G3. 如何设计 model cascade？

答题锚点：calibrated uncertainty + value/risk routing、双阈值、conditional quality、escalation rate、人审容量、cost minimization。

### G4. 模型漂移告警后是否自动重训？

答题锚点：先区分 schema/traffic/seasonality/label delay/concept；retrain 仍走 frozen eval、canary、rollback。

### G5. 标签 30 天后才有，如何在线监控？

答题锚点：领先 proxy + calibration/input/prediction drift + random human audit；最终按 cohort join delayed outcome，不用 proxy 替代 truth。

### G6. 量化后平均分不变，可以上线吗？

答题锚点：关键 slice、calibration、tail latency、long context/rare class、安全、hardware-specific numerics；shadow + canary。

### G7. 怎样证明系统真正节省了成本？

答题锚点：cost/success、total workflow + human correction、quality-adjusted throughput、A/B、固定质量 operating point；不是只报单次 inference 价格。

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/09_question_bank.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/09_question_bank.md)。作者整理资料；许可和第三方来源范围见阅读指南。

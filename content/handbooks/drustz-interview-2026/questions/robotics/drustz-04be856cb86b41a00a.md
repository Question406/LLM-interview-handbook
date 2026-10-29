---
id: drustz-04be856cb86b41a00a
section: robotics
order: 37
level: A
title: >-
  04 · Robot 数据引擎与采集（Data Engine & Data Collection） · 8. 收尾叙事（对 Cruise
  出身面试官，英文版，60 秒）
quick: >-
  作者文档章节 · 04 · Robot 数据引擎与采集（Data Engine & Data Collection） · 8. 收尾叙事（对 Cruise
  出身面试官，英文版，60 秒）
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/04_data_engine.md
    type: primary
---
## 8. 收尾叙事（对 Cruise 出身面试官，英文版，60 秒）

> "I treat a home-robot fleet as a close cousin of an AV fleet. On-device triggers and shadow eval decide what gets uploaded. Every teleop intervention is a disengagement: it enters a triage funnel — dedup and cluster, rank by severity times frequency, attribute root cause, and use counterfactual replay or a world model to decide whether it's really a policy deficiency. Every event becomes a permanent regression test. A miner searches the fleet for lookalikes and spins up targeted collection campaigns. On the training side, mixture weights and dedup — the Re-Mix and SCIZOR playbook — control the distribution, and the budget buys environment and object diversity, not more demos in the same kitchen. On privacy I'd follow the 1X template — per-session consent, no-go zones, edge redaction, employed operators — and include the labeling supply chain in the threat model, because that's where iRobot got burned. And I'd run the whole line on demos per hour, QA yield, the coverage matrix, flywheel cycle time, and marginal success rate per hundred demos."

---

### 速记卡（面试前 5 分钟扫一眼）

- 数字：221 triggers / 10k clips 一周 auto-label / π0 = 10k h·903M steps·7 构型·68 任务 / π0.5 ~100 环境 / Helix 500 h / Figure 10→60h ⇒ 88→95% / 20–40 demos/h / $118–136 per hour / $1–10 per demo / NEO &#36;20k / Waymo 30k→60k mi/disengagement
- 词：shadow mode · trigger campaign · CLM · miner · triage funnel · severity×frequency · counterfactual replay · necessary vs unnecessary takeover · Road-to-Sim · Morpheus · Fleet Response · Content Search · farm-to-table data · social contract · no-go zones · RECAP coaching · Re-Mix · SCIZOR · coverage matrix · intervention rate · &#36; per point of success rate

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/04_data_engine.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/04_data_engine.md)。作者整理资料；许可和第三方来源范围见阅读指南。

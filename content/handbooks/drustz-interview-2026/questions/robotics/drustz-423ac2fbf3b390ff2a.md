---
id: drustz-423ac2fbf3b390ff2a
section: robotics
order: 34
level: A
title: >-
  04 · Robot 数据引擎与采集（Data Engine & Data Collection） · 5. Failure-Driven Data
  Collection（高频考点）
quick: >-
  作者文档章节 · 04 · Robot 数据引擎与采集（Data Engine & Data Collection） · 5. Failure-Driven
  Data Collection（高频考点）
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
## 5. Failure-Driven Data Collection（高频考点）

### 5.1 方法论三板斧

1. **接管即金标数据**：自主执行中人接管 = 失败标注 + 正确后续，一条数据两种信号（DAgger / HG-DAgger / Sirius 谱系；π*0.6 RECAP 的 coaching 是工业化版本）。
2. **失败 taxonomy → 定向 campaign**：按失败模式建分类（抓取滑落 / 遮挡 / 语言歧义 / 长程规划断裂），逐类下发采集任务——Tesla trigger campaign 的操作任务版。
3. **回放/世界模型前置发现失败**：1X world model 预测候选 policy 结果；Cruise Road-to-Sim 让每个事件永久成为回归场景——**失败一次，永远测试**。

### 5.2 示范回答（英文，背熟）

**Q: "Our bot has a high failure rate on one task category. How do you fix it with data?"**

> "I'd run it as a triage-then-campaign loop, borrowing directly from how AV companies handle disengagements.
>
> **First, characterize before collecting.** Pull every failure episode in that category from fleet logs, dedupe and cluster them, and rank clusters by severity times frequency. Then attribute root cause per cluster — is it perception (occlusion, novel objects), policy (grasp slip, wrong subtask), language grounding, or something upstream like calibration or a broken reset assumption? A high failure rate on one task is almost never one problem; it's usually two or three clusters, and some of them aren't data problems at all — if it's a hardware or calibration issue, no amount of demos will fix it.
>
> **Second, verify it's a policy deficiency.** Replay the failures — against the current policy and candidates — through offline eval or a world model, the way Cruise used counterfactual sim to separate necessary from unnecessary takeovers. That also gives me a frozen regression set: every one of these failures becomes a permanent test before I've collected a single new demo.
>
> **Third, targeted collection per cluster.** For each data-fixable cluster I launch a campaign: teleop demos with scripted variation concentrated on the failing conditions — the specific objects, poses, lighting, clutter — plus recovery demonstrations that start from the failure state, because the policy needs to learn to get *out* of trouble, not just avoid it. In parallel, a miner searches fleet logs for near-miss lookalikes so I'm training on the whole failure neighborhood, not just the reported cases. And every future intervention on this task is auto-tagged as gold data — DAgger-style, interventions are the cheapest high-signal data we have.
>
> **Fourth, retrain and gate on the regression set.** Fine-tune with the new data upweighted but mixed carefully so I don't regress other tasks — mixture weights are a real lever, Re-Mix showed 30-plus percent gains from reweighting alone. Ship behind the regression eval plus a shadow or world-model eval, then watch the deployed intervention rate on that category.
>
> **And the exit criterion matters:** I'd track marginal success rate per 100 added demos — Figure published exactly this curve for logistics, 10 to 60 hours took barcode scanning from 88 to 95 percent — and stop collecting when the curve flattens, because at that point the bottleneck has moved somewhere else."

追问 **"What if the failures are too rare to collect enough of?"**：
> "Then I widen the funnel three ways: mine the fleet for semantic lookalikes with embedding search, synthesize variations in sim or via world-model rollouts anchored on the real failures, and design the teleop campaign to oversample the failure's causal factors rather than replaying it literally. Rare events are exactly where the Cruise CLM lesson applies — U-turns were under 100 sightings a day across the whole fleet, and error-driven mining still fixed them."

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/04_data_engine.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/04_data_engine.md)。作者整理资料；许可和第三方来源范围见阅读指南。

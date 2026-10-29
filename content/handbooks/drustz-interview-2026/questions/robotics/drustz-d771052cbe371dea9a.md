---
id: drustz-d771052cbe371dea9a
section: robotics
order: 45
level: A
title: 05 — Debug Playbook：「The bot is not working」排查手册 · 6. 追问应对：硬件深水区 → 体面地引回强区
quick: >-
  作者文档章节 · 05 — Debug Playbook：「The bot is not working」排查手册 · 6. 追问应对：硬件深水区 →
  体面地引回强区
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/05_debug_playbook.md
    type: primary
---
## 6. 追问应对：硬件深水区 → 体面地引回强区

LLM 背景的候选人在这题上真正的风险不是"不懂电机"，而是**在不懂的地方装懂**（马上被戳穿）或**直接卡死**（显得只会软件）。正确姿势是一个三步公式：

> **Acknowledge（一句诚实）→ Reason（用第一性原理给推理层面的答案）→ Bridge（引到 telemetry/fleet 统计/data engine，在强区展开）**

诚实那句要**短且不卑微**——一句带过，不要道歉三次。Bridge 要**自然增值**，不是逃跑：你引过去的方向必须对解决当前问题真的有用。

### 场景 A：追问电机/电气细节（"How exactly would you diagnose the motor driver?"）

> "I'll be upfront: my hands-on depth is on the ML and data side, so for component-level electrical diagnosis I'd pair with the hardware team rather than pretend. But here's how I'd reason about it: I'd want commanded-versus-actual torque and velocity, motor current and temperature time series, and the driver's fault registers — because most of what looks like a 'broken motor' is visible in telemetry before you touch a screwdriver: thermal derating shows up as failures correlated with runtime and temperature, a dying driver shows up in the current signature. And that's actually where I'd add the most value: making sure **every robot ships with the telemetry that lets a hardware engineer diagnose this remotely** — per-device current-vs-velocity baselines, derating events in diagnostics, alerts when a unit deviates from its own history. That turns a field visit into a dashboard query."

### 场景 B：追问标定/运动学数学（"Walk me through the extrinsic calibration math."）

> "I know it at the level of: extrinsics are the SE(3) transform between sensor frames, drift shows up as reprojection error, and you re-estimate it from correspondences — but I haven't implemented a calibration pipeline myself, so I won't fake the details. What I *have* thought hard about is the **systems question around calibration**: how do you know, across a fleet, *which* robots have drifted, *before* their success rate drops? That's a monitoring problem — track reprojection-error-style consistency metrics online, baseline them per robot, alert on drift. There's published work on online miscalibration detection with very high accuracy. I'd rather catch drift with a fleet-wide monitor than with a technician's quarterly checkup."

### 场景 C：追问嵌入式/RTOS/CAN bus（"What would you look at on the CAN bus?"）

> "Honestly, embedded is the layer where I'd lean on teammates most — I know it at the level of: check error frame counts, bus-off events, and whether device dropouts correlate with vibration or specific poses, which is how you catch the classic loose-connector intermittent fault. What I can bring to that layer is the **statistical side**: intermittent hardware faults are brutal to catch one robot at a time, but trivial to catch in aggregate — if you log bus error counts fleet-wide, the flaky units jump out of the distribution long before anyone files a ticket. I care a lot about designing logging so that hardware engineers get that signal for free."

### 场景 D：面试官顺着 Bridge 问"那你会怎么设计 telemetry？"（这是你的主场，要能立刻接住并往深打）

准备一个 60 秒的迷你答案：

> "Three tiers. **Tier 1, always-on low-rate health**: temperatures, voltages, clock offsets, topic rates, inference p99, restart counts — cheap enough to stream continuously, baselined per device. **Tier 2, event-triggered flight recorder**: a continuous on-device ring buffer of full sensor and internal state, uploaded only around triggers — anomalies, low-confidence detections, planner interventions, human takeovers — which cuts storage by 90%+ while keeping every interesting moment replayable. **Tier 3, the change-event stream**: every OTA, config push, flag flip, and map update in one timeline, so any metric chart can be overlaid with deployment markers. Then the triage loop: auto-tag and cluster incoming events into a failure taxonomy, fix the biggest cluster first, and feed the failure data back into training and eval sets — that's the data engine."

### 通用桥接句备用（任何硬件深水区都能用）

- "That's exactly the kind of question where I'd want the answer to come from **fleet data rather than intuition** — let me describe what I'd measure."
- "I'd rather be honest that my depth there is limited — but the reason this failure class is hard is that it's **intermittent**, and intermittent problems are fundamentally a **statistics problem**, which is my home turf."
- "One robot's mystery is a fleet's histogram."（这句可以当金句收尾）

### 反面清单（不要做）

| 不要 | 因为 |
|---|---|
| 编造具体硬件参数/操作细节 | 面试官往往就是硬件出身，一戳就穿 |
| 说 "I don't know" 然后停住 | 等于放弃这道题的一半分 |
| 桥接太急（问题没答就跳走） | 显得在逃避；先给推理层面的实质内容再桥 |
| 连续道歉/过度铺垫 | 一句诚实就够，多了显得不自信 |

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/05_debug_playbook.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/05_debug_playbook.md)。作者整理资料；许可和第三方来源范围见阅读指南。

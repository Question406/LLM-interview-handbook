---
id: drustz-cf4e0d765e0767edc1
section: robotics
order: 17
level: A
title: '02 — 轮次形式与情报（The Bot Company Onsite, 13:00–17:00） · 5. 当天临场策略（13:00–17:00）'
quick: >-
  作者文档章节 · 02 — 轮次形式与情报（The Bot Company Onsite, 13:00–17:00） · 5.
  当天临场策略（13:00–17:00）
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/02_interview_rounds_intel.md
    type: primary
---
## 5. 当天临场策略（13:00–17:00）

### 5.1 时间与状态管理

| 时间 | 动作 |
|---|---|
| 11:30–12:15 | 轻午餐（蛋白质为主，避免大量碳水——14:30 血糖崩不起）。正常咖啡因剂量在 12:15 前摄入完毕，作用峰值恰好覆盖第一轮 |
| 12:15–12:45 | 最后翻阅：只看本文 TL;DR + 四段式项目卡片 + attention 默写一遍。**不看新材料**，新信息此时只会增加焦虑 |
| 12:45 | 到场/上线。带：笔记本电脑（PyTorch 环境提前验证可跑、编辑器配好）、充电器、水、能量小食（坚果/能量胶，第 2–3 轮间隙吃） |
| 13:00–14:15 | 第一轮。开场 30 秒自我介绍（见 5.2），前 5 分钟语速刻意放慢 10%——高压开局最容易语速失控 |
| 轮间隙（~5min） | 固定重置仪式：上厕所 → 喝水 → 3 次深呼吸 → 只看一眼四段式卡片。**不复盘上一轮**：单轮否决制下，复盘上一轮既无法改变结果又污染下一轮状态 |
| 14:15–15:45 | 第二轮（大概率 deep-dive）。这是权重最高的一轮，能量分配上留足 |
| 15:45 | 吃 snack。16:00 后是全天认知低谷 + founder 轮，靠这口顶住 |
| 15:50–17:00 | 第三轮。如果是 founder 轮且 20 分钟就结束——**这是好信号不是坏信号**（前面轮次已过，founder 只做确认） |

**关于「提前结束」的心理预案：** 提前结束既可能是否决也可能是提前通过，你无法从时长读出结果，所以规定自己**不解读**。每轮开始时的唯一目标：让这一轮的面试官愿意拍板要你。

**被问懵时的 3 秒话术（背下来，防大脑空白）：**

> "Good question — let me think out loud for a second."

然后从「这个问题在优化什么 / 约束是什么」开始重建。JD 要的 mental acuity 是可见的推理过程，沉默 20 秒才是真扣分。

### 5.2 每轮开场 30 秒自我介绍（英文模板）

> 与 08 §1 的分工：**首轮**用 08 §1 的 60–90 秒完整版；本节 30 秒版用于第 2/3 轮快速开场。两套都要练，别混。

**基础版（技术轮通用）——** 结构：身份一句 + 最相关经验一句 + 与岗位的钩子一句。方括号处按自己实际数字填：

> "Hi, I'm Ray. Until recently I was a member of technical staff at Reflection AI, where I worked on post-training LLMs for agentic tasks — my day-to-day was the full loop: designing data mixtures, running and debugging large-scale training experiments, and building the evals that tell us whether a change actually helped. Before that I did my PhD at the University of Washington on human-computer interaction, so I've always worked at the boundary between models and the messy real world. That's exactly why this role excites me — home robots are the hardest version of that boundary, and the bottleneck is the data and eval loop, which is where I live."

**Coding/debugging 轮变体（更短，快速进入干活状态）：**

> "Quick version: I'm Ray — I did post-training at Reflection AI, most of my time in PyTorch training loops and data pipelines, and I've debugged my share of runs that silently went wrong. Happy to dive right in."

**Founder 轮变体（使命 + agency 前置）：**

> "I'm Ray. Short version of my path: HCI PhD at UW, then post-training LLMs at Reflection AI — teaching models to act reliably, not just talk. I'm here because I think the gap between a robot demo and a robot product is a data-engine and evaluation problem, and I want to work on it in a sub-100-person team where everyone's an IC and the robot is ten feet from my desk."

**使用纪律：**
- 每轮都主动给这 30 秒，即使面试官没要——它设定你想被追问的方向（data mixture / eval / debug），把 deep-dive 引到你的主场。
- 30 秒是硬上限。练到 25 秒说完，留 5 秒缓冲。
- 三个版本各朗读 5 遍以上，做到脱稿且不背书腔。

### 5.3 一页 cheat sheet（轮间隙唯一允许看的东西）

打印或手写一张卡片，只放：
1. 四段式项目卡：failure mode / 诊断 / 改动 / 数字（每段一行关键词）。
2. 训练 debug 排查树的 5 个分支关键词。
3. Attention 一行公式 + 两个 mask。
4. Data engine 设计答案的 5 个节点：目标澄清 → 数据分层 → failure mining 闭环 → 分层 eval → trade-off。
5. Founder 轮三红线：no 管理话题 / no remote / no 跳板叙事。
6. 反问的 3 个问题。

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/02_interview_rounds_intel.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/02_interview_rounds_intel.md)。作者整理资料；许可和第三方来源范围见阅读指南。

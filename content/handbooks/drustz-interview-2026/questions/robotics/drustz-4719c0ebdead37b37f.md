---
id: drustz-4719c0ebdead37b37f
section: robotics
order: 71
level: A
title: 08 · 个人故事与提问清单（Stories & Asks） · §5 · 反问清单（按轮次分组）
quick: 作者文档章节 · 08 · 个人故事与提问清单（Stories & Asks） · §5 · 反问清单（按轮次分组）
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
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/08_stories_and_asks.md
    type: primary
---
> 下文的个人经历、时间安排与复习状态属于原作者 DrustZ；可用作组织自己材料的参考。

## §5 · 反问清单（按轮次分组）

> 原则：每个问题都要**携带信息**——让面试官意识到你已经想过这个问题的具体形态。每轮备 4 个，实际问 2–3 个。所有问题用英文原文准备。

### 轮次 1 · Practical / coding 轮（面试官大概率是 ML engineer）

| # | 问题（英文原话） | 为什么问（你的意图） |
|---|---|---|
| 1 | *"When a new policy checkpoint looks worse, what does the debugging loop look like today — replay, sim, or someone walking over to a robot? And how long is one iteration?"* | 探 eval/debug 基建成熟度；铺垫你 [05](?book=drustz-interview-2026&section=robotics&question=drustz-7452e6b3a4ec64009c) 的 cohort 切分思路 |
| 2 | *"What fraction of your failures turn out to be data problems versus model problems versus hardware? Do you have the observability to even attribute that today?"* | data-first 思维信号；attribution 正是你的 S1/S3 强项 |
| 3 | *"What's the most annoying tooling gap in your day right now?"* | IC 对 IC 的真话题；也探你入职后第一个可交付物 |
| 4 | *"How much of the training stack is shared across World Models, the foundation model, and whole-body control — one data platform or three?"* | 显示你读过他们 2026/2 的岗位拆分；探组织形态 |

### 轮次 2 · Project deep-dive 轮（面试官可能是 senior ML / research）

| # | 问题 | 意图 |
|---|---|---|
| 1 | *"You've publicly ruled out in-home teleoperation — which I think is the right call. So what does the correction signal look like at deployment: interventions by field operators, user feedback, autonomous retries? And who closes the loop on a failure clip today?"* | 全场最强一问：引用他们的公开立场 + 直击 intervention→DAgger 数据这条你最懂的线（[04](?book=drustz-interview-2026&section=robotics&question=drustz-ef21da31a0d135e774)） |
| 2 | *"How do you decide a checkpoint is good enough to OTA to the fleet? Is there an eval gate you trust, and what's its false-pass rate — has a model that passed eval ever regressed in homes?"* | eval 金字塔 + 统计功效（[06](?book=drustz-interview-2026&section=robotics&question=drustz-36784fe27814ef4267)：90% 成功率 50 trials CI ±8pp）——问完可自然接一句你对配对设计/sequential testing 的看法 |
| 3 | *"On data mixtures: as the fleet grows, how do you weigh fresh fleet data against the original demonstration corpus? Have you hit catastrophic forgetting or distribution collapse when re-training on your own deployment data?"* | mixture/curation 是你 S1 的主场；self-training feedback loop 是前沿痛点 |
| 4 | *"Is RL from real deployment experience on the roadmap, or is post-training mostly BC on curated data for now?"* | 直接对位你的 RL post-training 背景；答案决定你入职后的位置 |

### 轮次 3 · Founder / culture 轮（Kyle 或 Paril）

| # | 问题 | 意图 |
|---|---|---|
| 1 | *"You've said the team stays under a hundred people. As the fleet scales from tens to thousands of robots, which functions do you refuse to grow headcount for — and what has to become software instead?"* | 引用 Vogt 公开立场；本质在问 automation-first 文化，而「把人力变软件」正是 data engine 的核心命题 |
| 2 | *"You and Paril both watched the AV industry build data engines at enormous cost. What's the one thing from Tesla or Cruise you're deliberately *not* copying?"* | 让 founder 讲他最有观点的话题；显示你知道他们的师承（Tesla trigger/auto-label、Cruise CLM——见 [04](?book=drustz-interview-2026&section=robotics&question=drustz-ef21da31a0d135e774)） |
| 3 | *"For the first tasks — the 90-to-99-percent-tolerance ones — what's the metric that tells you a task is ready to ship to real customers? Success rate alone, or something closer to 'user never had to think about it'?"* | product cadence + 你的 HCI 视角：shipping bar 是行为指标不是模型指标 |
| 4 | *"What does the company look like in twelve months if everything goes right — and what's the single riskiest assumption between here and there?"* | 经典但有效的 founder 收尾；听 risk 排序（data? hardware? cost?），你可当场接上自己对口的那条 |

### ⚠️ 不要问 / 不要提

| 雷 | 原因 |
|---|---|
| Airbnb 诉讼、合同工集体诉讼 | 你知道 ≠ 该在面试提；负面法务话题零收益 |
| "机器人到底长什么样？能给我看看吗？" | Stealth 公司，逼问产品形态显得不懂规矩（他们主动展示当然最好） |
| Remote / hybrid 可能性 | 全员 SF onsite 是明牌，问了 = 没做功课或意愿存疑 |
| 融资/估值细节 | 全是公开信息，问了浪费反问额度 |
| Reflection 内部细节被反问时 | 主动说保密边界（§3 开头那句），透露反而减分——面试官也在测你会不会将来泄他们的密 |

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/08_stories_and_asks.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/08_stories_and_asks.md)。作者整理资料；许可和第三方来源范围见阅读指南。

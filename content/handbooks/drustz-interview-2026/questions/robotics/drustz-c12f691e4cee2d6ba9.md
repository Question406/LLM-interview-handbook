---
id: drustz-c12f691e4cee2d6ba9
section: robotics
order: 70
level: A
title: >-
  08 · 个人故事与提问清单（Stories & Asks） · §4 · 弱点预案："You have no robotics / hardware
  experience"
quick: >-
  作者文档章节 · 08 · 个人故事与提问清单（Stories & Asks） · §4 · 弱点预案："You have no robotics /
  hardware experience"
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

## §4 · 弱点预案："You have no robotics / hardware experience"

> 一定会被问（可能以更委婉的形式：*"What would be hardest for you here?"*）。原则：**先承认，再精确切分缺什么/不缺什么，给两个「缺口会快速闭合」的证据，落在 day-one 贡献上。** 不辩解，不说 "robotics is just software"。

**主答（~60 秒）：**

> You're right — I haven't shipped a robot, and I won't pretend otherwise. Let me be precise about what's missing and what isn't.
>
> What isn't missing: the training loop. Robot learning has converged on the LLM recipe — a VLM backbone, behavior cloning as SFT, RL on top, data mixtures as the main lever, and evaluation as the open problem. I've owned that exact loop in production, including the failure modes: reward curves that flatten because of difficulty distribution, metrics that lie, preference data that's secretly noise.
>
> What is missing: physical intuition — contact dynamics, controls, sim-to-real, how hardware fails. Two reasons I believe that gap closes fast. First, I've closed a similar one before: at Meta Reality Labs I worked one layer above raw EMG sensors — noisy, drifting, person-dependent signals with millisecond latency budgets. Not robotics, but the same discipline. Second, my ramp-up pattern: [填入你最快上手新领域的一个实例，如「x 周内在陌生领域交付了 y」——可用 Exa work trial：两天在多查询向量检索命题下交付可复跑实验]。
>
> And frankly — your bet is end-to-end networks eating near-raw sensor data, which moves the leverage *away* from hand-engineered robotics and *toward* data and post-training. That's where I contribute from day one, while I learn the physical stack from people ten feet away from the robot.

**追问预案：**

| 追问 | 要点 |
|---|---|
| "What's the hardest thing you'll have to learn?" | 诚实指名：real-time control loop 的思维方式（50Hz、action chunking、延迟即正确性的一部分）——但指出你在 EMG 实时decoding里碰过它的边（latency budget 决定架构）。别答 "nothing much" |
| "How would you spend your first 30 days?" | ① 跟一台机器人 + 采数据的 operator 轮几个班（数据是怎么长出来的）；② 跑通现有训练→eval→部署一整圈，不改任何东西；③ 挑一个 eval 或 data-curation 的小痛点做出第一个可合入的改进 |
| "sim-to-real 你懂多少？" | 不装深：知道 domain randomization / 知道 sim 是高功效回归 gate 而真机是终审（引 [06](?book=drustz-interview-2026&section=robotics&question=drustz-36784fe27814ef4267) 的 eval 金字塔思路）；说明你会先把 sim-vs-real 的评估相关性当数据问题来量化——这是你的母语 |
| "我们招过 pure-ML 背景的人失败了，为什么你不会？" | 差异点不在 ML 强弱，在于你的专长恰好是他们卡住的两件事（data engine、eval），且你有跨域重启的前科（HCI→wearable→LLM，每次都到了能发表/上产品的深度） |

---

---

来源：[DrustZ / Mingrui Zhang · ml_sys_prep/bot_company/08_stories_and_asks.md](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/ml_sys_prep/bot_company/08_stories_and_asks.md)。作者整理资料；许可和第三方来源范围见阅读指南。

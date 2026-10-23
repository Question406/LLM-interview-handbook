---
id: dt-case-map
section: cases
order: 1
level: S
title: 准备三个案例，回答大部分「什么是好数据」类问题
quick: "准备一个自己的案例和两个公开研究案例。被问到「什么是好数据」这种抽象问题时，先用一句话回答，再说「拿我做过的 X 举例」，讲其中最相关的那一步。"
companies:
  - apple
tags:
  - Apple
  - 备考地图
  - Data Story
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Terminal-Bench: Benchmarking Agents on Hard, Realistic Tasks in Command Line Interfaces"
    url: https://arxiv.org/abs/2601.11868
    type: primary
  - title: "ToolRL: Reward is All Tool Learning Needs"
    url: https://arxiv.org/abs/2504.13958
    type: primary
  - title: "Learning by Distilling Context"
    url: https://arxiv.org/abs/2209.15189
    type: primary
---

「什么是好数据」「你怎么判断一批数据有没有用」，这类问题只给定义会显得很空。我的办法是准备三个案例，先一句话回答，再说「拿我做过的 X 举例」，只讲最相关的那一步。

自己的案例最有说服力，因为能讲当时是怎么判断的、哪里做错了。公开案例用来说明你的判断和领域里的结论一致，报一两个数字就够了，比如「Endless Terminals 在自己的开发集上把 7B 模型从 10.7% 训到 53.3%，Terminal-Bench 只从 2.2% 到 3.4%」。

| 案例 | 讲什么 | 适合回答 |
| --- | --- | --- |
| 自己的实习：网页设计能力（`dt-case-web-diagnose` → `dt-case-web-skill` → `dt-case-web-internalize` → `dt-case-web-grounding`） | 诊断缺口 → test-time skill → rejection sampling、SFT、RL 训进模型 → 修数字幻觉 | 数据故事、哪些样本值得留、合成数据怎么验证、能力什么时候该训进权重、hallucination penalty 怎么设计 |
| Terminal-Bench 爬坡（`dt-case-tbench-climb`） | Endless Terminals、TMax、River、Terminal-Universe 四种环境数据 | 开发集涨、公开评测不动；难度带；verifier 质量比数量重要 |
| 工具调用 RL（`dt-case-toolcall-rl`） | ToolRL 的奖励拆分，Kimi K2 的工具合成 | 奖励粒度、长度奖励的副作用、模拟环境和 judge 的偏差 |

## 题目怎么对上案例

- **什么是好数据、多和好哪个重要**（`dt-good-data-def`、`dt-more-vs-better`）：讲 River 只用三成环境、滤掉坏 verifier 后增益更大；再讲你的 rejection sampling 里，「只有带 skill 才过」的那批样本为什么最值钱。
- **讲一个数据解锁能力的故事**（`dt-data-story`）：整条网页设计线。
- **讲一次失败的数据下注**（`dt-failed-data-bet`）：网页案例里风格单一的那版 SFT 数据，或者视觉 judge 被钻空子的那一轮。
- **合成数据怎么验证**（`dt-synth-reasoning`、`dt-when-not-synth`）：网页的渲染、功能、视觉三道检查；Kimi K2 的 rubric judge。
- **幻觉和 grounding**（`dt-grounding-data`、`dt-honest-fluent`）：网页里「数字加 reference」的回查和覆盖率。
- **Agent RL 环境怎么做**（`dt-agent-env-is-data`、`dt-agent-tmax-synth`）：Terminal-Bench 案例。
- **奖励怎么写、怎么防 hack**（`dt-agent-reward-spec`、`dt-length-hack-data`）：ToolRL 的奖励拆分和长度奖励实验；网页 RL 里视觉分推着模型编数字。

## 追问

**自己的数字不能说怎么办？**
说方向和相对量，比如「加了 skill，checklist 通过率涨了一截，拿掉又掉回去」，再说明数字受保密限制。指标怎么定义、对照怎么做，这些都可以讲清楚。

**面试官没听过某篇论文？**
一句话说清它做了什么、结论是什么，然后回到你自己的判断上，不用展开。

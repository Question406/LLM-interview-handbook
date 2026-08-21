---
id: baichuan-agent-online-eval-adoption
section: agent
order: 114
level: A
title: 百川智能：Agent 上线后如何评估，使用量应怎样解读？
quick: >-
  将线上评估拆成用户价值、任务可靠性、成本/性能和风险：按 cohort 测 task success、用户接受/改写、留存、
  tool error、latency、token 与安全事件。使用量只是一项 adoption 信号，必须与分母、任务结构和实验组比较，不能把请求数当效果。
tags:
  - Baichuan
  - Agent Evaluation
  - Online Metrics
  - Product Analytics
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: 百川智能大模型实习一面 压力好大（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/e3e6543bd5ab478292b74a48f031c530
    type: candidate-first-hand
---
## 真题记录

- 公司：百川智能
- 团队 / 岗位：大模型实习；具体团队原帖未披露
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-02-12
- 来源类型与可信度：牛客候选人原帖，B（公司、实习性质、轮次与发帖时间明确，届别和面试日期未披露）
- 原始措辞：**“上线了吗 线上如何评估 使用量是多少”**

原帖把「上线了吗 / 怎么评估 / 使用量」连在一起。实习一面不要编一个 DAU 数字，也别把 QPS 当效果。先定义任务契约，再拆价值、可靠性、成本、风险；使用量只在有分母和对照时才可解读。维度可对照 `kuaishou-agent-eval-dims`、`jd-agent-eval-beyond-qa`、`xiaohongshu-agent-business-eval`。

## 线上评什么

上线前定义一次任务的开始、成功、部分成功、放弃和人工接管，trace 可回放。主指标贴近用户价值：完成率、接受后未改写比例、节省时长、复用和留存。同时按任务类型看 tool success、重试、幻觉/违规、p50/p95、tokens 和成本。高风险业务要抽样人工审计和 kill switch。离线集过了不等于线上好：分布、工具失败、用户改写都会制造 gap，见 `arl-eval`。

## 使用量怎么读

至少区分 UV、激活率、任务数/活跃用户、完成任务数、留存和调用深度，并按新老用户、入口、权限、场景分 cohort。请求数上升可能来自失败重试或机器人，不能代表产品更好。没有分母的「用了很多」无法回答这题。对重要变更用 A/B 或逐步 rollout 对照基线，结合反馈与 failure bucket，才能把用量变化归因到能力而不是季节性或渠道。原帖问「使用量是多少」时，应说明：没有公开数字，我会报完成任务数和 cohort 留存，而不是原始调用次数。

## 追问

- **为什么不把 token 当主指标？** Token 是成本。主指标应是用户价值；成本和延迟是约束，避免选出又贵又慢的「成功」。
- **失败重试会不会把用量做高？** 会。所以要同时看任务成功和每任务调用次数。用量单独涨是告警不是庆功。
- **离线指标很好但没人用？** 查入口、权限、延迟、以及任务定义是否和真实需求一致。Adoption 和 capability 要分开看。
- **如何快速回滚？** 按失败桶和安全事件设闸门；用量暴涨但完成率掉、违规升，应 kill switch 而不是继续放量。

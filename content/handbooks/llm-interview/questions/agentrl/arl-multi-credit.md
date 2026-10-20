---
id: arl-multi-credit
section: agentrl
order: 8
level: S
title: Multi-Agent RL 的 Credit Assignment 为什么更难？
quick: "团队最终奖励同时取决于主控如何拆分任务、各执行 Agent 的表现，以及它们如何共享信息。所有 Agent 同时更新时，每个 Agent 面对的其他成员也在变化，因此更难识别各自的贡献。"
tags:
  - Multi-Agent RL
  - Credit Assignment
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ Kimi K2.5
    url: 'https://arxiv.org/abs/2602.02276'
    type: legacy-reference
---

常见误区是：给整队同一个 $+1$，让没有实际贡献的 worker 也得到强化。单 Agent 已经难把终局 $0/1$ 分到几十步工具调用；多 Agent 还要在人之间分。Team 奖励分数（reward） 同时取决于 orchestrator 的拆分、worker 的执行和他们传的信息。所有人一起更新，别人变成非平稳环境，「谁贡献了多少」更糊。单 Agent 的 credit 是时间维；本题多的是人和通信维（对照 `arl-credit`）。

## 共享回报为什么糊

设 A 调度 B/C/D，成功 $R=1$。Credit 可能来自 A 拆对了、B 找到关键证据、C 写对代码，D 几乎没干活。把同一个标量奖励分配给所有 token，梯度分不清。通信是自然语言，动作空间巨大，counterfactual（「若 D 不说话会怎样」）几乎不可精确算。同时更新时，A 学到的是「旧 B」，B 已变，信用估计持续过期。多智能体论文里的非平稳，在 LLM 编排里更具体：提示格式一变，工人行为就变，orchestrator 的「好拆分」立刻过时。

## Difference reward 与中心 Critic：有用，但有坑

冻 worker 只训 orchestrator：把工人当环境能力，credit 简单，但执行 Agent 的能力不会随训练提升，A 还可能 overfit 固定行为，换人就 shift。交替训练：分阶段更新，减非平稳，仍要防止一侧过拟合另一侧的瞬时策略。

Difference reward / counterfactual baseline（COMA 一类）用「队回报减去没有该 Agent 时的基线」估边际贡献，理论干净；LLM 上要用中心模型滚或学一个 $Q$，文本通信下贵，且基线本身偏。中心 Critic 见全局轨迹，方差更小，但把信息集中化：部署若是分布式、Critic 见不到真实全局，训练/部署不一致；Critic 也容易 hack 到「看起来像协作」的假通信。局部 验证器（verifier）（子任务单测、artifact 质量、下游是否被采用）能增加信号密度，必须对齐 team 目标，否则工人刷局部分、伤害全局。

工程上先能冻结或交替，再谈精巧的差分奖励；上来就上中心 Critic 而不报训练/部署信息差，面试里要追问。

实践顺序：先能复现单 Agent credit，再上「冻一侧」的编排实验，最后才上差分奖励或中心 Critic。每加一层都要报：换工人后是否掉点、局部奖励是否和团队成功相关、通信是否变成空洞客套。引用多智能体方法时，应说明适用条件和局限，不要只列 COMA/QMIX 等缩写。局部奖励必须对齐团队成功；通信变成空洞客套也是 hack，Critic 会当成协作。

## 追问

- **冻 workers 的缺点？** 执行 Agent 的能力不会提升，orchestrator 过拟合固定行为；换 worker 或换提示格式即分布偏移。适合先把调度学稳，不适合当终态。
- **如何给 individual reward？** 按子任务 verifier、产物质量、下游是否被采用打局部分。必须抽检局部指标与 team 成功的相关，防止刷局部分、伤害全局。
- **和单 Agent credit？** 单 Agent 是时间维上的稀疏回报；本题多人和通信维，还有同时更新造成的非平稳。见 `arl-credit`。先能做一侧冻结，再谈差分奖励。
- **中心 Critic 部署时见不到全局怎么办？** 训练/部署信息差会让价值函数失效。要么部署也汇聚轨迹，要么别把中心 Critic 当上线组件，只当离线方差减工具。

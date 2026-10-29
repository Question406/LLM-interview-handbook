---
id: arl-multi-credit
section: agentrl
order: 8
level: S
title: Multi-Agent RL 的 Credit Assignment 为什么更难？
quick: "团队最终奖励同时取决于主控怎么拆任务、各执行 Agent 做得怎样、它们之间传了什么信息；所有 Agent 同时更新时，每个人面对的队友也在变，更难认出各自的贡献。实践上先冻结一侧或交替训练，再考虑差分奖励或中心 Critic。"
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

因为团队的最终奖励同时取决于 orchestrator 怎么拆任务、各个 worker 执行得怎么样、它们之间传了什么信息，而且所有 Agent 同时在更新，每个人面对的队友都在变。单 Agent 要把终局 $0/1$ 分到几十步工具调用上，这是时间维；多 Agent 还多了人和通信这两维，对照 `arl-credit`。

举个例子：设 A 调度 B、C、D，任务成功，$R=1$。功劳可能来自 A 拆对了、B 找到了关键证据、C 写对了代码，而 D 几乎没干活。给整队同一个 $+1$，D 也被强化了，把同一个标量奖励分配给所有 token，梯度分不清谁该得多少。

## 共享回报为什么糊

通信是自然语言，动作空间巨大，「如果 D 不说话会怎样」这种 counterfactual 几乎没法精确算。同时更新时，A 学到的是「旧 B」，可 B 已经变了，信用估计一直在过期。多智能体论文里讲的非平稳，在 LLM 编排里更具体：提示格式一变，工人行为就变，orchestrator 学到的「好拆分」马上过时。

## Difference reward 与中心 Critic：有用，但有坑

工程上先做冻结或交替。冻住 worker 只训 orchestrator，相当于把工人当成环境能力，credit 很简单，但执行 Agent 的能力不会随训练提升，A 还可能 overfit 固定行为，换人就 shift。交替训练是分阶段更新，能减轻非平稳，但也要防一侧 overfitting 另一侧的瞬时策略。

更精巧的方法有两类。Difference reward 或 counterfactual baseline（COMA 一类）用「队伍回报减去没有这个 Agent 时的基线」估边际贡献，理论上很干净；在 LLM 上却要用中心模型去滚，或者学一个 $Q$，文本通信下很贵，基线本身也有偏。中心 Critic 看得到全局轨迹，方差更小，但信息被集中了：部署要是分布式的，Critic 看不到真实全局，训练和部署就不一致；Critic 也容易被 hack 到「看起来像协作」的假通信上。局部验证器（verifier），比如子任务单测、artifact 质量、下游有没有采用，能加密信号，但要和 team 目标对齐，否则工人刷局部分、伤害全局。上来就用中心 Critic、又不报训练和部署之间的信息差，面试官大概率会追问。

我的实践顺序是：先能复现单 Agent 的 credit，再做「冻一侧」的编排实验，最后才上差分奖励或中心 Critic。每加一层都报三件事：换工人后掉不掉点、局部奖励和团队成功是否相关、通信有没有变成空洞客套。空洞客套也是一种 hack，Critic 会把它当成协作。引用多智能体方法时，要说明适用条件和局限，光列 COMA/QMIX 这些缩写不够。

## 追问

**冻住 workers 有什么缺点？**
执行 Agent 的能力不会提升，orchestrator 会 overfitting 固定行为，换 worker 或换提示格式就是分布偏移。适合先把调度学稳，不适合当终态。

**怎么给单个 Agent 发奖励？**
按子任务 verifier、产物质量、下游是否被采用打局部分，并且抽检局部指标和团队成功的相关性，防止刷局部分、伤害全局。

**中心 Critic 部署时看不到全局怎么办？**
训练和部署的信息差会让 value function 失效。要么部署时也汇聚轨迹，要么别把中心 Critic 当上线组件，只拿它当离线的 variance reduction 工具。

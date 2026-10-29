---
id: afm-ref-joint-tool-rl
section: projects
order: 4
level: S
title: 个人 Reference 4：Joint Agent–Speculator RL，预测正确是否就是好奖励？
quick: >-
  下一次 tool calls 是一个具体例子：从 agent 自己的 trajectories
  里提取目标，但预测对了它要做什么，还要再检查它做的是不是对的。
companies:
  - apple
tags:
  - Apple
  - 个人研究 Reference
  - Jiabao Ji
  - AFM 2026-10-27
  - 口述版
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: Speculate While You Reason — v1
    url: 'https://arxiv.org/html/2607.25816v1'
    type: primary
  - title: tau-bench — original benchmark
    url: 'https://arxiv.org/abs/2406.12045'
    type: primary
  - title: tau2-bench — dual-control environment
    url: 'https://arxiv.org/abs/2506.07982'
    type: primary
---

## 面试官可能这样问

模型怎么用自己的 rollout 产生有用的训练信号？

## 可以这样回答

一个具体例子是我们做的下一次 tool calls 预测。agent 运行以后，会留下“在这段历史之后，它实际调用了什么工具”的记录。这些记录可以拿来训练预测器，而且比一个完全不同的模型生成的 trajectories，更接近当前 agent 的行为。

但我会特别注意，预测正确和任务正确不是一回事。假如 agent 本来就要调用一个错误工具，预测器猜中了，也不代表用户的任务完成得更好。所以我会同时看调用预测和最后的任务结果。

另一个问题是策略会变。训练了几轮以后，它的调用方式可能已经不同了，旧 trajectories 就没那么合适。我会保留 trajectories 对应的模型版本，并检查新策略上的表现。至于是否真的节省时间，还得算上预测开销和白做的调用，不能只拿命中率来推断。

## 被追问时再展开

**可以提前执行所有预测的工具吗？** 不能一概而论。只读查询和会创建订单、改文件的调用风险不同；写操作需要单独的执行条件和权限判断。

## 技术备查

## 已核对的相关研究
[Speculate While You Reason](https://arxiv.org/html/2607.25816v1) 从 agent 自身 rollout 提取下一 tool calls 目标，并进行双模式联合训练。公开实验覆盖 HotpotQA、MuSiQue、BrowseComp-Plus 及 tau-bench Airline/Retail。面试先核对你实际负责的训练、系统或评测部分。

[原始 tau-bench](https://arxiv.org/abs/2406.12045) 比较对话后的数据库目标状态，并讨论重复运行可靠性；[tau2-bench](https://arxiv.org/abs/2506.07982) 加入用户也能改变共享环境的双控制场景，适合做后续扩展，不能自动说是你已跑过的新域。$\mathrm{pass}^{k}$ 强调多次都可靠，和代码领域“至少一次成功”的 pass@k 含义不同。

## 最好聊的 setting（建议扩展）
每条样本是部分 trajectoriesh、后续实际调用 a、工具 schema 及环境快照。数据必须来自相应策略版本；只有 prefix 可供预测，未来 tool 结果不能进输入。policy update 后目标分布改变，记录生成 checkpoint，避免新策略训练只拟合过期目标。

分别评 exact-call match、任务成功、净 wall-clock、浪费调用和副作用。命中一个错误 agent 调用仍可能得到预测奖励；因此命中率不能替代任务质量。净收益约等于可隐藏的等待时间减去预测、误执行与取消成本，只有受控端到端测量才能给结论。

额外实验先限于只读且结果可缓存的工具；写操作预测可保留为候选，不默认预执行。比较固定外部预测器、同模型零样本、SFT、联合 RL；固定总预算并做新工具/参数域迁移，排查模型仅学 schema 字符串。不要将 tool calls 投机与 token-level speculative decoding 的分布保持证明混为一谈。

## 英文60秒参考
> In joint agent–speculator work, we use an agent's own trajectories to create supervision for predicting its next tool call. This is a concrete example of policy-dependent training data. For the broader data strategy, I would track policy versions and evaluate both prediction quality and downstream task success. Matching the agent is only a proxy: the agent itself may be wrong. I would also measure net latency and wasted calls, and treat speculative execution of state-changing tools as a separate safety constraint.

## 高频追问与回答方向
**反馈来自自己，为什么能变好？** 自身 rollout 提供分布匹配的监督目标，是否改进需要外部任务信号和独立评价；自我重复不是新增真值。
**只优化 Hit@1会怎样？** 可能偏向容易预测而无用的调用，需要任务约束及无进展调用审计。
**为什么不全部离线 DPO？** 取决于新策略候选覆盖、可验证反馈和探索需要，不是 DPO 天然不能做工具任务。

继续练 `dt-stale-rollout-incident`、`afm-rm-dpo-reference-shift`、`apple-spec-edge`。


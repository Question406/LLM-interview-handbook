---
id: ali-credit-token
section: alibaba
order: 7
level: S
title: 序列级最终奖励，在 GRPO 里如何分配到每个 token？
quick: >-
  最常见是把序列 advantage 广播到所有生成 token；更细可做 step/action 边界对齐、过程奖励或
  critic。粗广播能训但方差大，关键错误步与废话会被同等强化。
tags:
  - Alibaba
  - GRPO
  - Credit
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 阿里国际大模型算法一面
    url: 'https://www.nowcoder.com/feed/main/detail/27a27fc44b8a4613ae790ba27add8850'
    type: legacy-reference
  - title: ↗ 淘天 Agent 社招一面
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
---

错法：「GRPO 已经做了 credit assignment」。组内标准化只解决同题多条回复谁更好，不解决一条回复里哪个 token 有功。阿里国际算法面常追到这里：序列级 $R$ 怎么落到 token。最常见实现是把序列 advantage 广播到所有生成 token；粗广播能训，但关键错误步与废话会被同等强化。组内 $A$ 的算法见 `ali-grpo-advantage`，loss 见 `ali-grpo-loss`。

## 默认：整段共享同一个 $A$

同一 prompt 采 $G$ 条，$r_i$ 标准化得 $\hat{A}_i$，再对 $o_i$ 里每个生成 token 用同一个 $\hat{A}_i$ 乘重要性比。短 reasoning（数学填最终答案）还说得通：outcome 在 EOS 才出现，内部 token 本来共享同一个 $G$。长 CoT 或 Agent 轨迹上，正确前缀 + 最后一步写错，整段一起被罚；废话灌水若碰巧答对，灌水 token 也被强化。这是方差来源，不是实现 bug。

## 更细：按动作边界切，不要均匀刷 Thought

Agent 多工具调用时，按 tool-call / turn 切段，只在 decision token 上优化（选 tool、填参），观察回填和格式性 token 可 mask。中间步骤可打分时上过程奖励/校验器，得到 denser signal，再收成标量进 GRPO，或按段给不同 $A$。需要逐步 $V$ 时才引入 critic/TD。GRPO 常刻意避免这一点。长 horizon 只靠最终成功往往不够，见 `ali-agent-final-reward`。回答模板：先承认默认广播的局限，再说任务长度与是否有 verifier，再给出可落地的更细 credit。

## 别把广播和 length bias 混在一起

有的实现对 loss 再除以序列长度，长回复的每 token 梯度被稀释；有的不除，长回复总梯度更大。这会改变「废话是否被同等强化」的程度，但仍然不是逐步 credit：它只是另一把全局标尺。Dr.GRPO 一类工作指出长度归一和组内 $\sigma$ 会偏置题目权重，面试能点到「广播不等于逐步归因，归一化还会改题间权重」即可，不必背实现细节。

淘天 Agent 面把这题和最终奖励连着问：数学题广播还能训，是因为对错发生在整条推理；退货链路对错发生在「选 tool / 填参」那几步。回答结构保持：默认广播 → 任务是否有 verifier → 动作边界或过程分。不要一上来就画 GAE，除非环境真有逐步 $r_t$。

## 追问

- **Agent 多轮工具调用还有什么挑战？** 状态非平稳、工具失败重试、部分可观测、长 horizon credit、环境 reset/幂等。只靠 final success 往往不够。
- **只优化最后几个 token 行不行？** 答案 token 可以，但推理链上的关键错误会失去梯度；除非有过程分标出错误步。
- **和 PPO+GAE 比？** GAE 需要逐步 $r_t$ 或 $V(s)$。多数 LLM outcome 任务没有逐步奖励，广播是工程默认，不是理论最优。

---
id: ali-credit-token
section: posttrain
order: 7
level: S
title: 序列级最终奖励，在 GRPO 里如何分配到每个 token？
quick: "默认是整条回答的所有生成 token 共用同一个优势，能训，但方差大，也分不出关键步骤和无关输出。要更细，就按工具调用或轮次这类动作边界切段，用过程奖励或校验器打分，需要逐步价值时再引入价值评估模型（critic）。"
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

最常见的实现是把序列 advantage 广播到这条回答的所有生成 token，大家共用同一个 $\hat{A}_i$。这样能训，但关键的错误步和废话会被同等强化。要更细，就按 tool-call / turn 这类动作边界切段，或者上过程奖励 / 校验器，需要逐步 $V$ 时才引入 critic。

常有人说「GRPO 已经做了 credit assignment」。组内标准化解决的是同一道题的几条回复谁更好，解决不了一条回复里哪个 token 有贡献。阿里国际算法面常追到这一步：序列级 $R$ 怎么落到 token。组内 $A$ 怎么算见 `ali-grpo-advantage`，损失（loss）见 `ali-grpo-loss`。

先说默认做法。同一输入提示采 $G$ 条，$r_i$ 标准化得到 $\hat{A}_i$，再对 $o_i$ 里每个生成 token 用同一个 $\hat{A}_i$ 乘重要性比。短 reasoning 还说得通，比如数学只填最终答案，outcome 在 EOS 才出现，内部 token 本来就共享同一个 $G$。到了长思维链（CoT，即分步推理过程）或 Agent 轨迹上就有问题：前缀都对、最后一步写错，整段一起被罚；灌了一堆废话碰巧答对，灌水的 token 也被强化。这是方差的来源，算不上实现 bug。

淘天 Agent 面把这题和最终奖励连着问。数学题广播还能训，因为对错发生在整条推理上；退货链路的对错发生在「选 tool / 填参」那几步。所以 Agent 多工具调用时，按 tool-call / turn 切段，只在 decision token 上优化（选 tool、填参），观察回填和格式性的 token 可以 mask。中间步骤能打分时上过程奖励 / 校验器，信号更密，再收成标量进 GRPO，或者按段给不同的 $A$。需要逐步 $V$ 时才引入 critic / TD，而 GRPO 常常就是刻意避开这一点。长 horizon 只靠最终成功往往不够，见 `ali-agent-final-reward`。别一上来就画 GAE，除非环境真有逐步的 $r_t$。

还有一件事别和广播混在一起，就是 length bias。有的实现对 loss 再除以序列长度，长回复每个 token 的梯度被稀释；有的不除，长回复总梯度更大。这会改变废话被强化的程度，但它只是另一把全局标尺，仍然不是逐步 credit。Dr.GRPO 一类工作指出长度归一和组内 $\sigma$ 会偏置题目权重，面试能点到「广播不等于逐步归因，归一化还会改题间权重」就够了，实现细节不用背。

所以回答的顺序是：先承认默认广播的局限，再看任务长度、有没有验证器（verifier），最后给出能落地的更细 credit，也就是动作边界或过程分。

## 追问

**Agent 多轮工具调用还有什么挑战？**
状态非平稳、工具失败重试、部分可观测、长 horizon 的 credit、环境 reset / 幂等。只靠 final success 往往不够。

**只优化最后几个 token 行不行？**
答案 token 可以，但推理链上的关键错误会失去梯度，除非有过程分把错误步标出来。

**和 PPO+GAE 比呢？**
GAE 需要逐步的 $r_t$ 或 $V(s)$。多数 LLM outcome 任务没有逐步奖励，广播是工程上的默认做法，不是理论最优。

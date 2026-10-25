---
id: ali-agent-final-reward
section: agentrl
order: 23
level: S
title: Agent RL 只靠最终结果奖励够不够？多步工具轨迹如何 credit？
quick: "长轨迹只靠最终奖励通常不够：同一个 0/1 乘到每一步，错参和正确前缀会被一起奖励或惩罚。我会加可自动校验的过程分，按 tool-call 边界切段优化关键决策，并把能恢复的失败和不可逆失败分开处理。两三步的短任务可以先只用最终成功。"
tags:
  - Alibaba
  - Agent RL
  - Credit
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 淘天 Agent 社招一面
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
---

长轨迹通常不够。两三步、对错一眼能看的短任务，可以先只用最终成功；步数一多、又有不可逆动作，纯最终奖励几乎学不动。我会加可自动校验的过程奖励，按 tool-call 边界切段优化关键决策，并把能恢复的失败和不可逆失败分开处理。

举个退货 Agent 的例子：先查单、再选原因码、最后提交。只在退货成功时给 $r=1$，中间原因码填错了、客服后台碰巧放过，这个错参也会被当成正确策略强化；反过来，前面查单完全正确、最后提交失败，正确的前缀也一起挨罚。

## 为什么最终奖励会糊

设轨迹 $H=(a_1,\ldots,a_T)$，只有 $R(H)\in\{0,1\}$。策略梯度把同一个 $R$ 乘到所有 $\nabla\log\pi(a_t)$ 上，$T$ 越大，信噪比越差。淘天社招面这题关心的就是这个：把 GRPO 的序列广播搬到多步工具 Agent 上，终点 $r=1$ 均匀刷到每一句 Thought 和每一次 tool-call，方差大，学不会「哪一步选对了工具」。数学题的思维链（CoT）至少还有整条推理对错的弱对齐；工具链里的对错发生在决策边界上，也就是选哪个 tool、填什么参，和每个 token 关系不大。序列级广播的细节见 `ali-credit-token`。

## 过程分要能自动判定

我只用能自动判的过程奖励：参数过不过 schema 校验、订单号存不存在、原因码属不属于枚举、单元测试或校验器过不过。让另一个模型空口夸「这步想得对」我不用，那是把 judge 的幻觉写进 reward，很容易被 hack，见 `ali-reward-hacking`。回到退货的例子，就是给「订单号填对」「原因码属于枚举」过程分，对「提交退款」单独加约束。整体的组合是任务成功加成本 / 步数惩罚、关键 tool 参数的过程分、对 irreversible action 单独约束，评测集里还要区分「偶然成功」和「稳健策略」。Function Calling 的过程奖励设计可以对照 `ali-function-call-grpo-process-reward`。

轨迹内部的 credit 按 tool-call / turn 切段，只在 decision token 上优化，别把最终 $r$ 均匀广播到每一句 Thought。超时重试这种可恢复失败和不可逆失败不给同一个负分。环境有逐步奖励时 n-step / GAE 有用，但多数电商 Agent 没有逐步 $r_t$，更现实的是动作边界对齐加稀疏过程分。多 Agent 还要在人之间分 credit，更难，见 `arl-multi-credit`。没有自动校验器的话，先用示范轨迹做监督微调（SFT），别拿另一个 LLM 空口当过程奖励。

## 追问

**过程奖励会不会让模型刷步数？**
会。多调用就加分，会鼓励无效的工具调用。过程分要对应「关键约束满足」，多余的调用给成本惩罚。

**没有校验器怎么办？**
先别上强化学习（RL）。用 SFT 示范轨迹加沙盒成功率，没有自动判定就没有稳定的梯度。

**和 GRPO 组内优势怎么叠？**
分两层。先把一条轨迹收成标量 $R$：最终成功加过程分，减步数 / 成本，减越权罚；再在同一输入提示的 $G$ 条轨迹上算组内 $A$。过程分加密的是轨迹之间的可分性，能减少空组；切段优化的是轨迹内部的归因。别在 token 上再叠一套互相打架的 $A$，两层同时乱加权，梯度会打架。

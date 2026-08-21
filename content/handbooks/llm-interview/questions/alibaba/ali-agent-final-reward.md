---
id: ali-agent-final-reward
section: alibaba
order: 23
level: S
title: Agent RL 只靠最终结果奖励够不够？多步工具轨迹如何 credit？
quick: 经常不够。长 horizon 下要过程奖励、关键决策步加权、失败可恢复轨迹，或 action-level 优化，否则成功归因模糊。
tags:
  - Alibaba
  - Agent RL
  - Credit
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-19
sources:
  - title: ↗ 淘天 Agent 社招一面
    url: 'https://www.nowcoder.com/feed/main/detail/90afe4cd751f4bd38b1e48bcec35263f'
    type: legacy-reference
---

陷阱是把 GRPO 的序列广播直接搬到多步工具 Agent：终点 $r=1$ 均匀刷到每一句 Thought 和每一次 tool-call，方差大，学不会「哪一步选对了工具」。淘天社招面原题方向就是 final reward 广播糊。短任务（两三步、对错一眼能看）可以先只用最终成功；步数多、有不可逆动作时，纯最终奖励几乎学不动。

## 为什么最终奖励会糊

设轨迹 $H=(a_1,\ldots,a_T)$，只有 $R(H)\in\{0,1\}$。策略梯度把同一个 $R$ 乘到所有 $\nabla\log\pi(a_t)$。中间填错原因码但客服后台碰巧通过，错参也被强化；前面查单完全正确、最后提交失败，正确前缀也被惩罚。$T$ 越大，信噪比越差。这和数学题 CoT 不同：数学 outcome 至少还有「整条推理对/错」的弱对齐；工具链里对错发生在 **决策边界**（选哪个 tool、填什么参），不是每个 token。序列级广播的细节见 `ali-credit-token`。

## 过程分必须可自动判定

可用的过程奖励：参数是否过 schema、订单号是否存在、原因码是否属枚举、单元测试/校验器是否过。不可用的：另一个模型空口夸「这步想得对」——那是把 judge 幻觉写进 reward，极易 hacking（见 `ali-reward-hacking`）。实践组合：任务成功 + 成本/步数惩罚；关键 tool 参数正确性过程分；对 irreversible action 单独约束；评测集区分「偶然成功」与「稳健策略」。Function Calling 的过程奖励设计还可对照 `ali-function-call-grpo-process-reward`。

例子：退货 Agent 先查单、再选原因码、最后提交。只在「退货成功」给 $r=1$，中间填错原因码但碰巧通过，模型会把错参当正确策略。应给「订单号填对」「原因码属于枚举」过程分，并对「提交退款」单独约束。

## 更细的 credit：切段，不要均匀广播

按 tool-call / turn 切段，只在 decision token 上优化；可恢复失败（超时重试）和不可逆失败不要同一负分。n-step / GAE 在逐步环境奖励存在时有用；多数电商 Agent 没有逐步 $r_t$，更现实的是 **动作边界对齐 + 稀疏过程分**。不要把最终 $r$ 均匀广播到每一句 Thought。多 Agent 还要在人之间分，更难，见 `arl-multi-credit`。

和 GRPO 叠法要说清两层：先把一条轨迹收成标量 $R$（最终成功 + 过程分 − 步数/成本 − 越权罚），再在同 prompt 的 $G$ 条轨迹上算组内 $A$。过程分加密的是 **轨迹之间** 的可分性，降低空组；切段优化的是 **轨迹内部** 的归因。两层同时乱加权，梯度会打架。没有自动校验器时，先 SFT 示范轨迹，不要用另一个 LLM 空口当过程奖励。

## 追问

- **过程奖励会不会刷步数？** 会。多调用就加分会鼓励无效工具。过程分应对「关键约束满足」，并对多余调用给成本惩罚。
- **没有校验器怎么办？** 先别上 RL。用 SFT 示范轨迹 + 沙盒成功率；没有自动判定就没有稳定梯度。
- **和 GRPO 组内优势怎么叠？** 先把每条轨迹收成标量（最终 + 过程 − 成本），再在同 prompt 组内标准化；不要在 token 上再叠一套互相打架的 $A$。

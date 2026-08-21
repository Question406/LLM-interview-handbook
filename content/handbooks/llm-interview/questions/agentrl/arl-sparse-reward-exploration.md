---
id: arl-sparse-reward-exploration
section: agentrl
order: 19
level: S
title: 长程 Agent 只有终局稀疏奖励时，如何做有效探索且不爆炸方差？
quick: 用课程、分层目标、好奇心/新颖性、演示引导与 Hindsight relabel；同时限制探索在安全动作子集，并监控无进展轨迹占比。
tags:
  - Exploration
  - Sparse Reward
  - Agent RL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: Hindsight Experience Replay
    url: https://arxiv.org/abs/1707.01495
    type: primary
---

纯 outcome 下，几十步工具调用只有终局 $0/1$，随机探索几乎碰不到成功，REINFORCE 方差随视野爆炸。陷阱是发明错误 shaping：奖「打开了文件」「多调了工具」，模型会刷假进度。目标是 **不发明错误 shaping 的前提下把可学习信号变密**，同时把探索关在安全动作子集里。

## 先让成功变得可碰到

按侵入性从低到高：

- **课程：** 先短 horizon、少工具、高成功率环境，再加长、加噪声。比一上来加大温度更稳——高温在不可逆动作上很贵。
- **演示 / 专家 bootstrap：** 先 SFT 或 BC 出能碰到成功的策略，再 RL。稀疏奖励几乎都需要这条；没有成功样本，组相对优势也全是 $0$。
- **分层 / 可验证子目标：** 「打开指定文件」「单测由红变绿」这类能执行检查的中间点可以给分。Shaping 必须可执行，否则刷假进度。见 `arl-credit`、`arl-reward`。
- **HER：** 失败轨迹按实际达到的状态 relabel 成「假如目标是这个」。适合目标空间明确（到达某 URL、某文件树），不适合开放对话。这是 relabel，不是事后编贡献，和 `arl-hindsight` 不同。
- **内在奖励：** 新颖性、预测误差。必须衰减，并监控与 gold 成功的相关；相关掉了就关，避免「为新而新」空转，见 `arl-loop`。

工程上：early episode 提高多样性温度，后期退火；工具失败做结构化重置，不要在坏状态空转到超时。探索动作限制在安全子集——不能乱删、乱付款、乱发外部请求。安全是硬约束，不是小负分。

## 控方差，不要靠无限加熵

碰到成功之后，方差仍然大：同一任务里绝大多数 rollout 仍是 $0$。更有效的是：

- 组相对 baseline（GRPO 式）比较同任务多条轨迹，而不是绝对 $0/1$；
- 短 rollout 截断与课程，先减 $T$；
- 成功轨迹过采样 / 回放，但要注意 off-policy，见 `arl-offpolicy-reuse`；
- 只在决策 token 上优化，不要把 observation 当策略目标。

评估看的是 **新成功模式** 是否出现，不是平均轨迹变长。盯：无进展轨迹占比、唯一成功模板数、intrinsic 与 gold 成功的相关、安全违规。轨迹变长但模板不增，多半在空转。相关掉了就关好奇心，不要调大熵系数硬撑。

面试收口：稀疏奖励先解决「到不了终局」，再解决归因。课程、演示、可验证子目标、HER 是正途；好奇心要衰减。探索锁在安全子集，用组相对和短视野压方差，而不是无限加噪声。

## 追问

- **和 `arl-hindsight` 重复吗？** 那题讲事后重估中间步；本题讲稀疏奖励下的探索工具箱，HER 只是其中一块 relabel。
- **Process reward 能替代探索吗？** 能加密信号，也会 hacking。探索解决「根本到不了终局」，过程奖励解决「到了但归因为难」。
- **方差还是大怎么办？** 组相对 baseline、短 rollout 截断、成功轨迹过采样，而不是无限加熵系数。
- **没有明确目标空间能用 HER 吗？** 很难。开放对话没有「已达状态」可当伪目标，应改用课程和可验证子目标。

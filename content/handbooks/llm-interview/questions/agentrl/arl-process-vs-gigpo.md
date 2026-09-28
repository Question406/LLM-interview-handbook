---
id: arl-process-vs-gigpo
section: agentrl
order: 123
level: S
title: Agent 逐步信用：过程奖励和 GiGPO 锚点哈希怎么选？
quick: >-
  有可验证中间事件就先写过程分 / 硬门，不要训打分头。没有逐步 oracle、但环境状态能重复对齐，再用 GiGPO
  做组内对照。开放网页几乎没有同一状态，两条都退回结局 $0/1$ 加权限门。过程奖励会 hacking；锚点哈希会错组。可以叠，不是二选一。
tags:
  - GiGPO
  - Process Reward
  - Credit Assignment
  - Agent RL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-24
sources:
  - title: Group-in-Group Policy Optimization for LLM Agent Training
    url: https://arxiv.org/abs/2505.10978
    type: primary
  - title: Let's Verify Step by Step
    url: https://arxiv.org/abs/2305.20050
    type: primary
---

`arl-credit` 列出过程奖励、Critic、hindsight 几条路；`arl-gigpo` 讲组内组怎么算；字节 / 阿里真题讲怎么设计过程分。本题只问先用哪一条。不要把 GiGPO 答成「另一种 PRM」，也不要把过程分答成「不训 Critic 的 GiGPO」。

## 先问环境，再问公式

按环境能提供什么选，不按论文新不新选。

| 环境给你什么 | 先用 | 别用 |
| --- | --- | --- |
| schema / 权限 / 单测 / 可复核里程碑 | 规则过程分 + 终局门槛 | 给 Thought 打「想得对」 |
| 可重置、状态能哈希（房间、模板页） | GiGPO 内层组 | 把 DOM 噪声写进 state id |
| 每次观测都独一无二 | 结局 $0/1$ + 硬门 + 缩短 horizon | 假装有逐步 oracle |
| 愿意多一个头、有逐步环境奖励 | GAE / Critic | 用 PRM 分数冒充 $V^\pi$ |

过程分改的是标量 $r$，让组内全失败也能排序，见 `byte-agentic-rl-process-reward`、`ali-function-call-grpo-process-reward`。GiGPO 不改 $r$，改的是优势怎么在步上相对：同一锚点状态下换一个动作，比折扣回报，见 `arl-gigpo`。PRM / Critic 的定义差见 `pt-prm-orm-critic`。

现场口令：有 oracle 先写门，有重复状态再分组，两样都没有就别硬造逐步信号。

## 失败模式不要说成一种

过程奖励。每个 dense 项都是新表面：重复合法查询、漂亮 JSON、空转检索。$\lambda$ 必须明显小于 1，或改成硬门控。验收看过程分与终局成功的相关，相关掉了先关 shaping。

GiGPO。内层组依赖「同一状态」真的同一。哈希过粗，不该一组的动作捆在一起；过细，组退化成单例，$\hat A_S=0$，等于没上逐步项。开放搜索结果、一次性订单号，内层经常是空的。

可学习过程模型。没有环境事件还要逐步分，等于再训一个会被拍马屁的评委。Let's Verify 的主场是找错步 / 搜索，不是宣称可以替换 Agent 的环境 oracle。

可以叠：规则项打在可验证事件上；剩下的稀疏结局仍用外层 GRPO；若还有重复锚点，再加 $\omega\hat A_S$。token 仍只训动作，观察要 mask，见 `pt-agent-grpo-token-mask`。不要三套信号都变成「整段平均」。

## 追问

- **和 GAE 怎么排？** 有逐步环境奖励、也愿意训 $V$，GAE 是正统 baseline。GiGPO 换的是不训 Critic、不多采一套。过程分可以进 GAE 的 $r_t$，进了之后就不要再把同一事件写成第二套线性加分。
- **Function Calling 两三步？** 终局 oracle 往往够。先别上 GiGPO，也别给每句 Thought 打分。
- **怎么证明选对了？** 过程分：注入错参必须掉、等价 JSON 不能变。GiGPO：报非空锚点组比例，接近 0 就说明内层没工作。held-out 任务成功是锚，milestone 均值不是。

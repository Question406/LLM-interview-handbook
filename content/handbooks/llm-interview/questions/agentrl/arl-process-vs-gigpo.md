---
id: arl-process-vs-gigpo
section: agentrl
order: 123
level: S
title: Agent 逐步信用：过程奖励和 GiGPO 锚点哈希怎么选？
quick: "看环境能给什么。有独立可验证的中间事件，就先用规则过程分或硬性检查；没有逐步标准、但状态能重复对齐，就用 GiGPO 在同一状态下比较不同动作。两样都没有，先用终局 $0/1$ 奖励加权限限制。过程分会被钻空子，锚点哈希也会分错组，两边要各自验证。"
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

先看环境能提供什么，再决定用哪一条。环境里有能独立验证的中间事件，比如 schema 校验、权限检查、单测、可复核的里程碑，就先用规则过程分，再加终局门槛；没有逐步标准、但状态能重复对齐，就用 GiGPO 在同一状态下比较不同动作；两样都没有，就老老实实用终局 $0/1$ 加权限限制，别硬造逐步信号。

先把两者分清楚，面试里最容易在这里混。过程分改的是标量 $r$，组内全失败的时候，也能靠中间事件排出先后，字节和阿里那两道真题就是在设计这个，见 `byte-agentic-rl-process-reward`、`ali-function-call-grpo-process-reward`。GiGPO 不改 $r$，改的是优势怎么在步上算：找到同一个锚点状态，看在这里换一个动作，折扣回报差多少，见 `arl-gigpo`。所以别把 GiGPO 答成「另一种 PRM」，也别把过程分答成「不训 Critic 的 GiGPO」。PRM 和 Critic 的定义差别在 `pt-prm-orm-critic`，过程奖励、Critic、hindsight 这几条路的全貌在 `arl-credit`，这题只问先用哪一条。

举个例子。Agent 在一个可重置的模板页面上操作，每次 reset 都回到同一个表单，很多条轨迹都会经过「表单填了一半」这个状态。把它哈希成锚点，比较在这里点提交和继续填的回报，GiGPO 就有东西可比。换成开放网页搜索，每次结果都不一样，订单号也是一次性的，几乎没有两条轨迹经过同一个状态，内层组经常是空的。

按环境能提供什么来选，大概是这张表：

| 环境给你什么 | 先用 | 别用 |
| --- | --- | --- |
| 字段和类型规范（schema） / 权限 / 单测 / 可复核里程碑 | 规则过程分 + 终局门槛 | 给 Thought 打「想得对」 |
| 可重置、状态能哈希（房间、模板页） | GiGPO 内层组 | 把 DOM 噪声写进 state id |
| 每次观测都独一无二 | 结局 $0/1$ + 硬门 + 缩短 horizon | 假装有逐步 oracle |
| 愿意多一个头、有逐步环境奖励 | GAE / Critic | 用 PRM 分数冒充 $V^\pi$ |

两边坏掉的方式不一样，要分开讲。过程奖励的每个 dense 项都是一个新的可钻空子的地方，重复合法查询、把 JSON 写得很漂亮、空转检索都能刷分。所以权重 $\lambda$ 要明显小于 1，或者干脆改成硬门控；验收看过程分和终局成功的相关性，相关性掉了，先把 shaping 关掉。GiGPO 依赖「同一状态」真的是同一个：哈希太粗，不该一组的动作被捆在一起；太细，组退化成单例，$\hat A_S=0$，等于没加逐步项。

再往下一档是可学习的过程模型。环境没有事件可查，还硬要逐步分，相当于再训一个会被拍马屁的评委。Let's Verify 的主场是找错步、做搜索，它没有说 PRM 能替代 Agent 的环境 oracle。

三种信号可以叠起来用：规则项打在可验证事件上，剩下的稀疏结局照样用外层 GRPO，还有重复锚点就再加 $\omega\hat A_S$。文本处理单位（token） 层面只训动作，观察要 mask，见 `pt-agent-grpo-token-mask`。三套信号别都变成整段平均。

## 追问

**和 GAE 怎么排？**
有逐步环境奖励、也愿意训 $V$，GAE 是正统 baseline。GiGPO 换来的是不用训 Critic、不用多采一套。过程分可以放进 GAE 的 $r_t$，放进去之后，同一个事件就别再写成第二套线性加分。

**Function Calling 只有两三步，要上这些吗？**
终局 oracle 往往就够了。先别上 GiGPO，也别给每句 Thought 打分。

**怎么证明选对了？**
过程分这边，注入错误参数分数必须掉，等价 JSON 分数不能变。GiGPO 这边，报非空锚点组的比例，接近 0 就说明内层没在工作。最后锚定 held-out 任务成功率，milestone 均值不算数。

---
id: xiaohongshu-credit-assignment
section: agentrl
order: 140
level: S
title: 小红书：Credit assignment 怎么做？
quick: "以最终结果为主奖励，只给能自动判定的中间里程碑加过程分，工具合法性检查当硬门，没过就排除。有逐步奖励用 GAE，只有轨迹奖励用组相对优势，再对应到需要训练的 token。最后用替换实验和反例检查模型是不是靠无用步骤刷过程分。"
tags:
  - Xiaohongshu
  - Credit Assignment
  - Agent RL
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 小红书大模型实习一面
    url: https://www.nowcoder.com/feed/main/detail/3f96f6fe7ed44c3b8c49cea3455d38a4
    type: candidate-first-hand
---

## 真题记录

- 公司：小红书
- 团队 / 岗位：大模型实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“credit assignment怎么实施的”**

我会按三步实施：先定下能自动判定的中间里程碑，只给这些事件过程分，终局成功还是主奖励；再把信号传到可训练的 token 上；最后用替换实验验证归因对不对。不可验证的 思维链（CoT） 写得再好也不给分。

要这么做，是因为单轮 outcome 强化学习（RL） 把整段 completion 当成一个动作，credit 已经很粗；Agent 轨迹更长，选错工具可能在第 2 步，成败却到最后才知道。拿小红书业务里「笔记审核 / 检索改写」这类轨迹来说，中间检索有没有命中能查，这一步就能给分；改写得好不好没法自动判，就只能靠终局。中间步能不能验证，比换一个更炫的优势估计器更决定能不能训动。背景差异见 `xiaohongshu-agentic-rl-diff`，通用方法见 `arl-credit`。

里程碑选那些能自动判定的事件：检索是否命中、调用是否符合 schema、子目标是否达成。只对这些给 dense 信号，Thought 流畅不流畅不计入 reward。合成奖励时加门槛，合法门没过，outcome 记零，防止「业务碰巧过、调用全错」的轨迹拿分。这和 `arl-reward`、`ali-function-call-grpo-process-reward` 是同一个约束。

传到 token 时，同一步里的 thought 和 action 共享步级优势；有逐步 $r_k$ 就用 GAE，GRPO 则在同任务的多条轨迹之间对比。广播和 mask 的细节按 `byte-agent-token-credit`：观测结果（observation）、输入提示（prompt）、padding 不进梯度。诊断时看奖励从哪一步开始分叉，再做替换实验，改掉某一步的 observation 或者删掉某次调用，看归因站不站得住，见 `arl-hindsight`。

Dense 信号一定会被 hack：反复做合法但没用的检索刷「命中」，把 JSON 写得很长刷 formatter。对策是终局锚定、多余调用惩罚、等价改写分数不变、注入错误参数必须掉分。成功轨迹过采样能降方差，但别把过程分当成新的主任务。实施上我会先把「同任务多条 rollout 加可执行门」跑通，再加 hindsight 或逐步 GAE；一上来就给每句 Thought 打分，通常是在优化叙事。多 Agent 还要在成员之间分，更难，见 `arl-multi-credit`。

## 追问

**没有中间 oracle 怎么办？**
只用终局，加上 schema 和权限的硬门，或者缩短 horizon。别用另一个模型空口打步分。

**GAE 和 GRPO 怎么选？**
有逐步环境奖励用 GAE；只有轨迹级 $0/1$、又能同一任务多跑几条，用组相对。两者可以并存：组内比终局，再加少量过程项。过程分和 GiGPO 怎么排，见 `arl-process-vs-gigpo`。

**怎么证明归因是对的？**
删掉或替换嫌疑步，终局应该明显变化。终局不变却拿了高过程分，就是在编故事。

**指标怎么报？**
原帖也问到了指标。除了任务成功，还要报过程分和成功的相关性、刷步率、mask 有没有漏掉 observation。credit 方案本身也是评测对象，过程分和成功的相关性掉了，就把 shaping 关掉。

---
id: ali-function-call-grpo-process-reward
section: agentrl
order: 101
level: S
title: 阿里 26 校招：GRPO 训练 Function Calling，过程奖励如何设计？
quick: >-
  用 outcome reward 验证最终业务结果，再增加只奖励可验证过程事件的信号：选对工具、参数 / schema 正确、权限合规、工具结果被正确
  grounding、低成本完成。不要奖励表面 JSON 漂亮或无意义的多步调用。
tags:
  - Alibaba
  - 2026 Campus Recruiting
  - GRPO
  - Function Calling
  - Process Reward
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 阿里26校招大模型算法二面45min（候选人原帖）
    url: https://www.nowcoder.com/feed/main/detail/2c84e26c05664d52845959039cf99edd
    type: candidate-first-hand
---
## 真题记录

- 公司：阿里巴巴
- 团队 / 岗位：大模型算法
- 届别 / 流程：26 届校招；二面（45 分钟）
- 面试时间：原帖未披露；帖子发布于 2025-12-12
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“在使用 GRPO 提升大模型的Function Calling能力时，除了结果奖励（outcome reward），还可以如何设计过程奖励（process reward）？”**

错法：把「JSON 漂亮、多调几次工具、CoT 写得长」当成过程分。阿里这面要听的是：终局仍由可执行业务 oracle 判定，过程分只打可自动验证的事件，并且这些事件必须提高到达正确终局的概率。只靠 outcome 的长工具链，关键错参和正确前缀会被同一条 $0/1$ 糊在一起，见 `arl-credit`、`ali-agent-final-reward`。

## 过程分只打可验证事件

我会把一条 Function Calling 轨迹拆成硬门 + 终局 + 稀疏过程项，而不是再请一个 LLM 夸「这步想得对」：

- **工具选择：** 当前 state 下是否选了契约里允许且任务需要的 tool；选不存在 / 越权工具直接 hard fail。
- **参数 / schema：** 必填字段齐、类型对、枚举落在白名单、ID 能在环境里 grounding（订单号真存在，而不是格式像订单号）。
- **权限与副作用：** 未授权写操作、不确定是否执行的高风险 action，按失败处理，不用小负分抵消，见 `agent-tool-permissions`。
- **Observation grounding：** 下一步是否使用了工具返回，而不是忽略结果继续编。
- **成本：** 在终局正确的前提下惩罚多余调用；单独奖「步数多」会刷无意义循环。

不可用的过程分：formatter 分数、Thought 流畅度、调用次数本身。这些和 `ali-reward-hacking` 同一类 proxy。合成标量时用门槛：schema / 权限未过则 outcome 项为零，防止「业务碰巧过、契约全错」成为最优。

## GRPO 组内必须可比，还要防刷步骤

GRPO 吃的是同一 prompt 下多条 rollout 的相对优势。Verifier 要对等价参数、可交换的独立调用、外部抖动鲁棒，否则组内 $A_i$ 比较的是「环境今天是否抖」而不是策略。同一任务的 group 应共享工具版本、权限集和 oracle；环境污染会破坏组相对，见 `arl-environment-reset`。

上线前三组反事实：注入错误 tool / 错误参数，过程分必须掉；把合法调用改成字段顺序不同的等价 JSON，过程分不能变；加无意义的重复查询，成本项应惩罚、outcome 不应涨。若过程分与终局成功相关掉了，先关 shaping 再查 oracle。Token 级怎么落到可训练 token，对照 `byte-agent-token-credit`。Outcome 锚定业务结果；过程分只覆盖选 tool、schema、权限、grounding 和成本。GRPO 还要求 verifier 对等价轨迹稳定，并用注入测试确认没有在刷 formatter。

## 追问

- **没有可执行 oracle 怎么办？** 先把任务改到能自动判定，或只用 schema / 权限硬门，不要用另一个模型空口打过程分。状态能哈希时可以用 GiGPO，见 `arl-process-vs-gigpo`。
- **和纯 outcome GRPO 何时够用？** 两三步、对错一眼能看时可以先只用终局；长链、有不可逆写操作时必须加密可验证中间事件。
- **过程分会不会 hacking？** 会。每个 dense 项都是新表面。用终局门槛、相关监控和「等价 JSON / 多余调用」反事实压刷分。
- **组内有的轨迹环境超时？** 超时样本不要进相对优势，否则模型学的是基础设施抖动。先修环境，再谈算法。

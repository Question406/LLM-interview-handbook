---
id: ali-function-call-grpo-process-reward
section: agentrl
order: 101
level: S
title: 阿里 26 校招：GRPO 训练 Function Calling，过程奖励如何设计？
quick: >-
  终局仍由可执行的业务 oracle 判，过程分只奖励能自动验证的事件：选对工具、参数过 schema、遵守权限、用上工具返回、不做多余调用。schema
  或权限没过时 outcome 项归零；JSON 好看或调用次数多不给分，上线前用等价 JSON 和注入错参做反事实检查。
tags:
  - Alibaba
  - 2026 Campus Recruiting
  - GRPO
  - Function Calling
  - Process Reward
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21T00:00:00.000Z
sources:
  - title: 阿里26校招大模型算法二面45min（候选人原帖）
    url: 'https://www.nowcoder.com/feed/main/detail/2c84e26c05664d52845959039cf99edd'
    type: candidate-first-hand
---

## 真题记录

- 公司：阿里巴巴
- 团队 / 岗位：大模型算法
- 届别 / 流程：26 届校招；二面（45 分钟）
- 面试时间：原帖未披露；帖子发布于 2025-12-12
- 来源类型与可信度：牛客候选人原帖，A
- 原始措辞：**“在使用 GRPO 提升大模型的 Function Calling 能力时，除了结果奖励（outcome reward），还可以如何设计过程奖励（process reward）？”**

我会让最终业务结果仍由可执行的 oracle 来判，过程分只打能自动验证、而且确实能提高到达正确终局概率的中间事件：选对工具、参数通过 schema 校验、遵守权限、用上了工具返回、不做多余调用。JSON 写得漂亮、多调几次工具、CoT 写得长，这些都不给分。

为什么要过程分？长工具链只靠 outcome 的话，关键的错参和正确的前缀会被同一个 $0/1$ 糊在一起，见 `arl-credit`、`ali-agent-final-reward`。比如一条「查订单 → 改地址」的轨迹，第一步填的订单号格式没问题，可这个订单根本不存在，后面全跟着错；只看终局，模型不知道是哪一步坏的。

## 过程分只打可验证事件

一条 Function Calling 轨迹我会拆成 mandatory checks、终局和稀疏过程项，不再请一个 LLM 来夸「这步想得对」。工具选择看当前 state 下选的 tool 是不是契约里允许、任务也需要的，选了不存在或越权的工具直接 hard fail。参数看必填字段齐不齐、类型对不对、枚举在不在白名单里，ID 能不能在环境里 grounding，订单号要真存在，格式像订单号不算。权限和副作用方面，未授权的写操作、不确定有没有执行的高风险 action，都按失败处理，不用小负分去抵，见 `agent-tool-permissions`。Observation grounding 看下一步有没有用上工具返回，忽略结果继续编要扣分。成本是在终局正确的前提下惩罚多余调用，单独奖「步数多」会刷出无意义的循环。

formatter 分数、Thought 流畅度、调用次数本身都不能当过程分，它们和 `ali-reward-hacking` 里说的是同一类 proxy。合成标量时用 threshold：schema 或权限没过，outcome 项直接为零，这样「业务碰巧过、契约全错」就不会成为最优。

## GRPO 组内要可比，还要防刷步骤

GRPO 比的是同一个输入下多条 sampling 轨迹（rollout）的相对优势，所以验证器（verifier）对等价参数、可交换的独立调用、外部抖动都要稳，不然组内 $A_i$ 比出来的是「环境今天抖没抖」。同一任务的 group 要共享工具版本、权限集和 oracle，环境污染会破坏组相对，见 `arl-environment-reset`。

上线前我会做三组反事实：注入错误 tool 或错误参数，过程分必须掉；把合法调用改成字段顺序不同的等价 JSON，过程分不能变；加无意义的重复查询，成本项要罚、outcome 不能涨。过程分和终局成功的相关性掉了，先关 shaping，再查 oracle。过程信号怎么对应到需要训练的 token，对照 `byte-agent-token-credit`。

## 追问

**没有可执行 oracle 怎么办？**
先把任务改到能自动判定，或者只用 schema validation 与 authorization checks，别让另一个模型空口打过程分。状态能哈希的话可以用 GiGPO，见 `arl-process-vs-gigpo`。

**什么时候纯 outcome GRPO 就够了？**
两三步、对错一眼能看时，可以先只用终局；推理过程很长、有不可逆写操作时，要加密可验证的中间事件。

**过程分会不会被 hack？**
会，每个 dense 项都是一个新的可钻空子的地方。用终局 threshold、相关性监控和「等价 JSON / 多余调用」反事实把刷分压住。

**组内有的轨迹环境超时了怎么办？**
超时样本别进相对优势，否则模型学到的是基础设施抖动。先修环境，再谈算法。

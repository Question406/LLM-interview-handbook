---
id: baichuan-multi-agent-collab
section: agent
order: 125
level: A
title: 百川智能：多 Agent 如何协作？
quick: >-
  先定义共享任务状态、角色接口和唯一写者，再选路由、辩论、流水线里的一种，别做成多个 chatbot 互聊。协作协议要含交接、冲突解决、超时和失败升级，用端到端任务成功评，别看对话轮数。
tags:
  - Baichuan
  - Multi-Agent
  - Coordination
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 百川智能大模型实习一面 压力好大
    url: https://www.nowcoder.com/feed/main/detail/e3e6543bd5ab478292b74a48f031c530
    type: candidate-first-hand
---

## 真题记录

- 公司：百川智能
- 团队 / 岗位：大模型实习
- 届别 / 流程：实习；一面
- 面试时间：原帖未披露；帖子发布于 2026-02-12
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“多 agent如何如何做的协作”**

错法：「多个 chatbot 互聊」。多 Agent 只在单模型上下文或技能过载时才值得拆。先写共享 state、角色接口和唯一写者，再选拓扑。评的是端到端任务成功，不是轮数。对照 `arl-multiagent`、`pdd-multi-vs-single-agent`、`xiaohongshu-multiagent-quality`。同一面表格 / SQL 是天然流水线。

## 先协议，后拓扑

共享 state：任务目标、已检索证据、表格句柄、未决问题、权限。每个角色短接口（规划、检索、SQL、校验）。同一资源只能有一个 writer，避免互相覆盖。交接必须结构化（JSON / 工具参数），不要靠「请你接着说」。失败时重试当前角色、换工具或升级人，设超时，禁止两个 Agent 无限讨论。

常见拓扑：

- **路由器 + 专家**：主控选一个专家执行，简单、易测。
- **流水线**：抽取 → 执行 → 校验，适合表格 / SQL，见 `baichuan-complex-table-extract`。
- **辩论 / 复核**：高风险结论由独立 checker 找错，成本高，用于信贷解释或不可逆写入。

## 什么时候不该拆

上下文装得下、工具面不大、角色边界糊时，拆开会增加交接错误和重复调用。单 Agent 加清晰 Skill 往往更稳。评测看最终任务成功、冲突次数、重复调用、越权、延迟。表格场景里：一个 Agent 理解用户意图，一个写受限 SQL，一个解释结果，比三个通用助手清楚。权限仍在网关，角色提示不能提权，见 `agent-tool-permissions`。

## 追问

- **冲突谁说了算？** 共享 state 的唯一 writer + 显式冲突规则（校验角色可否决执行角色）。不要靠更长的辩论。
- **要不要共享全部对话？** 不要。只传接口需要的字段，降低串扰和注入面。
- **怎样发现拆错了？** 交接失败、重复工具调用、端到端成功不升但费用升。这时合并角色。
- **和单 Agent 路由的差别？** 路由是选一条技能；多 Agent 是多角色并发或流水线。先证明单 Agent 不够再拆。

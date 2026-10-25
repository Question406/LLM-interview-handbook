---
id: meituan-workflow-vs-agent
section: agent
order: 120
level: A
title: 美团：Workflow 和 Agent 的核心差异与适用场景？
quick: "核心差异在控制权：Workflow 的下一步由人预先写死，可控、可测、延迟稳定；Agent 由模型动态选工具和下一步，灵活但边界难保证。稳定 SOP 用 Workflow，开放任务和探索用 Agent，生产里常是外层 Workflow 保边界、局部节点交给 Agent，再加护栏。"
tags:
  - Meituan
  - Agent
  - Workflow
  - 2025-2026
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: 美团大模型算法岗完整面经（一面+二面）
    url: https://www.nowcoder.com/feed/main/detail/b264abf14d4d4c44bc022c9ea1dce981
    type: candidate-first-hand
---

## 真题记录

- 公司：美团
- 团队 / 岗位：大模型算法
- 届别 / 流程：原帖未披露；一面
- 面试时间：原帖未披露
- 来源类型与可信度：牛客候选人原帖，B
- 原始措辞：**“详细区分 Workflow 和 Agent 的核心差异与适用场景”**

Workflow 和 Agent 的核心差异是控制权：下一步做什么，是人预先写死，还是交给模型选。能调工具不等于 Agent，下一跳和参数都由规则决定的，只是 Workflow 里的工具节点，把「能调工具的 chat」都叫 Agent 是常见误区。生产里几乎总是组合用：外层 Workflow 保边界，局部节点交给 Agent 消化歧义。

美团到店售后能说明这个分法。「先查订单再判责」这种流程写得全，就不要交给模型自由选边。用户说「骑手等了很久但系统显示已送达」，描述含糊，要跨骑手、商家和系统日志排查，路径事先写不全，这时才在查证节点里放一个 Agent，做理解、检索和跨系统排查，查完回到固定节点出结论或转人工。

Workflow 把控制流写成有向图或状态机，节点、边、超时、重试、降级都由人预先规定。它适合输入字段和类型规范（schema）稳定、合规要求硬、延迟必须可预测的链路。失败按节点契约定位，评测按节点成功率拆，成本也可预测。Agent 让模型来选工具、填参数、决定澄清还是终止，适合目标开放、路径事先写不全的任务。代价是轨迹方差大，要另做权限、预算、副作用控制和可回放的 trace；评测看任务成功加过程违规，光看最终一句话不够，见 `jd-agent-eval-beyond-qa`。

| 维度 | Workflow | Agent |
| --- | --- | --- |
| 控制 | 人写死边与条件 | 模型选 action |
| 失败 | 节点级重试 / 降级清晰 | 需轨迹级恢复 |
| 评测 | 单节点契约 | 成功率 + 过程违规 |
| 成本 | 可预测 | 步数 / 工具费方差大 |

落到美团的业务，下单、退款、券核销、账号变更优先走 Workflow，涉及金额和券的必须有 Human-in-the-loop。复杂客诉可以局部用 Agent。探索性任务，比如帮用户规划周末到店组合，可以用 Agent，但还是要有预算，不可逆动作要确认。灵活是有代价的，代价就是边界，这类业务先保边界。

组合的方式是让 Workflow 的某个节点内部跑 Agent 循环，进出节点的契约不变：进节点带订单号，出节点必须是枚举结论。这样延迟和合规仍然能测。Skill 可以描述「这类客诉怎么做」，再编译进图，或者交给 Agent 按需加载，见 `jd-skills-essence`。现场判断时可以问一句：失败后能不能按节点契约复盘？能，多半是 Workflow；只能回放整段模型对话再猜下一步，就已经是 Agent 了。没有状态闭环和副作用控制的，只是 RAG 管道或工具 chat，不用升级称呼。

图框架只是实现手段，见 `meituan-langgraph-vs-prompt`；和检索增强生成（RAG）的关系见 `jd-agent-vs-rag`，RAG 常常只是其中一种动作。

## 追问

**能调工具就是 Agent 吗？**
不是。下一跳和参数都由规则写死的话，那是 Workflow 里的工具节点。

**为什么生产要组合？**
全用 Agent 很难保证退款边界，全用 Workflow 又覆盖不了开放的表述。外层保合规，内层消化歧义。

**延迟敏感的链路能上 Agent 吗？**
可以，但要设步数上限和超时边。超时必须降级到固定话术或人工，不能让模型无限想。

**和 Multi-Agent 什么关系？**
多 Agent 是把动态决策再拆成几个角色，代价更高。能用单 Agent 节点或路由解决的，不要先拆，见 `jd-rag-multiagent-iter`。

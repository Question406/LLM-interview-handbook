---
id: meituan-workflow-vs-agent
section: agent
order: 120
level: A
title: 美团：Workflow 和 Agent 的核心差异与适用场景？
quick: >-
  Workflow 是预定义有向图 / 状态机，可控、可测、延迟稳定；Agent 由模型动态选工具与下一步，灵活但难保证边界。业务上：稳定 SOP
  用 Workflow，开放任务与探索用 Agent，生产常二者组合并加护栏。
tags:
  - Meituan
  - Agent
  - Workflow
  - 2025-2026
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-19
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

陷阱是把「能调工具的 chat」都叫 Agent。关键差异是控制权：下一步由人写死还是由模型选。美团到店 / 配送里，下单、退款、风控要可控可测；复杂客诉理解才需要动态决策。生产几乎总是组合：外层 Workflow 保边界，局部节点交给 Agent。图框架只是实现，见 `meituan-langgraph-vs-prompt`；和 RAG 的关系见 `jd-agent-vs-rag`——RAG 常是其中一种动作。

## 控制流、失败和评测都不一样

Workflow 把控制流写成有向图或状态机：节点、边、超时、重试、降级都是人预先规定。适合输入 schema 稳定、合规硬、延迟必须可预测的链路。失败按节点契约定位，评测按节点成功率拆。成本可预测。

Agent 把「下一步做什么」交给模型：选工具、填参、决定澄清或终止。适合目标开放、路径事先写不全的任务。轨迹方差大，必须另做权限、预算、副作用和可回放 trace。评测是任务成功 + 过程违规，不能只看最终一句，见 `jd-agent-eval-beyond-qa`。

| 维度 | Workflow | Agent |
| --- | --- | --- |
| 控制 | 人写死边与条件 | 模型选 action |
| 失败 | 节点级重试 / 降级清晰 | 需轨迹级恢复 |
| 评测 | 单节点契约 | 成功率 + 过程违规 |
| 成本 | 可预测 | 步数 / 工具费方差大 |

没有状态闭环和副作用控制，只是 RAG 管道或工具 chat，不要升级称呼。

## 美团场景：强约束走 Workflow，开放理解局部 Agent

下单、退款、券核销、账号变更：优先 Workflow，金额与券必须 Human-in-the-loop。复杂客诉（「骑手等了很久但系统显示已送达」）可局部 Agent 做理解、检索、跨系统排查，但查完回到固定节点出结论或转人工。探索性任务（帮我规划周末到店组合）可用 Agent，仍要预算和不可逆动作确认。

组合方式：Workflow 的某个节点内部是 Agent 循环，但进出节点的契约不变——进节点带订单号，出节点必须是枚举结论。这样延迟和合规仍可测。Skill 可以描述「这类客诉怎么做」，再编译进图或交给 Agent 按需加载，见 `jd-skills-essence`。面试不要把灵活性说成无条件优点：灵活的代价是边界，美团业务先保边界。判断题可以用「失败后能不能按节点契约复盘」：能，多半是 Workflow；只能回放整段模型对话再猜下一步，已经是 Agent。两者都合法，取决于路径能否事先写全。到店售后里「先查订单再判责」写得全，就不要交给模型自由选边；「用户描述含糊、要跨骑手 / 商家 / 系统日志」写不全，才在查证节点内放 Agent。

## 追问

- **能调工具就是 Agent 吗？** 不是。若下一跳和参数都是规则写死，那是 Workflow 里的工具节点。
- **为什么生产要组合？** 全 Agent 难保证退款边界；全 Workflow 覆盖不了开放表述。外层保合规，内层消化歧义。
- **延迟敏感链路能上 Agent 吗？** 可以，但要步数上限和超时边；超时必须降级到固定话术或人工，不能无限想。
- **和 Multi-Agent 的关系？** 多 Agent 是把动态决策再拆角色，代价更高。能用单 Agent 节点或路由解决的不要先拆，见 `jd-rag-multiagent-iter`。

---
id: ali-framework-choice
section: alibaba
order: 27
level: A
title: Agent 编排选 LangChain 类开源还是自研？
quick: PoC 可用开源加速；生产看可控性、可观测、权限与性能。核心业务链路我一般自研状态机/图编排，开源作外围。关键是 trade-off，不是站队。
tags:
  - Alibaba
  - Agent
  - 架构
realInterview: true
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ 淘天 Agent 开发技术面
    url: 'https://www.nowcoder.com/feed/main/detail/4c8da8a740e64eb5827fb1b962928eda'
    type: legacy-reference
  - title: ↗ 淘宝闪购 Agent 算法一面
    url: 'https://www.nowcoder.com/discuss/879393838081597440'
    type: legacy-reference
---

错法：站队。「LangChain 不生产」或「自研才专业」。PoC 可用 LangChain / LangGraph 类开源加速；生产看可控性、可观测、权限与性能。核心业务链路往往自研状态机或图编排，开源作外围（连接器、评测脚手架）。淘天/闪购面经共同点：能说清「为何选/为何不选」，并承认企业内数据不出域、私有化约束。MCP vs Function Calling 是协议层，和编排框架不是同一题（`ali-mcp-vs-fc`）。

## 适用条件：验证期开源，资金链路自研

需求还在验证、团队没人写编排时，开源能快出 Demo。一旦涉及资金、库存、售后写操作、数据不出域或要私有化，框架升级和隐默重试会变成事故源，核心路径应自研。对比维度：开发速度、可调试性、版本锁定、性能开销、安全合规、团队熟悉度。开源默认的自动重试、隐式记忆和全量工具注入，带进生产会出现重复下单或权限绕过。

例子：闪购客服 Agent，PoC 用开源把「查单 → 推荐 → 下单」串起来；上线后把「改地址 / 取消订单」收进自研状态机，每步有明确超时、幂等键和审计，开源只保留外围检索和 prompt 实验。Guardrail 必须写在编排和工具服务端，不能只写在 system prompt（`ali-guardrail`）。

## 可观测与权限是业务约束，不是插件清单

自研成本在脚手架：trace、回放、权限矩阵、熔断。这些在双十一峰值下是存活条件（`ali-double11-scale`），不是框架 feature 列表上的可选项。开源适合：评测跑 batch、连一批只读工具、prompt 实验。不适合：不可逆写、跨域数据、需要确定性状态机的售后。模块化规划与 fallback 应是显式图，而不是 agent 循环里碰运气（`ali-modular-agent-plan`）。

追问「自研成本会不会更高」：承认脚手架成本，但强调可观测和权限是业务约束。混合是常态：外围开源、核心自研，用稳定的 tool schema 当边界，而不是把整个图锁死在某一个库的大版本上。闪购/淘天这题我会讲 trade-off：PoC 速度 vs 生产可控。我会画出「哪些边必须确定性、哪些边可以 LLM 发挥」，不背框架名。版本锁定、隐式 memory、全量工具注入这三件事，我会主动说关或下沉到服务端。

## 追问

- **LangGraph 算自研吗？** 仍是开源运行时。图你自己画，但重试、checkpoint、版本仍受上游约束。关键写路径建议自研状态机。
- **如何防止开源隐式重试？** 幂等键下沉到工具服务端；编排层关掉自动 retry，或只对只读路径开。
- **和 MCP 怎么分工？** MCP 管 tool/resource 协议；编排管状态、权限、降级。协议开源、编排自研是常见切法。

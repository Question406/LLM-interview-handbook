---
id: ali-framework-choice
section: agent
order: 27
level: A
title: Agent 编排选 LangChain 类开源还是自研？
quick: "PoC 阶段用 LangChain / LangGraph 类开源框架快速验证；上生产后，涉及资金、写操作或数据不出域的核心链路改用自研状态机或图编排，连接器、评测这类外围继续用开源。回答时要说清收益和维护成本。"
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

我的答案是混合：验证期用开源跑通，核心业务链路自研，外围继续用开源。站队说「LangChain 不能上生产」或者「自研才专业」都答偏了。淘天和闪购的面经有个共同点，面试官要听你说清为什么选、为什么不选，并且考虑到企业内数据不出域、要私有化部署这些约束。

拿闪购客服 Agent 举例。PoC 阶段用开源把「查单 → 推荐 → 下单」串起来，很快就能出 Demo。上线后，「改地址 / 取消订单」收进自研状态机，每步有明确的超时、idempotency key 和审计，开源只留给外围检索和 prompt 实验。

核心路径要收回来，是因为一旦涉及资金、库存、售后写操作、数据不出域或私有化，框架升级和隐式重试都可能引发事故。开源默认的自动重试、隐式记忆和全量工具注入，带进生产就会出现重复下单或权限绕过，这三件事加上版本锁定，我会主动说明怎么关掉或者下沉到服务端。比较的时候看开发速度、可调试性、版本锁定、性能开销、安全合规和团队熟悉度。Guardrail 要写在编排和工具服务端，光写在 system prompt 里不够（`ali-guardrail`）。

开源适合跑评测 batch、连一批只读工具、做 prompt 实验；不可逆写、跨域数据、需要确定性状态机的售后就不适合。模块化规划和 fallback 应该是一张显式的图，别在 agent 循环里碰运气（`ali-modular-agent-plan`）。

被追问「自研成本会不会更高」，我会承认脚手架有成本，trace、回放、权限矩阵、熔断这些基础设施都得自己补。但可观测和权限是业务约束，面对双十一这样的流量峰值，它们直接决定系统能不能稳住（`ali-double11-scale`）。两边混用时，用稳定的工具 schema 约定接口，别把整张图锁死在某个库的大版本上。白板上我会画出哪些边必须确定性、哪些边可以让 LLM 发挥，框架名不用背。另外，MCP 和 Function Calling 是协议层的问题，和选编排框架是两道题（`ali-mcp-vs-fc`）。

## 追问

**LangGraph 算自研吗？**
还是开源运行时。图是你自己画的，但重试、checkpoint 和版本仍受上游约束，关键写路径建议用自研状态机。

**怎么防止开源框架的隐式重试？**
把 idempotency key 下沉到工具服务端；编排层关掉自动 retry，或者只对只读路径开。

**和 MCP 怎么分工？**
MCP 管 tool / resource 协议，编排管状态、权限和降级。协议用开源、编排自研，是常见的切法。

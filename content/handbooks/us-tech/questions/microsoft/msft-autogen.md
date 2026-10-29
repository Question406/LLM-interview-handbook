---
id: msft-autogen
section: microsoft
order: 12
level: A
title: Microsoft：AutoGen / 多 agent 编排，失败、预算、和 SK 差别
quick: >-
  AutoGen 用多个可对话 agent 编排任务，Semantic Kernel 则围绕插件、过滤器和中间件管理 call interface。多
  agent 的状态要核对系统证据，宿主限制轮数、token、时间与写操作，避免循环、hallucination 成功和权限漂移。
tags:
  - Microsoft
  - AutoGen
  - Agent
  - Orchestration
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: AutoGen — Enabling Next-Gen LLM Applications via Multi-Agent Conversation
    url: 'https://arxiv.org/abs/2308.08155'
    type: primary
  - title: Magentic-One — A Generalist Multi-Agent System for Solving Complex Tasks
    url: 'https://arxiv.org/abs/2411.04468'
    type: primary
  - title: Semantic Kernel overview
    url: 'https://learn.microsoft.com/en-us/semantic-kernel/overview/'
    type: primary
---

## 可以这样回答

AutoGen 管多个 agent 如何协作对话，Semantic Kernel 管工具调用和 middleware responsibilities。企业助手可以用 SK 控制权限，需要复杂协作时再启动有预算的子团队。例如浏览器 agent 与终端 agent 可以分工，但测试是否通过仍要读取执行结果，不能仅靠彼此的口头确认。

SK 的原生函数会有副作用，语义函数只产文本，写操作要确认，失败结构化返回，见 `msft-semantic-kernel`。AutoGen 中多个模型互发消息，若缺少这些 authorization checks，一句「看起来已完成」就可能成为后续错误事实。企业助手可由 SK 或后来的 Agent Service 管工具，再用子团队写代码、浏览网页。GroupChat 直接接生产邮箱会放大重复副作用。

## 技术备查

AutoGen 管多个 agent 如何协作对话，Semantic Kernel 管工具调用和 middleware responsibilities。企业助手可以用 SK 控制权限，需要复杂协作时再启动有预算的子团队。例如浏览器 agent 与终端 agent 可以分工，但测试是否通过仍要读取执行结果，不能仅靠彼此的口头确认。

AutoGen（Wu 等）把 LLM、人和工具组合成 conversable agent，Magentic-One 在此上增加 Orchestrator、Task Ledger 和 Progress Ledger。公开 SDK 从 0.2 group chat 向 Agent Framework 演进，API 名称需要按版本确认。本卡是公开架构讨论，`realInterview: false`。

## 编排与 tool interface 与 permissions 各管一层

| | Semantic Kernel | AutoGen / Magentic-One |
| --- | --- | --- |
| 单位 | 插件函数 + 一次模型调用 | 多个 conversable agent |
| 控制 | filter / 中间件拦调用 | 对话策略、选下一个说话者 |
| 身份 | 用户授权令牌向下传到 Graph | 每个 agent 自己的工具箱，更容易漏 ACL |
| 产品位 | Copilot 式企业插件运行时 | 研究 / 复杂任务的多智能体实验床 |

SK 的原生函数会有副作用，语义函数只产文本，写操作要确认，失败结构化返回，见 `msft-semantic-kernel`。AutoGen 中多个模型互发消息，若缺少这些 authorization checks，一句「看起来已完成」就可能成为后续错误事实。企业助手可由 SK 或后来的 Agent Service 管工具，再用子团队写代码、浏览网页。GroupChat 直接接生产邮箱会放大重复副作用。

Coder / Reviewer 可能互相鼓励反复修改，未设 `max_round` 就持续消耗 TPM；选 speaker 还可能偏向健谈角色。工具超时却被总结成测试通过，也需要回到系统记录核验。Web Surfer 的应用身份、Coder 的沙箱密钥等权限必须放在工具运行时，evidence limitations 见 `msft-copilot-ground`。

每轮复制全量聊天会让 $T$ 增长，加重 TPM 与 lost-in-the-middle，见 `msft-azure-tpm`、`msft-long-context`。Ledger 保留结构化状态：外环改 Task Ledger 计划，内环改 Progress Ledger 进度，连续无进展就重计划。论文 GAIA / WebArena 完成率在百分之三十几量级，可用来分析失败与恢复。

## 预算和副作用写进运行时

```python
def run_team(step, *, max_rounds=8, max_tokens=12000, max_wall_s=120):
    used, t0 = 0, time.time()
    for r in range(max_rounds):
        if used >= max_tokens or time.time() - t0 > max_wall_s:
            return {"status": "budget", "round": r}
        out = step(r)
        used += out["tokens"]
        if out["done"] or out.get("needs_human"):
            return out
    return {"status": "max_round"}
```

除轮数、token、时间上限外，只读操作可以自动，写、发、删、付款要确认或使用 idempotency key，默认不重试。`design-agent-harness` 中的工具类型、沙箱、钱和步数都要有硬限制。

评测把真完成、预算终止、失败后 hallucination 成功和重复副作用分开，避免把「宣称完成」记为成功。多角色设计也要证明覆盖了不同工具界面，不能只按人数判断能力。

## 追问

**单 agent 加工具不够吗？**
能用清楚 schema 完成就优先单 agent。隔离浏览器与终端，或需要明确复核时，再验证多角色的收益。

**人应该放在哪？**
计划确认、不可逆动作和预算耗尽的降级，而非靠加入下一轮聊天临时判断是否继续。

**AutoGen 0.4 或后续改名会影响回答吗？**
抽象仍然适用，但具体 API 要核对版本。对话编排与插件运行时承担的职责并未因此消失。

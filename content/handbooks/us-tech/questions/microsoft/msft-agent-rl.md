---
id: msft-agent-rl
section: microsoft
order: 20
level: A
title: Microsoft：多 agent 失败，循环、互相吹捧幻觉、预算？
quick: "多 agent 要同时验证是否真正完成、是否应当停止：宿主限制轮数、token 和实际耗时，结果用退出码、CI、文件或 API 状态核验。另一个 agent 说「成功」不能当 RL 奖励。连续无进展时重计划，写操作默认不自动重试。"
tags:
  - Microsoft
  - Multi-Agent
  - Evaluation
  - Budget
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: AutoGen — Enabling Next-Gen LLM Applications via Multi-Agent Conversation
    url: https://arxiv.org/abs/2308.08155
    type: primary
  - title: Magentic-One — A Generalist Multi-Agent System for Solving Complex Tasks
    url: https://arxiv.org/abs/2411.04468
    type: primary
  - title: Why Do Multi-Agent LLM Systems Fail? (MAST)
    url: https://arxiv.org/abs/2503.13657
    type: primary
  - title: Semantic Kernel overview
    url: https://learn.microsoft.com/en-us/semantic-kernel/overview/
    type: secondary
---

多 agent 失败要先检查两件事：是否陷入循环，以及是否把失败当作成功。比如执行器超时，评论员却根据摘要写「测试已绿」，后续角色再把这句话当事实，团队就会在错误状态上继续推进。

AutoGen 用对话编排，背景见 `msft-autogen`；Magentic-One 增加 Task Ledger / Progress Ledger，MAST 将失败归到规格、协调、验证几类；Semantic Kernel 管插件边界。这里讨论公开设计和失败模式，不作为真题记录，通用运行环境见 `design-agent-harness`。

## 状态和停止条件交给宿主

Coder 反复「请再审」，Reviewer 回「很好再改一版」，没有 `max_round` 就会不断耗 TPM，见 `msft-azure-tpm`。选说话者的模型还可能总选健谈角色，让该执行任务的人迟迟没机会。Magentic-One 的外环调整计划，内环检查进展；连续若干步没进展就重计划，避免一再催同一个 Web Surfer。其 GAIA 完成率也说明该设计适合用来分析失败，不能据此声称已经能自主办公。

执行结果以退出码、CI、工单字段等系统记录为准，见 `msft-semantic-kernel`。Complimentary 幻觉指角色互证成功，无新证据仍给通过。做 RL 或在线采样时，奖励应来自测试、文件 diff、API 幂等结果；另一个 LLM 的成功评价可能直接强化这类互捧。任务成功与越权分别计数，见 `amazon-agent-eval`，还要查角色是否使用了别人的工具。

轮数、token、实际耗时用宿主硬限制，写操作默认不自动重试：

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

Ledger 只保存计划与证据指针，每轮复制所有聊天会让上下文不断增大，见 `msft-long-context`。Copilot 的仓库循环也需要同类限制，见 `msft-copilot-agent`。

## 分开记录完成与失败

评测分别统计真完成、预算终止、工具失败后的幻觉率、重复副作用，以及评论员无新证据仍通过的次数。GroupChat 若直接连生产邮箱，循环可能不断发信；权限应绑定工具运行时，prompt 不能代替 ACL。

## 追问

**两个 agent 不够，要加到五个吗？**
先判断新增角色是否覆盖独立工具界面或必要复核。每个角色都会增加通信与误调用成本。

**什么时候单 agent 更合适？**
单 agent 加明确 schema 已能完成时就用它。多 agent 的收益应来自界面隔离或显式复核。

**人在什么位置介入？**
计划确认、不可逆动作和预算耗尽后的降级，介入点应预先定义。

**框架改名后这些分析还适用吗？**
适用。对话编排、插件边界、状态核验和预算都是独立于包名的设计问题。

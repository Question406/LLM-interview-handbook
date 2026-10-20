---
id: msft-agent-rl
section: microsoft
order: 20
level: A
title: Microsoft：多 agent 失败，循环、互相吹捧幻觉、预算？
quick: "多 agent 常见翻车：停不下来，以及以为自己停对了。循环要硬顶轮数 / token 数 / 实际耗时。Complimentary 幻觉是角色互相捧场，把失败说成成功。不要用「对方说完成了」当 强化学习（RL） 奖励。"
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

微软 Agent 岗在 `msft-autogen` 之后会追问失败。公开材料：AutoGen 把对话当编排；Magentic-One 用 Task Ledger / Progress Ledger；MAST 论文把多智能体失败收成规格、协调、验证几类。产品侧 Semantic Kernel 管插件边界。本题收 **循环、互相吹捧、预算**，不当成真题记录。通用 harness 见 `design-agent-harness`。

## 三种停不下来

1. **对话循环。** Coder「请再审」，Reviewer「很好再改一版」，`max_round` 没设就烧 TPM，见 `msft-azure-tpm`。选下一个说话者的模型喜欢最健谈的那个，该动手的那个反而排不上。
2. **互相吹捧幻觉。** 不是对用户拍马，是 agent 之间互证成功：执行器超时，评论员根据自然语言摘要写「测试已绿」。下一轮当事实。状态必须以系统记录为准：退出码、CI、工单字段，见 `msft-semantic-kernel`。MAST 里大量失败是验证缺失；规划再长也救不了。
3. **预算幻觉。** 模型说「再试一次就能好」。没有硬顶就会在工具抖动里空转。写操作默认不自动重试。

Magentic-One 值得搬上白板：外环改计划，内环问「这一步有没有进展」。连续若干步无进展就重计划，别再催同一个 Web Surfer。GAIA 完成率论文写得很一般，用它当失败框架，不要当「已经能自主办公」。

## 奖励不能是「看起来完成」

若做强化学习或线上采样，奖励必须绑环境：测试通过、文件 diff、API 幂等成功。用另一个 LLM 的「成功」当奖励，就是在训练 complimentary 幻觉。`amazon-agent-eval` 同一句：任务成功和越权要分开计。多 agent 还要加：角色是否越权用了别人的工具箱。

预算写在宿主：

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

上下文不要每轮粘全部聊天。Ledger 只留计划和证据指针，见 `msft-long-context`。Copilot 仓库循环同一套顶，见 `msft-copilot-agent`。

评测拆：真完成、预算终止、工具失败后的幻觉率、重复副作用、角色互捧次数（评论员在无新证据时仍给通过）。不要只报任务完成率。

常见误区是：加人就当更强；把 GroupChat 接到生产邮箱；RL 优化「对话看起来像成功」。权限绑工具运行时，不绑 输入提示（prompt）。

## 追问

- **两个 agent 不够为什么加到五个？** 每增加一个 Agent，就会增加通信开销和误调用风险。角色要覆盖一种工具界面，人多本身不加分。
- **和单 agent 带工具比？** 单 agent + 好 字段和类型规范（schema） 能做的，不要上 GroupChat。多 agent 只在隔离的工具界面或显式复核时划算。
- **人放哪？** 计划确认、不可逆动作、预算打满后的降级。不要让人去当下一轮 speaker 来「感觉还可以」。
- **AutoGen 改名了还能这么答吗？** 能。抽象没变：对话编排 vs 插件中间件。失败模式不随包名消失。

---
id: msft-autogen
section: microsoft
order: 12
level: A
title: Microsoft：AutoGen / 多 agent 编排，失败、预算、和 SK 差别
quick: >-
  AutoGen 把对话当编排：多个可对话 agent 互发消息。失败典型是互相捧场死循环、工具抛错被当成成功、token 账单爆炸。预算要硬顶（轮数、token、墙钟、写操作）。和 Semantic Kernel 的差别是：SK 管插件边界和中间件，AutoGen 管多智能体怎么说话。
tags:
  - Microsoft
  - AutoGen
  - Agent
  - Orchestration
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
  - title: Semantic Kernel overview
    url: https://learn.microsoft.com/en-us/semantic-kernel/overview/
    type: primary
---

## 题怎么来的

微软应用 / Agent 岗现在很少只问「你会不会 ReAct」。公开材料里 AutoGen（Wu 等人，多智能体对话）把 agent 定义成可对话对象：LLM、人、工具可以组合；Magentic-One 在这上面加了 Orchestrator、Task Ledger、Progress Ledger。产品侧 Semantic Kernel 是插件、过滤器和 planner。评委要听 **编排模型、失败合同、预算**，不是背 class 名。SDK 还在从 0.2 group chat 迁到 Agent Framework，别把过时 API 当架构。`realInterview: false`。

## 和 SK 不是同一个抽象

我会先画两条线，避免「微软有两个 agent 框架所以都讲一遍」：

| | Semantic Kernel | AutoGen / Magentic-One |
| --- | --- | --- |
| 单位 | 插件函数 + 一次模型调用 | 多个 conversable agent |
| 控制 | filter / 中间件拦调用 | 对话策略、选下一个说话者 |
| 身份 | 用户 token 向下传到 Graph | 每个 agent 自己的工具箱，更容易漏 ACL |
| 产品位 | Copilot 式企业插件运行时 | 研究 / 复杂任务的多智能体实验床 |

SK 的核心契约在 `msft-semantic-kernel`：原生函数有副作用，语义函数只产文本；写操作要确认；失败要结构化回给模型。AutoGen 默认是 **模型在跟另一个模型聊天**。没有 filter，一次「看起来像成功的」自然语言就会把错误放大成下一轮的事实。

不是谁取代谁。企业助手常常是 SK（或后来的 Agent Service）做工具边界，必要时再开一个有预算的子团队去跑 Magentic-One 那种「写代码 + 逛网页」。把 GroupChat 直接接到生产邮箱 API 上，是在请死循环发信。

## 失败模式：循环、幻觉成功、权限漂移

多智能体最常见的不是「不够聪明」，是 **停不下来** 和 **以为自己停对了**。

1. **捧场循环。** Coder 说「请再审一下」，Reviewer 说「很好再改一版」，`max_round` 没设就烧 TPM。选 speaker 的模型喜欢找最健谈的那个，不是最该动手的那个。
2. **工具失败当成功。** 代码执行超时，agent 用自然语言总结「已经跑过了」。下一轮当测试绿。收口必须和 SK 同一句：状态以系统记录为准，见 `msft-semantic-kernel`。
3. **权限漂移。** Web Surfer 用应用身份；Coder 在沙箱里读到密钥。多 agent 要把 ACL 绑在 **工具运行时**，不要绑在 prompt「请尊重权限」。接地规则同 `msft-copilot-ground`。
4. **上下文膨胀。** 每轮把全部聊天粘回去，$T$ 线性涨，TPM 和 lost-in-the-middle 一起爆，见 `msft-azure-tpm`、`msft-long-context`。Ledger 存在的意义就是别把小说当状态。

Magentic-One 公开设计值得搬上白板：外环改 Task Ledger（计划），内环改 Progress Ledger（这一步有没有进展）。连续若干步没进展就重计划，而不是再催一次同一个 Web Surfer。GAIA / WebArena 上的完成率论文写得很一般（百分之三十几量级），面试用它当 **失败分析框架**，不要当「已经能自主办公」。

## 预算是硬顶，写在运行时里

我会把预算写成宿主代码，不写在 system prompt 里「请节约」：

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

再加两条产品规则：只读工具可自动；写、发、删、付款必须确认或幂等键，默认不重试。评测不要只报任务完成率：「编造成功」会变成正例。要拆：真完成、预算终止、工具失败后的幻觉率、重复副作用次数。和 `design-agent-harness` 同一套：工具类型、沙箱、钱和步数的硬顶。

## 追问

- **两个 agent 不够为什么加到五个？** 每加一个就多一份对话税和一份误调。Magentic-One 的消融是「这个角色是否覆盖一种工具界面」，不是人多力量大。
- **和单 agent 带工具比？** 单 agent + 好 schema 能做的，不要上 GroupChat。多 agent 只在需要隔离的工具界面（浏览器 vs 终端）或需要显式复核时才划算。
- **人在回路放哪？** 计划确认、不可逆动作、预算打满后的降级。不要让人去当下一轮 speaker 来「感觉还可以」。
- **AutoGen 0.4 改名了还能这么答吗？** 能。抽象没变：对话编排 vs 插件中间件。改的是包名，不是失败模式。

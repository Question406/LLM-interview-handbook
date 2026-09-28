---
id: align-tool-rl
section: alignment
order: 23
level: A
title: 对齐：只对工具成功给奖，还是逐步过程奖
quick: >-
  只奖「任务做成」最贴目标，但工具环上几十步全是 0，学不动。逐步奖 schema、返回码、检索命中，密但会刷工具次数。
  主信号仍是终局成功；过程分只能来自环境可观察事件，不能来自「CoT 好看」。
tags:
  - OpenAI
  - Anthropic
  - Tools
  - RL
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Let's Verify Step by Step
    url: https://arxiv.org/abs/2305.20050
    type: primary
  - title: Function calling
    url: https://platform.openai.com/docs/guides/function-calling
    type: primary
  - title: Building effective agents
    url: https://www.anthropic.com/engineering/building-effective-agents
    type: primary
---

OpenAI function calling、Anthropic 的工具循环、Microsoft Copilot 都会把「工具 RL 奖什么」问出来。Let's Verify 讲的是数学步骤；工具环同构：终局 0/1 太稀，中间分太密就换目标。过程监督总论见 `align-process-reward`；稀疏信用见 `align-agent-rl`。生产执行契约见 `design-tool-prod`，本题只谈**训练信号**。

## 两种奖，优化的不是同一件事

**只奖成功。** $r=1$ 当且仅当任务金标达成（单测绿、工单关闭、WebArena 终态）。工具 200、schema 合法都不给分。优点：Goodhart 缝窄，模型不会靠「多调两次搜索」混分。缺点：中间全 0，探索要靠演示、课程、或很大 $G$。

**逐步过程奖。** 例如 JSON 能 parse、必填字段在、宿主返回非错误、检索块被引用、沙箱没超时。写成

$$
r=r^{\mathrm{out}}+\lambda\sum_k s_k,
$$

$\lambda$ 一大，策略会最大化 $\sum s_k$：无必要调用、重复查询、把同一 API 拆成十次。$r^{\mathrm{out}}$ 变成装饰。面试先说：过程奖是 shaping，不能替代任务成功。

更阴的一种：奖「调用了工具」而不是「调用对了」。trace 里出现 tool 块就加分，模型学会每轮都调，观察当噪音读。正确的过程事件是环境可观测的：返回码、单测断言、是否改到了目标文件。人读 CoT 打的「这一步有用吗」噪声大，且不可复现。

```python
def tool_reward(task_ok, events, lam=0.05):
    # events: schema_ok, http_ok, used_in_answer — 都来自宿主，不来自 CoT
    shape = 0.3 * events["schema_ok"] + 0.3 * events["http_ok"] + 0.4 * events["used"]
    return float(task_ok) + lam * shape
```

$\lambda$ 从小扫。曲线要同时看任务成功率、平均调用次数、无调用成功率。调用次数涨、任务不动，就是在刷 $s_k$。

## 怎么选

能规则核验的中间态优先规则，不要训一个工具 PRM。开放网页没有 oracle，过程分更容易变成「像会用浏览器」。搜索时可用过程分做启发式、outcome 做终局门禁，比把过程分直接加成奖励安全，和数学 PRM 同一句。

和 RFT 的关系：grader 可以只看终局，也可以看 trace 约束（禁止某工具、必须引用）。约束是政策，不是稠密 shaping。政策用硬规则在宿主执行，见 `design-agent-harness`；RL 里再学一次「别调用」又慢又脆。

失败模式：工具失败自动重试被当成过程分（失败也有返回码）；确认框点了才执行，训练却在模拟器里默认确认，线上全卡确认；只奖 200，模型对错误站点也「成功调用」。评测要把模拟器版本钉死，见 `design-eval-agent`。

## 追问

- **为什么不把每次成功调用都设成 1？** 任务可能零次调用就能答。奖调用就是在惩罚「该停」。
- **schema 合法能不能当主奖励？** 不能。合法参数可以是错对象、错金额。金额走确认框，训练金标仍是业务结果。
- **$\lambda$ 怎么定？** 扫到过程分涨而 $r^{\mathrm{out}}$ 不掉的区间；掉了就减小或改成仅搜索启发式。
- **和 GRPO 冲突吗？** 不冲突。GRPO 管 baseline；$r$ 的定义是本题。组内若过程分把大家都抬成同一个数，优势照样为零。

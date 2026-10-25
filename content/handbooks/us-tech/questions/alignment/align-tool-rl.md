---
id: align-tool-rl
section: alignment
order: 23
level: A
title: 对齐：只对工具成功给奖，还是逐步过程奖
quick: "工具 RL 以任务最终成功为主奖励，再给可可靠检查的中间事件少量过程分。比如参数合法、HTTP 成功可以辅助学习，但不能代替工单真的处理完；否则模型可能靠重复调用刷分。"
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

我会以任务终局成功为主奖励，再用少量、可检查的过程分帮助探索。例如 HTTP 200 只说明接口返回成功，工单是否真的关闭，还得查业务终态。只奖终局时信号可能太稀；过程分太重，又会让模型追求调用次数。工具循环和 Let's Verify 中的步骤监督都有这个取舍。

## 两种信号各解决什么问题

只奖成功时， $r=1$ 当且仅当任务金标达成（单测绿、工单关闭、WebArena 终态）。工具 200、字段和类型规范（schema） 合法都不给分。优点：可供模型钻评分规则空子的空间较小，模型不会靠「多调两次搜索」混分。缺点：中间全 0，探索要靠演示、课程、或很大 $G$。

过程分可以来自 JSON 能否 parse、必填字段是否齐全、宿主是否返回非错误、检索块是否被引用，以及沙箱是否超时。把它加到终局奖励上，可以写成

$$
r=r^{\mathrm{out}}+\lambda\sum_k s_k,
$$

$\lambda$ 一大，策略会最大化 $\sum s_k$：无必要调用、重复查询、把同一 API 拆成十次。$r^{\mathrm{out}}$ 变成装饰。所以过程奖只做 shaping，任务成功仍要单独检查。

另一种更隐蔽的问题：奖「调用了工具」而不是「调用对了」。trace 里出现 tool 块就加分，模型学会每轮都调，却不认真利用工具返回的结果。正确的过程事件是环境可观测的：返回码、单测断言、是否改到了目标文件。人读 思维链（CoT，即分步推理过程） 打的「这一步有用吗」噪声大，且不可复现。

```python
def tool_reward(task_ok, events, lam=0.05):
    # events: schema_ok, http_ok, used_in_answer — 都来自宿主，不来自 CoT
    shape = 0.3 * events["schema_ok"] + 0.3 * events["http_ok"] + 0.4 * events["used"]
    return float(task_ok) + lam * shape
```

$\lambda$ 从小值开始逐步试验。曲线要同时看任务成功率、平均调用次数、无调用成功率。调用次数涨、任务不动，就是在刷 $s_k$。

## 怎么接入训练和评测

能用规则核验的中间状态，优先用规则。开放网页没有 oracle 时，学习到的工具 PRM 容易只奖励「看起来会用浏览器」。也可以让过程分只做搜索启发式，outcome 做终局门禁，减少它改变训练目标的风险。

和 RFT 的关系：grader 可以只看终局，也可以看 trace 约束（禁止某工具、必须引用）。约束是政策，不是稠密 shaping。政策用硬规则在宿主执行，见 `design-agent-harness`；只靠强化学习（RL）让模型学会「别调用」，收敛慢且容易失效。

评测要检查工具失败重试是否也拿了过程分，确认框是否在模拟器里被默认跳过，以及模型有没有对错误站点拿到 200。模拟器版本要固定，否则训练和线上契约可能不一致。

相关：`align-process-reward`、`align-agent-rl`、`design-tool-prod`、`design-eval-agent`。

## 追问

**为什么不把每次成功调用都设成 1？**
任务可能零次调用就能答。奖调用就是在惩罚「该停」。
**schema 合法能不能当主奖励？**
不能。合法参数可以是错对象、错金额。金额走确认框，训练金标仍是业务结果。
**$\lambda$ 怎么定？**
扫到过程分涨而 $r^{\mathrm{out}}$ 不掉的区间；掉了就减小或改成仅搜索启发式。
**和 GRPO 冲突吗？**
不冲突。GRPO 管 baseline；$r$ 的定义是本题。组内若过程分把大家都抬成同一个数，优势照样为零。

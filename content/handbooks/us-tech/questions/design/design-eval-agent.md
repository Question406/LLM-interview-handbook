---
id: design-eval-agent
section: design
order: 20
level: S
title: 设计：Agent 评测平台——任务图、重放、非确定性
quick: >-
  Agent 对错不是一条字符串匹配。任务是图：子目标、工具副作用、终态检查。重放必须钉死模拟器、种子、工具夹具。
  模型采样、网页、时钟三路随机要拆开报，否则成功率不可比。通用 LLM 评测见 `design-eval-platform`。
tags:
  - Evals
  - Agent
  - OpenAI
  - Anthropic
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: WebArena — A Realistic Web Environment for Building Autonomous Agents
    url: https://arxiv.org/abs/2307.13854
    type: primary
  - title: openai/evals
    url: https://github.com/openai/evals
    type: secondary
  - title: Building effective agents
    url: https://www.anthropic.com/engineering/building-effective-agents
    type: primary
---

OpenAI / Anthropic / Google 的 agent 岗会问「你怎么知道新 harness 能发」。WebArena 把指标写成功能成功；GitHub evals 只是 runner。白板要的是任务图、可重放、把非确定性关进笼子。污染和 A/B 纪律见 `design-eval-platform`；浏览器环境见 `design-browser-agent`。

## 任务是图，不是一道题的 BLEU

每条 case 有起始状态、允许工具、金标终态、以及可选的中间节点（必须访问某页、必须调用某只读工具、禁止调用支付）。成功可以是终态谓词，进度可以是图上覆盖的节点比例。只报「最后一句像不像」会把会说话不会干活的策略选上去。

节点类型要写进 schema：`assert_state`（数据库/页面）、`assert_tool`（曾经以合法参数调用）、`forbid_tool`、`human_grade`。可验证节点走程序；价值判断走人和指南。RFT 的 grader 应对着同一份 schema，见 `align-rft`。

```python
def score(trace, graph):
    hit = {n.id for n in graph.nodes if n.check(trace)}
    if graph.forbid & hit:
        return 0.0, "policy"
    if graph.terminal.check(trace):
        return 1.0, "success"
    return len(hit & graph.partial) / max(len(graph.partial), 1), "partial"
```

部分分用来诊断，发版门禁仍以终态 + 政策违规为主。平均步数、美元成本、p95 墙钟、确认取消率一起上表，否则「更成功」来自贵 10 倍的乱试。成本写「USD / 任务」，不要在文里用货币符号。

## 重放：没有夹具就没有回归

一次失败要能在同一 `eval_set@sha`、`env@sha`、`tools@sha`、解码参数下重跑。工具走模拟器或录制的 fixture（HTTP 磁带、浏览器快照），禁止评测作业打真实支付。时钟注入；随机数种子单独列。Web 若必须活网，报告里写「活网」并当成不同实验，不要和冻结环境比小数点。

Trace 存：模型消息、工具名与参数、工具结果哈希、截屏或无障碍树、预算剩余、用户确认。重放模式：严格（比特级工具响应）和宽松（只重放到分叉点）。严格用于回归；宽松用于「模型变了之后旧磁带对不上」的分析。

污染：把评测站点写进训练博客、把 fixture HTML 喂进预训练，都会让 WebArena 类分数虚高。Canary 页面和 n-gram 扫训练集，见 `align-eval-contam`。评测日志回流训练前必须换 held-out 图。

## 非确定性要拆开报

三路噪声：

1. **策略。** 温度、top-p、隐藏思考预算。对比模型时钉死；要报方差就多次采样，写均值和分位数，不要一次 rollouts 定生死。
2. **环境。** 广告、A/B、时间、检索索引。用冻结镜像消灭；消灭不了就当不同环境版本。
3. **基础设施。** 超时、限流、工具 5xx。重试策略要算进成本，且评测里应对失败注入，看会不会死循环。

LLM-as-judge 打「轨迹漂不漂亮」只能当筛子。主指标是功能谓词。Judge 会偏长轨迹和会道歉的失败，见 `align-llm-judge`。发布表：冻结环境成功率、活网抽查、安全违规、成本、延迟、污染报告。缺一项不能发。

## 追问

- **温度 0 就确定了吗？** 没有。并列 token、工具时间、隐藏预算仍会漂。环境不冻，温度 0 也不可比。
- **为什么要任务图而不是一个布尔？** 布尔太稀，调不了 harness。图上的部分分告诉你是检索挂了还是最后确认挂了。
- **模拟器会不会过拟合？** 会。定期用活网抽查和人红队打假绿，见 `align-red-team`。
- **和离线 chat eval 能否共用平台？** 共享血缘、权限、污染扫描；执行器、超时、夹具是 agent 专用列。

---
id: design-eval-agent
section: design
order: 20
level: S
title: 设计：Agent 评测平台——任务图、重放、非确定性
quick: >-
  我会用任务图检查子目标、工具副作用和最终状态，再固定模拟器、随机种子及模拟或录制的工具响应来重放。模型
  sampling、网页环境和时钟等随机性要分开报告，成功率才有可比性；通用 LLM 评测见 `design-eval-platform`。
tags:
  - Evals
  - Agent
  - OpenAI
  - Anthropic
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: WebArena — A Realistic Web Environment for Building Autonomous Agents
    url: 'https://arxiv.org/abs/2307.13854'
    type: primary
  - title: openai/evals
    url: 'https://github.com/openai/evals'
    type: secondary
  - title: Building effective agents
    url: 'https://www.anthropic.com/engineering/building-effective-agents'
    type: primary
---

## 题目描述

本题是手册归纳的系统设计练习。流量、数据量和具体 SLO 未给定时，请先列出可调整的假设，不把假设当成已披露事实。

### 场景与目标

设计评估 agent 是否真正完成任务的平台。待测 agent 可能浏览网页、调用工具或修改环境，仅凭最终回复不足以判断成功。

### 需要满足的功能

- 接收带起始环境、允许动作、目标状态和禁止行为的测试任务，运行并生成判定。
- 记录并重放模型、工具和环境交互，用于定位失败。
- 汇总成功率、进度、违规、调用次数、时延和费用，并比较不同版本。

### 约束与交付物

需要区分可程序验证的终态、人工判断与随机性，明确重复运行和环境版本变化的定义。达到目标但越权执行的轨迹不能被当成正常成功。

请说明 scope 和 constraints、对外接口及返回语义、核心数据对象、主要请求的完整生命周期、故障与恢复行为，以及能验证设计是否达标的指标。题目不预先指定数据库、模型或调度算法；需要解释自己作出的选择与代价。

### 请求与结果示例

任务要求查询订单但禁止支付，即使 agent 最后回答正确，只要轨迹中出现未经授权的支付操作，评测仍应给出违反约束的结果与证据。

## 可以这样回答

我会用任务图检查 agent 是否完成了目标，再用固定环境和工具响应重放失败。比如最后一句说任务完成了，支付工具却被违规调用，最终仍应判失败。WebArena 用功能成功来评分，GitHub evals 提供 runner；完整平台还要记录环境、工具和 sampling 的版本，才知道新 harness 的变化来自哪里。

这类设计适用于 OpenAI / Anthropic / Google 的 agent 评测方向。污染和 A/B 方法见 `design-eval-platform`；浏览器环境见 `design-browser-agent`。

## 技术备查

## 解题思路与参考答案

我会用任务图检查 agent 是否完成了目标，再用固定环境和工具响应重放失败。比如最后一句说任务完成了，支付工具却被违规调用，最终仍应判失败。WebArena 用功能成功来评分，GitHub evals 提供 runner；完整平台还要记录环境、工具和 sampling 的版本，才知道新 harness 的变化来自哪里。

这类设计适用于 OpenAI / Anthropic / Google 的 agent 评测方向。污染和 A/B 方法见 `design-eval-platform`；浏览器环境见 `design-browser-agent`。

## 把目标和失败条件写成任务图

每条 case 有起始状态、允许工具、金标终态、以及可选的中间节点（必须访问某页、必须调用某只读工具、禁止调用支付）。成功可以是终态谓词，进度可以是图上覆盖的节点比例。只报「最后一句像不像」会把会说话不会干活的策略选上去。

节点类型要写进字段和类型规范（schema）：`assert_state`（数据库/页面）、`assert_tool`（曾经以合法参数调用）、`forbid_tool`、`human_grade`。可验证节点走程序；价值判断走人和指南。RFT 的 grader 应对着同一份 schema，见 `align-rft`。

```python
def score(trace, graph):
    hit = {n.id for n in graph.nodes if n.check(trace)}
    if graph.forbid & hit:
        return 0.0, "policy"
    if graph.terminal.check(trace):
        return 1.0, "success"
    return len(hit & graph.partial) / max(len(graph.partial), 1), "partial"
```

部分分用来诊断，release criteria 仍以终态 + 政策违规为主。平均步数、美元成本、p95 实际耗时、确认取消率一起上表，否则「更成功」来自贵 10 倍的乱试。成本写「USD / 任务」，不要在文里用货币符号。

## 固定重放条件，再区分随机性

一次失败要能在同一 `eval_set@sha`、`env@sha`、`tools@sha`、decoding 参数下重跑。工具走模拟器或录制的 fixture（HTTP 磁带、浏览器快照），禁止评测作业打真实支付。时钟注入；随机数种子单独列。Web 若必须活网，报告里写「活网」并当成不同实验，不要和冻结环境比小数点。

Trace 存：模型消息、工具名与参数、工具结果哈希、截屏或无障碍树、预算剩余、用户确认。重放模式：严格（比特级工具响应）和宽松（只重放到分叉点）。严格用于回归；宽松用于「模型变了之后旧磁带对不上」的分析。

污染：把评测站点写进训练博客、把 fixture HTML 喂进预训练，都会让 WebArena 类分数虚高。Canary 页面和 n-gram 扫训练集，见 `align-eval-contam`。评测日志加入 training data 前必须换 held-out 图。

三路噪声：

1. **策略。** 温度、top-p、隐藏思考预算。对比模型时固定这些设置；要报方差就多次 sampling，写均值和分位数，不要一次 rollouts 定生死。
2. **环境。** 广告、A/B、时间、检索索引。用冻结镜像消灭；消灭不了就当不同环境版本。
3. **基础设施。** 超时、限流、工具 5xx。重试策略要算进成本，且评测里应对失败注入，看会不会死循环。

LLM-as-judge 打「轨迹漂不漂亮」只能当筛子。主指标是功能谓词。Judge 会偏长轨迹和会道歉的失败，见 `align-llm-judge`。发布表：冻结环境成功率、活网抽查、安全违规、成本、延迟、污染报告。缺一项不能发。

## 追问

**温度 0 就确定了吗？**
没有。概率接近的候选 token、工具时间、隐藏预算仍会漂。环境不冻，温度 0 也不可比。
**为什么要任务图而不是一个布尔？**
布尔太稀，调不了 harness。图上的部分得分能说明是检索失败，还是最后确认失败。
**模拟器会不会 overfitting？**
会。定期用实时网页抽查和人工红队发现虚假的通过结果，见 `align-red-team`。
**和离线 chat eval 能否共用平台？**
共享血缘、权限、污染扫描；执行器、超时、夹具是 agent 专用列。

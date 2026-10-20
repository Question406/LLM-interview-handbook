---
id: dt-tool-apigen
section: posttrain-data
order: 9
level: S
title: 工具调用合成：Gorilla / ToolLLM / APIGen 这类管线，grader 是什么？
quick: "先用机器可读的 API schema 合成请求、调用和参数，再分层验证：JSON 能解析，工具存在，参数符合类型与范围，能执行的调用确实执行成功。只训练 JSON 格式而不运行环境，模型可能会调用接口，却编造「已添加」等结果。"
companies:
  - apple
tags:
  - Apple
  - Tool Use
  - Synthetic Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "Gorilla: Large Language Model Connected with Massive APIs"
    url: https://arxiv.org/abs/2305.15334
    type: primary
  - title: ToolLLM
    url: https://arxiv.org/abs/2307.16789
    type: primary
  - title: "APIGen: Automated Pipeline for Generating Verifiable Function-Calling Datasets"
    url: https://arxiv.org/abs/2406.18518
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

先确定 grader 要检查什么：工具是否选对，参数是否符合 schema，能执行的调用是否实际成功。只对 JSON 计算交叉熵损失（CE）而不运行环境，模型可能只学会接口格式。

只记接口格式的模型，在产品 schema 变化后可能失效，见 `dt-tool-alias`。只到 schema 层，模型会编造「已添加」。Gorilla 从 API 文档出调用数据，评测看能不能打到对的 API。ToolLLM 大规模 REST 工具，DFS 搜轨迹。APIGen 用层级检查滤合成垃圾。

苹果公开的工具平台结合执行环境和人工修改、回滚；这些论文讨论的是自动化方案。用户日志不进基础模型。面试把 grader 说清楚就够。

## 三层 grader，由便宜到贵

1. 结构。JSON 可解析、工具名在目录里、必填字段在。不过这一层的，直接扔。
2. Schema。类型、枚举、范围。字符串日期能不能 parse。APIGen 公开把这层当硬门。
3. 执行。无状态计算器、检索是否命中 id、有状态日历是否写入。AFM 场景也需要检查实际执行结果。只到第 2 层，模型会编造「已添加」。

Toolformer 是另一头：在普通文本里插 API 调用，看调用是否降低困惑度。那是预训练味道。后训练工具数据要有用户意图和最终回复。

负例：目录里没有能用的工具仍调用，见 `dt-tool-irrelevance`。合成正例堆得越多，越要配这些负例，否则变成见题就调。

## 文档当种子

Gorilla 用 API 文档。文档过时，数据就过时。schema 版本进 lineage，和轨迹绑在一起，见 `dt-traj-quality`。从过期文档合成的「正确调用」，在新产品上是错的。

## 追问

- **BFCL 能当训练集吗？** 评测留下。同族约束可以叠到自己的 mix，见 `dt-ifeval-overlay` 的同类纪律。
- **多 API 供应商？** 别名评测要有，训练示范长得像产品 schema，见 `dt-tool-alias`。
- **合成 query 谁来写？** 教师可以写，人抽查意图是否真需要这个工具。空转调用（能直接答还调）要标出来。

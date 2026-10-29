---
id: dt-tool-apigen
section: posttrain-data
order: 9
level: S
title: tool calls 合成：Gorilla / ToolLLM / APIGen 这类 pipeline，grader 是什么？
quick: >-
  grader 是由便宜到贵的三层检查：JSON 能解析、工具存在、必填字段齐全；参数符合 schema 的类型、枚举和范围；能执行的调用真的执行成功。只训
  JSON 格式、不跑环境，模型学会了接口长什么样，却会编造「已添加」这类结果，schema 一变也容易失效。
companies:
  - apple
tags:
  - Apple
  - Tool Use
  - Synthetic Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: 'Gorilla: Large Language Model Connected with Massive APIs'
    url: 'https://arxiv.org/abs/2305.15334'
    type: primary
  - title: ToolLLM
    url: 'https://arxiv.org/abs/2307.16789'
    type: primary
  - title: >-
      APIGen: Automated Pipeline for Generating Verifiable Function-Calling
      Datasets
    url: 'https://arxiv.org/abs/2406.18518'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

grader 分三层，由便宜到贵：先看结构（JSON 能解析、工具在目录里），再看 schema（参数类型、枚举、范围对不对），最后看执行（能执行的调用是否真的成功）。只对 JSON 计算 cross-entropy 损失（CE）、不运行环境，模型可能只学会了接口格式。

只学会格式会出什么事，看一个例子。用户说「把明天的会加到日历」，模型输出一个格式完美的添加调用，回复「已添加」，日历里却什么也没有。检查只到 schema 层，模型就会编造这类结果，因为它从没被要求真的完成操作。这样的模型 schema 一变也可能失效，见 `dt-tool-alias`。

三篇公开工作各管一段。Gorilla 从 API 文档生成调用数据，评测看能不能调到正确的 API。ToolLLM 用大规模 REST 工具，靠 DFS 搜索 trajectories。APIGen 用层级检查过滤掉合成出来的垃圾数据。

## 三层 grader 怎么搭

最便宜的一层查结构：JSON 可解析、工具名在目录里、必填字段都在，不过的直接扔。第二层查 schema 的类型、枚举、范围，比如字符串形式的日期能不能 parse，APIGen 公开把这一层当必须满足的验收条件。第三层看执行，无状态的计算器看结果，检索看是否命中对的 id，有状态的日历看是否真的写入。

正例够了之后还要配负例：目录里没有合适的工具时，模型仍然去调用，见 `dt-tool-irrelevance`。合成正例堆得越多，越需要这类负例，否则模型会变成见题就调。

和这些方案对照，Toolformer 走的是另一头：在普通文本里插入 API 调用，看调用能不能降低 perplexity，更接近 pre-training 的做法。post-training 的工具数据要有用户意图和最终回复。

## 追问

**用 API 文档当 seed 有什么隐患？**
文档过时，数据也就过时。Gorilla 用 API 文档当 seed，从过期文档合成的「正确调用」，放到新产品上就是错的。所以 schema 版本要进 lineage，和 trajectories 绑在一起，见 `dt-traj-quality`。

**BFCL 能当 training set 吗？**
不能，评测要留着。可以把同类约束叠加到自己的 mix 里，纪律和 `dt-ifeval-overlay` 一样。

**有多家 API 供应商怎么办？**
要有别名评测，训练示范要长得像实际部署时的 schema，见 `dt-tool-alias`。

**合成 query 由谁来写？**
teacher model 可以写，但要有人抽查这个意图是否真的需要这个工具。重复执行但没有推进任务调用（明明能直接回答还去调用）要标出来。

相关：`dt-tool-alias`、`dt-tool-irrelevance`、`dt-traj-quality`

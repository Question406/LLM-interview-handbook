---
id: xai-tool-use
section: xai
order: 14
level: A
title: xAI：Grok tool use / function calling 的公开层工程约束
quick: >-
  公开 API 分内置工具（服务端执行：搜网、搜 X、代码解释器等）和自定义函数（模型只出
  schema 调用，你在本地跑）。工程约束是：JSON schema 要硬、并行调用要幂等、写操作要确认、轮数和
  token 要封顶。不要编内部路由器或未文档化的隐藏工具。
tags:
  - xAI
  - Grok
  - Function Calling
  - Tools
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: xAI function calling
    url: https://docs.x.ai/docs/guides/function-calling
    type: primary
  - title: xAI tools overview
    url: https://docs.x.ai/docs/agents/tools
    type: primary
  - title: Grok 3 Beta — The Age of Reasoning Agents
    url: https://x.ai/blog/grok-3
    type: primary
  - title: Open Release of Grok-1
    url: https://x.ai/news/grok-os
    type: primary
---

## 题怎么来的

xAI 应用 / Agent 岗问 Grok 怎么接工具。公开层只有文档里的两类：内置工具在 xAI 侧执行（网页搜索、X 搜索、代码解释器、图片生成、Collections 检索等，以当时文档列表为准）；function calling 由你定义 JSON Schema，模型返回 `tool_call`，你执行后再把结果塞回对话。Grok-3 博文把 DeepSearch 写成带搜索和代码解释器的 agent，没有公布路由模型和重试策略。面试讲工程约束，不编内部 planner。`realInterview: false`。

## 合同：谁执行、什么 schema、何时停

自定义函数的循环和别家一样，差别在你要主动说清边界：

1. 请求带 `tools`（名字、描述、parameters 必须是 JSON object schema）和 `tool_choice`（`auto` / `required` / `none` / 指定函数）。
2. 模型要么直接答，要么返回一个或多个 tool call（文档默认允许并行）。
3. 你本地执行，用对应 `tool_call_id` 回传结果。内置工具则是服务端跑完，响应里可能带引用。
4. 没有上限的循环会在搜索和代码解释器上把自己打崩。宿主要设最大轮数、每轮超时、总 token，和 `xai-rate-limiter` 同一道门。

Schema 工程比「模型很聪明」重要。根类型要是 object；枚举写清；必填列出。描述决定模型何时调——把「删除账号」和「搜文档」放进同一轮 `auto`，是在请误调。文档写过单请求工具数量上限（量级是上百，以当时 docs 为准），上限之内仍然要按任务裁剪列表：工具太多，选错的先验上升。

并行调用：只读可并行；有依赖（先搜再写）必须串。写操作默认不自动重试，除非带幂等键。模型并行点了两次 `create_ticket`，没有幂等就是两张单。

## 失败、副作用、和约束解码

工具失败不要变成幻觉燃料。回给模型的应是短结构化错误：`retryable`、错误码、一句 hint。权限拒绝和资源不存在禁止再调同一函数。日历超时仍说「已经约上了」，是产品事故。状态以系统记录为准。

副作用分级：

- 内置搜索 / 检索：只读，可自动，但结果当不可信输入（网页可以带注入）。截断、当数据不是指令。
- 代码解释器：沙箱、无长期密钥、CPU 配额。Grok 博文没给沙箱细节，面试讲通用约束，标明不是他们的 runbook。
- 自定义写接口：确认框或二次校验。`tool_choice=required` 只保证会调工具，不保证调对、也不保证用户同意。

结构化参数和 `msft-constrained-decode` 同一物理：JSON 合法由解码或服务端 schema 保证，比「请输出 JSON」硬。约束不管是否该调；该不该调是策略和确认。自由生成再 parse，长参数会在重试上烧配额。

系统提示里的工具语法说明是公共前缀，适合 KV 共享；每个租户允许的工具列表不同，必须在分叉之后，见 `xai-prompt-cache`。工具 schema 字段顺序不稳，前缀缓存会抖。

评测拆：工具选对率、参数合法率、误调率、写操作重复次数、工具失败后的幻觉率、引用是否指向真实搜索结果。只报「任务完成」会把「编造成功」算进正例。DeepSearch 那种长轨迹还要报步数和墙钟，避免把「搜得久」当成质量。

错法：把内置搜索说成预训练见过实时 X（搜索是推理期工具，见 `xai-grok-pretrain`）；假设 Grok 会在服务端执行你的自定义函数；为 Agent 另开一条绕过鉴权的管理员工具。

## 追问

- **内置工具和自定义函数能不能混用？** 文档允许组合。混用时更要分清执行域：搜索结果来自 xAI，数据库写入来自你。失败处理和引用格式不要写成同一条管道。
- **模型一直调同一个失败工具？** 宿主计失败次数，超过就对模型返回 `retryable=false`，控制权交还用户。不要靠 prompt「请不要循环」。
- **并行 function calling 和 MoE decode？** 产品层一次响应里多个 tool call，对 GPU 仍是一段 decode。专家碎片故事在 `xai-moe-decode`；这里要管的是下游副作用是否并行安全。
- **没有 JSON 约束能不能做工具？** 能，但不稳。公开层至少要 schema + 解析失败重试上限。生产该把合法 JSON 当硬条件，把「该不该调」当策略。

---
id: xai-tool-use
section: xai
order: 14
level: A
title: xAI：Grok tool use / function calling 的公开层工程约束
quick: "我会先分清执行域：内置搜索、代码解释器由 xAI 服务端运行，自定义函数由模型提出 tool_call、宿主执行。参数要校验，依赖调用串行，写操作确认并带幂等键；循环设轮数、超时和 token 上限，失败用结构化错误回传，不能让模型编成功。"
tags:
  - xAI
  - Grok
  - Function Calling
  - Tools
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-29
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
  - title: Introducing Grok Build
    url: https://x.ai/news/grok-build-cli
    type: primary
---

接 Grok 工具时，我会先区分执行域，再定义校验、重试和停止条件。例如模型并行返回两次 `create_ticket`，宿主没有幂等保护就会创建两张单。公开 API 的内置工具由 xAI 侧运行，包括网页搜索、X 搜索、代码解释器、图片生成和 Collections 检索等，以相应文档为准；自定义 function calling 则由你定义 JSON Schema，模型返回 `tool_call`，你执行并回传结果。Grok-3 只公开了带搜索和代码解释器的 DeepSearch agent，没有公开 router 或重试策略。

## 合同：谁执行、使用什么 schema、何时停

自定义函数的循环和别家一样，差别在你要主动说清边界：

1. 请求带 `tools`（名字、描述、parameters 必须是 JSON object schema）和 `tool_choice`（`auto` / `required` / `none` / 指定函数）。
2. 模型要么直接答，要么返回一个或多个 工具调用（文档默认允许并行）。
3. 你本地执行，用对应 `tool_call_id` 回传结果。内置工具则是服务端跑完，响应里可能带引用。
4. 没有上限的循环会在搜索和代码解释器上把自己打崩。宿主要设最大轮数、每轮超时、总 token 用量，和 `xai-rate-limiter` 同一道门。

Schema 工程比「模型很聪明」重要。根类型要是 object；枚举写清；必填列出。描述决定模型何时调用。把「删除账号」和「搜文档」放进同一轮 `auto`，容易导致误调。文档写过单请求工具数量上限（量级是上百，以当时 docs 为准），上限之内仍然要按任务裁剪列表：工具太多，选错的先验上升。

并行调用：只读可并行；有依赖（先搜再写）必须串。写操作默认不自动重试，除非带幂等键。模型并行点了两次 `create_ticket`，没有幂等就是两张单。

## 失败、副作用、和约束解码

工具失败后，不要让模型编造执行结果。回给模型的应是短结构化错误：`retryable`、错误码、一句 hint。权限拒绝和资源不存在禁止再调同一函数。日历超时仍说「已经约上了」，是产品事故。状态以系统记录为准。

副作用分级：

- 内置搜索 / 检索：只读，可自动，但结果当不可信输入（网页可以带注入）。截断、当数据不是指令。
- 代码解释器：沙箱、无长期密钥、CPU 配额。Grok 博文没给沙箱细节，面试讲通用约束，标明不是他们的 runbook。
- 自定义写接口：确认框或二次校验。`tool_choice=required` 只保证会调工具，不保证调对、也不保证用户同意。

结构化参数和 `msft-constrained-decode` 使用相同的机制：JSON 合法由解码或服务端 schema 保证，比「请输出 JSON」硬。约束不管是否该调；该不该调是策略和确认。自由生成再 parse，长参数会在重试上烧配额。

系统提示里的工具语法说明是公共前缀，适合 KV 共享；每个租户允许的工具列表不同，必须在分叉之后，见 `xai-prompt-cache`。工具 schema 字段顺序不稳，前缀缓存会抖。

评测时分别报告工具选对率、参数合法率、误调率、写操作重复次数、工具失败后的幻觉率，以及引用是否指向真实搜索结果。只报「任务完成」会把「编造成功」算进正例。DeepSearch 那种长轨迹还要报步数和实际耗时，避免把「搜得久」当成质量。

常见误区是：把内置搜索说成预训练见过实时 X（搜索是推理期工具，见 `xai-grok-pretrain`）；假设 Grok 会在服务端执行你的自定义函数；为 Agent 另开一条绕过鉴权的管理员工具。

2026 年的 Grok Build 和 Grok Bot 也适用同样的执行约定，只是影响范围更大。Grok Build 包含 plan/diff、subagents，以及把任务分给多个 child agents 的 workflows，公开 budget 是 128、最多 1,024。Grok Bot 在用户级云 VM 上运行，多个 Bot 共享文件和登录，所以幂等与确认也要覆盖 child agents 和这台 VM。产品地图见 `xai-spacexai-now`，循环工程见 `xai-agent-loop`。

研究 screen 回答「为什么 xAI」时，可以点名这样的循环问题：错调工具、无法验证的 patch、共享 VM 的写入冲突，再说明自己的研究如何对应。

## 追问

**内置工具和自定义函数能不能混用？**
文档允许组合。混用时更要分清执行域：搜索结果来自 xAI，数据库写入来自你。失败处理和引用格式不要写成同一条管道。

**模型一直调同一个失败工具？**
宿主计失败次数，超过就对模型返回 `retryable=false`，控制权交还用户。不要靠 输入提示（prompt）「请不要循环」。

**并行 function calling 和 MoE 逐 token 生成（decode）？**
产品层一次响应里多个 工具调用，对 GPU 仍是一段 decode。专家负载不均和小矩阵的问题见 `xai-moe-decode`；这里要管的是下游副作用是否并行安全。

**没有 JSON 约束能不能做工具？**
能，但不稳。公开层至少要 schema + 解析失败重试上限。生产该把合法 JSON 当硬条件，把「该不该调」当策略。

本卡依据公开材料整理，标记为 `realInterview: false`。

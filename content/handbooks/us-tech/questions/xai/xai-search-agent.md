---
id: xai-search-agent
section: xai
order: 17
level: A
title: xAI：实时搜索工具，时效、引用、失败怎么收？
quick: "实时问题走 `web_search` 或 `x_search`，回答里的事实与引用要能对回本次返回的 URL、帖子和时间窗。我的循环会记录查询、结果与空集，超时限流返回结构化错误、次数和 token 设上限；外部内容按不可信数据处理，搜空就说明没找到。"
tags:
  - xAI
  - Search
  - Tools
  - Citations
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-29
sources:
  - title: xAI Web Search
    url: https://docs.x.ai/developers/tools/web-search
    type: primary
  - title: xAI X Search
    url: https://docs.x.ai/developers/tools/x-search
    type: primary
  - title: xAI tools overview
    url: https://docs.x.ai/docs/agents/tools
    type: primary
  - title: Grok 3 Beta — The Age of Reasoning Agents
    url: https://x.ai/blog/grok-3
    type: primary
  - title: Workflows in Grok Build
    url: https://x.ai/news/workflows
    type: primary
---

我会让时效问题走搜索工具，并把每条事实对回本次结果。例如用户问「刚才 X 上谁说了什么」，用 `x_search` 的 handle 和时间窗过滤，不能拿参数记忆中的旧数字补。公开文档中 `web_search`、`x_search` 都由 xAI 服务端执行；Grok-3 把 DeepSearch 描述成带搜索和代码解释器的 agent，没有公开查询规划器，预训练截止见 `xai-grok-pretrain`。

## 怎样把时效和引用对齐

用户问「刚才 X 上谁说了什么」，正确路径是 `x_search`（可滤 handle、时间窗），不是靠记忆。网页新闻走 `web_search`，可 `allowed_domains` / `excluded_domains`（文档写过上限大约 5 个，以当时为准）。`enable_image_understanding` 让 agent 看搜到的图，那是额外工具调用，会加延迟和视觉预算，见 `xai-grok-vision`。

引用契约：回答里的命题要能指回这一次工具返回的 URL / 帖子 id。搜到 A 却用预训练里的旧数字，是时效幻觉。搜空了要说没找到，不要补「一般认为」。DeepSearch 长轨迹还要报步数和实际耗时，避免把「搜得久」当成质量。

对搜索失败，我会分别处理：

- 超时 / 限流：结构化 `retryable`，宿主计次数，见 `xai-rate-limiter`。不要默默再用去年的参数记忆。
- 空结果：对模型返回空集，禁止「根据我的知识」。
- 注入：网页和帖子正文是不可信输入。截断、当数据不当指令，见 `xai-tool-use`。
- 引用漂：UI 展示的链接必须是工具结果里的，不能模型现编一个看起来像的 URL。

`from_date` / `to_date` 是 X 搜索的公开旋钮。评测要切时间窗：问「今天」却命中上周，算失败。允许域名单用于企业「只信文档站」，不是安全的全部。

常见误区是：把内置搜索说成预训练见过实时 X；自定义函数和搜索失败用同一套文案；并行两次搜索没有去重，引用打架。

## 评测

拆：是否该搜、查询是否对、结果是否被引用、空结果拒答率、注入后是否仍执行写操作、实际耗时。只报「答案像真的」会把编造新闻算进正例。Arena 偏好更不适合时效题，见 `xai-lmarena`。

循环预算：最大搜索次数、每次超时、总 token 预算。搜索 agent 比普通聊天更容易空转。观测要把截断后的 snippet 记下来，否则你调试的是模型没看见的世界，见 `xai-agent-loop`。

宿主记录每次查询、返回 URL 和是否空集，才能核对回答引用的确来自本次搜索。

在 2026 年的产品材料中，Grok 4.7 仍把 `web_search` 和 `x_search` 作为内置服务端工具。Grok Build 的 `/deep-research` 工作流会分派调查任务，并用来源核验结论。面试回答“为什么加入 xAI”时，可以从这里展开：信息时效、引用是否有来源，以及结果是否完整；要求完整集合的任务中，只有部分正确仍算失败。不能用 Arena Elo 判断模型是否知道“今天 X 上发生了什么”。公司信息见 `xai-spacexai-now`。

## 追问

**网页和 X 能不能一起开？**
文档允许组合。混用时分清来源：新闻站点 vs 帖子。引用格式不要合成一条「网上说」。

**为什么还要自定义检索？**
内部语料、付费库、权限文档不是公网。搜索工具补的是开放网，不替代你的 ACL 检索。

**搜到冲突怎么办？**
把冲突摆出来并引用两侧，或问用户信哪类来源。不要私下选听起来更顺的。

**图片搜索？**
`enable_image_search` 会把图嵌进回复；和「理解网页里的图」不是同一开关。以文档为准。

本卡依据公开材料整理，标记为 `realInterview: false`。

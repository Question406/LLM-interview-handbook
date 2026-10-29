---
id: xai-spacexai-now
section: xai
order: 0
level: S
title: 'xAI / SpaceXAI: what they are shipping now (Grok, Cursor, Colossus)'
quick: >-
  准备「为什么 xAI」时，我会从 Grok tools、Grok Build、Grok Bot 或 Cursor
  中选一个方向，讲清一个具体失败模式和自己能做的工作。材料称 xAI 已成为 SpaceX 子公司、公开品牌使用
  SpaceXAI；公司背景一句话交代，重点留给搜索、验证、缓存或共享 VM 等团队问题。
tags:
  - xAI
  - SpaceXAI
  - Grok
  - Cursor
  - Grok Build
  - Post-training
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-29T00:00:00.000Z
sources:
  - title: xAI joins SpaceX
    url: 'https://x.ai/news/xai-joins-spacex'
    type: primary
  - title: SpaceX acquires xAI (Reuters)
    url: >-
      https://www.reuters.com/business/musks-spacex-merge-with-xai-combined-valuation-125-trillion-bloomberg-news-2026-02-02/
    type: secondary
  - title: Introducing Grok Build
    url: 'https://x.ai/news/grok-build-cli'
    type: primary
  - title: Workflows in Grok Build
    url: 'https://x.ai/news/workflows'
    type: primary
  - title: Designing Grok Bot for a world of persistent agents
    url: 'https://x.ai/news/designing-grok-bot'
    type: primary
  - title: Grok Bot overview
    url: 'https://docs.x.ai/grok-bot/overview'
    type: primary
  - title: Grok 4.7
    url: 'https://docs.x.ai/developers/grok-4-6'
    type: primary
  - title: Context compaction
    url: 'https://docs.x.ai/developers/advanced-api-usage/context-compaction'
    type: primary
  - title: Prompt caching
    url: 'https://docs.x.ai/developers/advanced-api-usage/prompt-caching'
    type: primary
  - title: Grok 4.20 Multi-Agent
    url: 'https://docs.x.ai/developers/models/grok-4.20-multi-agent-0309'
    type: primary
  - title: Cursor is now a part of SpaceX
    url: 'https://cursor.com/blog/joining-spacex'
    type: primary
  - title: xAI tools overview
    url: 'https://docs.x.ai/docs/agents/tools'
    type: primary
---

这张卡用来准备「为什么 xAI」：先选一个公开产品方向，再说明你想解决的具体失败模式，例如错调工具、搜索集合不完整、verifier 执行不了，或 compaction 丢掉后续需要的观察。公司背景一句话交代即可。下面只整理公开材料，不推测内部集群拓扑、职级或未发布训练配方；15 分钟 screen 的日历仍可能写 xAI，产品文档则使用 SpaceXAI。

## 公司背景与产品地图

SpaceX 于 2026 年 2 月 2 日收购 xAI，保留其子公司身份，见 [x.ai/news/xai-joins-spacex](https://x.ai/news/xai-joins-spacex)。Reuters 报道这笔全股票交易中，xAI 估值约 2500 亿美元，SpaceX 约 1 万亿美元。之后公开写作采用 SpaceXAI 名称。Cursor 自己的文章称，Anysphere 收购于 2026 年 8 月 14 日完成，团队将参与 Grok Build、Grok Bot、Grok API 和 Cursor。

如果面试官问「你指 SpaceX 还是 xAI」，用一句话说明这层关系，再回到团队问题；招聘日历上仍可能沿用 xAI。

| 公开产品 | 它做什么 | 可以展开的研究问题 | 手册 |
| --- | --- | --- | --- |
| Grok tools / DeepSearch | 服务端 `web_search`、`x_search`、code execution | 时效、引用、空搜索诚实性、工具等待占用的 wall-clock | `xai-search-agent`、`xai-tool-use` |
| Grok 4.7（API 文档） | 面向 coding 和 agentic work 的前沿模型；500k 上下文；`prompt_cache_key` / `x-grok-conv-id`；长循环中的 compaction | 复用前缀 KV，与丢弃冗长工具轨迹分别解决什么问题 | `xai-prompt-cache` |
| Context compaction | `POST /v1/responses/compact` 把历史轮次变成不透明条目；无法补救已经超窗的请求 | 长 agent 中保留和删除哪些信息；研究 online KV 时还要考虑 proxy/delay | compaction docs |
| Grok Build | 终端 coding agent；plan/diff；subagents；AGENTS.md / skills / MCP | Coding-agent 后训练、可执行 verifier、reward hacking | `xai-agent-loop` |
| Grok Build workflows | 宿主把任务分给多个 child agents，独立检查后汇成一个报告；公开文章称 budget 128、最多 1,024 | 多 agent 的 credit assignment、验证、每个 child 的上下文隔离 | workflows post |
| Grok 4.20 multi-agent | 文档列出的模型 id，1M 上下文，用于并行研究 | 和 workflows 同类的协作问题，但 serving 约定不同 | model card |
| Grok Bot | 在用户级云 VM 上运行的命名持久 agent；Bots 共享文件和登录，界面不构成 security constraints | 进程隔离、共享可变状态、computer-use 确认 | Bot docs |
| Cursor / Composer | IDE 与 agentic coding models；Cursor 称 SpaceXAI 算力合作用于扩展 RL / continued pretrain | 对 diff 的奖励、评测、feedback-data incorporation | Cursor post |
| Colossus | 公开的超级计算基础设施方向 | 故障域和一致 checkpoint；不把集群 GPU 数当成个人经历 | `xai-colossus` |

Serving 中要分开解释缓存和压缩。Prompt cache 复用相同 token 前缀的已算 KV；模板漂移、工具 schema 重排或遗漏 `prompt_cache_key` 都会破坏命中。Compaction 则把冗长历史删减成一个 blob，让下一次调用变短；如果压缩率上升、任务表现下降，就可能删掉了后续工具仍要用的观察。

speculative decoding 隐藏的是 token decode 时间，工具调用推测隐藏的是 tool I/O 等待。两者处理的时间段不同，回答时分别核算。

## 选一个团队方向展开

下面这些方向来自公开岗位和产品页面。选与自己的经历和 JD 对得上的一个，再讲问题和方法：

- Coding agents / Grok Build / Cursor：可以讲 reasoning RL、数据集生成、evals 和「AI-native software engineering stack」。公开流程在 phone screen 后常有 coding assessment、两轮 post-training problem sessions 和一次 work presentation。
- Reasoning / post-training：在预训练基座上做 fine-tune 和 RL，重点是如何定义数据、奖励问题，不能只复述 Colossus 新闻。
- Search / DeepSearch / Grok tools：把实时网页和 X 当成一等工具，展开时效、来源和结果完整性。
- Inference / long agent loops：可以讲 cache、compaction、500k–1M 窗口和 multi-agent fan-out。
- Grok Bot / computer use：可以讲持久 VM、共享账号状态和 approvals。
- Training infra / Colossus：JD 是这个方向再选；没有亲自负责过 10k-GPU run 的 LLM PhD，不应把它说成自己的主场。
- Video gen / Imagine：公开存在的产品线，岗位没有指向这里时可以跳过。

只说「我喜欢 Grok」或「最大的集群」，很难让面试官判断你想做什么。更具体的说法是点名上面一行，再解释一个失败模式：wrong tool call、incomplete search set、verifier that cannot execute，或者 compaction drops a future observation。

已知与未知也要说清：内部 router、未公开 MoE recipe、Cursor 内部 reward weights 没有依据就不讲。JD 不属于火箭部门时，不把 SpaceX 火箭当成研究动机；Tesla occupancy / hydra nets 在这一章只作对照，不能当成 Grok 工作。交易金额、公司人数或「我们下个月上 Colossus 训练」也不能说成个人事实。

## 追问

**什么时候 cache，什么时候 compact？**
前缀稳定、后续仍需要每个 token 时用 cache；工具轨迹很大、下一步只要关键状态时用 compact。Compaction 不能修复 `context_length_exceeded`。

**workflows 为什么提 independent skeptics？**
它安排第二轮独立检查，把结论对回来源。一个 agent 发现问题又自己判分虽然便宜，但缺少这道独立验证；公开文章宣传的检查方式，和可执行 verifier 对比模型自己猜 expected output 的区别相似。

**Grok Bot 的电脑是怎么共享的？**
隔离按账号划分，多个 Bot 共享同一用户的 VM。回答进程与线程时可以用它作产品例子：文件系统和 cookies 都是共享状态，出错会影响同一账号里的其他 Bot。

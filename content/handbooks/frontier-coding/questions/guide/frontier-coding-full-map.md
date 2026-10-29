---
id: frontier-coding-full-map
section: guide
order: 0
level: S
title: 五家公司 Coding 总览：全部 117 道练习与本轮新增 20 题
quick: >-
  本轮新增 20 道：Meta 8、OpenAI 6、xAI 6。独立题本汇总 117 张可运行 Coding Cards，
  包含原先的公司章节与 16 张 shared ML coding；Humans& 与 Thinking Machines 按已有公开证据收录。
companies:
  - meta
  - openai
  - xai
  - humansand
  - thinking-machines
tags:
  - 练习导航
  - Frontier Coding 扩展 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Meta maze solver 公开题型
    url: https://www.1point3acres.com/interview/problems/company/meta/ai-coding-maze-solver
    type: secondary
  - title: Meta 公开目录
    url: https://landthelab.com/companies/meta
    type: secondary
  - title: AI-enabled coding 题型综述
    url: https://aceoffer.app/interviews/ai-coding
    type: secondary
  - title: OpenAI coding 公开目录
    url: https://aceoffer.app/interviews/openai/coding-questions
    type: secondary
  - title: xAI coding 公开目录
    url: https://aceoffer.app/interviews/xai/coding-questions
    type: secondary
  - title: xAI 公开目录
    url: https://landthelab.com/companies/xai
    type: secondary
  - title: Humans& 候选人自述
    url: https://www.uscardforum.com/t/topic/535363
    type: interview
  - title: Thinking Machines 官方研究文章
    url: https://thinkingmachines.ai/blog/
    type: primary
---

## 回答思路

> **Situation：** 上一批只展示新增九题，已有 coding 分散在不同题本，容易漏看。  
> **Task：** 将五家公司相关的完整练习集中浏览，并增加不同类型的新题。  
> **Approach：** 使用 canonical question references 汇总来源题本，本轮另加 20 张独立题面与可运行代码。  
> **Result：** 当前有 117 张 Coding Cards；每张保留原始来源链接，新增练习均可运行题内 assertions。

## 题本里有什么

这里的数量是 **question cards 数**，同一算法在不同场景的变体会分别保留。它用于安排练习量；面经来源的数量、公司出题频率和算法类别数需要分别看。

| 章节 | 可运行 Coding Cards | 本轮新增 |
| --- | ---: | ---: |
| Meta | 13 | 8 |
| OpenAI | 48 | 6 |
| xAI | 37 | 6 |
| Humans& | 1 | 0 |
| Thinking Machines Lab | 2 | 0 |
| Shared ML Coding | 16 | 0 |
| **合计** | **117** | **20** |

Shared 章节来自原题本带这些公司标签的 ML exercises；公司专属章节与 shared 的归属由原 canonical section 决定。每张 card 在本题本只收录一次。左侧选公司可以看该章节全部题；使用 **Frontier Coding 扩展 2026-10-28** 标签筛出这一轮新增。总览本身是一张导航卡，不计入上述 coding 数。

## 本轮新增 20 张 cards

所有新题都写出输入、输出、异常处理、具体示例、回答思路、完整 Python 实现和 tests。公开目录只给题名或短摘要时，card 开头会说明手册补充的接口与规则。

| 公司 | 练习 | 重点 |
| --- | --- | --- |
| meta | [[meta-maze-keys-direction-state]] | BFS state、key mask、outgoing direction |
| meta | [[meta-word-selection-letter-coverage]] | Bitmask DP、letter coverage、tie-breaking |
| meta | [[meta-card-triples-exact-selection]] | Exact search、disjoint triples、memoization |
| meta | [[meta-mutual-friends-topk]] | Two-hop graph、top-K、ranking validity |
| meta | [[meta-streaming-kmp-search]] | KMP、跨 chunk state、overlapping matches |
| meta | [[meta-shortest-unique-prefix-trie]] | Trie counts、word-prefix ambiguity |
| meta | [[meta-expand-signed-expression]] | Parser signs、nested parentheses、coefficients |
| meta | [[meta-parallel-build-bottlenecks]] | Topological batches、cycle detection |
| openai | [[openai-tree-route-required-tasks]] | Tree pruning、required subtree、route weight |
| openai | [[openai-grid-visit-targets-mask]] | Grid BFS、visited-target mask |
| openai | [[openai-modular-addition-bfs]] | Residue graph、negative steps、shortest path |
| openai | [[openai-file-content-dedup-collisions]] | Content hashing、exact equality、collision test |
| openai | [[openai-largest-subgrid-histogram-extension]] | Matrix histogram、monotonic stack |
| openai | [[openai-beat-notation-parser-extension]] | Grammar、Fraction、bar validation |
| xai | [[xai-atomic-hierarchical-sliding-limiter]] | Atomic commit、sliding window、threads |
| xai | [[xai-single-pass-document-cleaning]] | Normalization、exact deduplication、audit counters |
| xai | [[xai-courier-pay-event-sweep]] | Event sweep、integer cents、validation |
| xai | [[xai-nested-json-safe-viewer-core]] | HTML escaping、typed paths、collapsed containers |
| xai | [[xai-double-base-palindrome-enumeration]] | Palindrome generation、numeric order |
| xai | [[xai-async-dag-task-scheduler]] | Async concurrency、failure propagation、cleanup |

## 如何安排练习

先练能直接迁移到 AFM screen 的题：[[meta-maze-keys-direction-state]]、[[openai-grid-visit-targets-mask]]、[[xai-single-pass-document-cleaning]]、[[xai-async-dag-task-scheduler]]。它们分别要求把 state 写完整、构造 mask、说清 data quality policy 和处理 async failures。

然后各抽一题练 45 分钟：5 分钟读清 contract，25 分钟写代码，10 分钟测试，5 分钟解释 scale 与改进。AI-enabled 项目题也要先给一个可运行 reference，再加功能；如果引入 AI 生成代码，仍需能解释每个 state 和测试为什么必要。

每道题顶部的 callout 用于开场解释；完整答案用于核对 reasoning。代码后的 assertions 先覆盖手算示例，再覆盖失败情形。部分题额外用 brute-force oracle 核对小输入，例如 word selection、card triples、tree route、matrix rectangle。

## 来源怎么读

**候选人自述**保留当事人的公开链接；**平台题型改编**保留平台页面与能核对的题型；**题型扩展**由手册明确新增 constraints 与接口。这里的 Meta / OpenAI / xAI 新题以公开题型和自写实现为主。

Humans& 仍保留 [[humansand-top-p-live-debug]]：本轮检索未找到足够具体、能与已有 top-p 题区分的新 coding 题面。

Thinking Machines Lab 仍保留 [[tml-batch-invariant-rmsnorm-reference]] 与 [[tml-lora-linear-forward-gradients]]：这两张来自官方技术文章的机制练习。公开的 coding-round 讨论未提供足够题面，暂时按这些已有证据收录。

OpenAI 的 rectangle 与 beat parser cards 明确使用手册自定条件或 notation；xAI JSON card 将 UI 题拆为 Python renderer 模块。选择这些 cards 是为了练可验证的实现，各卡来源说明列出实际能核对的内容。

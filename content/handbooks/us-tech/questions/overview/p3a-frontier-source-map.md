---
id: p3a-frontier-source-map
section: overview
order: 20
level: S
title: Frontier Lab：118 道完整编程练习与 49 道设计 / 答辩题
quick: "这张导航汇总已复查的 167 张题卡：118 张有可执行题面、示例、参考实现和测试，49 张有场景参考回答，另存 385 条来源。按公司或能力路径进入，先分清原始线索和手册补的练习约定；缺失条件没有当作原题事实。"
companies:
  - openai
  - anthropic
  - xai
  - google
  - meta
  - microsoft
  - mistral
  - cohere
  - ai-labs
tags:
  - 1Point3Acres
  - Frontier-2026-10
  - 题型导航
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: OpenAI company bank
    url: https://www.1point3acres.com/interview/problems/company/openai
    type: secondary
  - title: Anthropic company bank
    url: https://www.1point3acres.com/interview/problems/company/anthropic
    type: secondary
  - title: xAI company bank
    url: https://www.1point3acres.com/interview/problems/company/xai
    type: secondary
---

## 这批材料如何使用

先按公司找到题卡，再按能力路径补相邻题；练习前看清证据范围和手册约定，避免把变体规则混用。材料于 2026-10-18 通过 Chrome 正常读取，多数依据公司题卡摘要，部分读到详情，没有逐一核对候选人原帖，也不保证穷尽全站。题卡分别说明题意、证据范围和手册参考解法，所有新条目都可用标签 `Frontier-2026-10` 或搜索 `1Point3Acres` 找到。

## 按公司进入

| 公司/范围 | 新增题卡 | 入口 |
| --- | ---: | --- |
| openai | 53 | [[p3a-openai-source-index]] |
| anthropic | 35 | [[p3a-anthropic-source-index]] |
| xai | 30 | [[p3a-xai-source-index]] |
| microsoft | 16 | [[p3a-microsoft-beam-search-decoder]] |
| perplexity | 16 | [[p3a-perplexity-source-index]] |
| mistral | 3 | [[p3a-mistral-source-index]] |
| cohere | 3 | [[p3a-cohere-source-index]] |
| google-deepmind | 2 | [[p3a-google-deepmind-source-index]] |
| cursor | 2 | [[p3a-cursor-source-index]] |
| google | 3 | [[p3a-google-source-index]] |
| meta | 4 | [[p3a-meta-source-index]] |

Cohere 删除数字5、xAI N-gram与输入框三条仅按标题重构练习，未标已核实真题。DeepMind 独立目录 2 条来自 Android 岗；研究岗优先看 [[p3a-google-deepmind-rs-paper-presentation-defense]]。Perplexity 与 Cursor 是补充 AI 公司范围。

## Microsoft AI / Copilot 题卡入口

- [[p3a-microsoft-dna-shotgun-sequencing]]
- [[p3a-microsoft-in-memory-sql-engine]]
- [[p3a-microsoft-employee-attrition-prediction]]
- [[p3a-microsoft-memory-allocator]]
- [[p3a-microsoft-kv-store-with-snapshot]]
- [[p3a-microsoft-parse-emails-state-machine]]
- [[p3a-microsoft-beam-search-decoder]]
- [[p3a-microsoft-max-number-occurrences-in-suffix]]
- [[p3a-microsoft-top-k-largest-retain]]
- [[p3a-microsoft-streaming-stop-token-detection]]
- [[p3a-microsoft-embedding-lm-head-distributed-sharding]]
- [[p3a-microsoft-chatbot-personalization-memory-design]]
- [[p3a-microsoft-web-crawler-system-design]]
- [[p3a-microsoft-search-autocomplete-typeahead]]
- [[p3a-microsoft-project-deep-dive]]
- [[p3a-microsoft-transformer-roofline-fp-precision]]

## 按能力串联

1. **ML 编程与调试**：[[p3a-openai-transformer-bug-hunt]] → [[p3a-openai-numpy-1nn-wx-b]] → [[p3a-openai-masked-cross-entropy-loss]] → [[p3a-openai-streaming-entropy]] → [[p3a-anthropic-rl-fundamentals-grpo-debug]]。重点是张量形状、数值稳定、损失与梯度能否用小例子解释。
2. **状态机与真实工程编码**：[[p3a-openai-gpu-credits]] → [[p3a-openai-fault-tolerant-work-queue]] → [[p3a-anthropic-coding-q3-stack-trace]] → [[p3a-anthropic-coding-q1-web-crawler]] → [[p3a-xai-transactional-key-value-store]]。重点是历史、乱序、重复执行与崩溃恢复，而不只是套数据结构。
3. **推理与分布式系统**：[[p3a-anthropic-sd-q1-inference-api]] → [[p3a-anthropic-sd-q3-model-distribution]] → [[p3a-xai-distributed-matmul-dp-fsdp]] → [[p3a-microsoft-embedding-lm-head-distributed-sharding]] → [[p3a-perplexity-map-reduce-and-blockwise-attention]]。每个方案都写出资源约束、通信量和失败路径。
4. **LLM 产品和 Agent**：[[p3a-anthropic-agents-coding-llm-tool-use]] → [[p3a-perplexity-durable-long-running-agentic-query-execution]] → [[p3a-meta-system-design-ai-enabled-agent-system]] → [[p3a-microsoft-chatbot-personalization-memory-design]]。先做可测的最小闭环，再谈多 agent 或复杂记忆。
5. **研究与项目答辩**：[[p3a-google-deepmind-rs-paper-presentation-defense]]、[[p3a-anthropic-mech-interp-take-home]]、[[p3a-openai-technical-deep-dive]]。准备假设、消融、局限与个人贡献，不把实验结果只讲成业务故事。

## 变体不能混合

- GPU Credit 有闭区间到期、半开区间、允许暂时透支与永久失败等不同契约。先按本次题面选择，不能从其他面经搬一个返回值规则过来。
- Anthropic 最长匹配 tokenizer 与 BPE 不是同一个算法；文件去重题也不等于只背 SHA-256。
- Task/DB OA 的第四级可能是 restore 或历史查询，两者存储设计不同。
- 至少一次 worker 投递不自动保证外部副作用恰好一次；源页面措辞强于可实现保证时，参考思路明确讨论实现边界。

## 来源等级与数量

`detail-read`：已读题目详情。`company-card-summary`：已读公司题卡摘要。`title-only`：仅目录标题，未确认题干。网站本身通常是面经二次整理，不能当公司官方确认。385 个来源条目包含重复与变体，并与167张题卡重叠。

本次保留现有题卡，以新增卡和交叉链接补充。完整机器可读档案在仓库 `content/sources/1point3acres-frontier-2026-10-18/`，含 JSON、CSV、统计和采集边界。源页面的显示总数在不同入口存在差异，这里按实际记录计数。

## 完整练习如何使用

题卡的「完整编程练习（手册重构版）」包含接口、约束、输入输出示例、正确性、完整实现、测试和复杂度；49道非编程题有独立场景与参考回答。代码另存来源档案的practice/solutions/，118张卡共用85份已测实现。

在仓库执行 `python3 scripts/check-frontier-practice.py` 可检查全部167张覆盖，并运行83份Python与2份JavaScript/React参考实现。Python依赖NumPy/Pillow，JS使用本仓库React。行为题演示是明确的假想案例，不是候选人真实经历。

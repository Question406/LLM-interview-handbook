---
id: dt-frontier-who-reports
section: frontier-release
order: 6
level: S
title: 哪家 lab、哪个模型、在哪次发布里报了哪项 benchmark？
quick: >-
  按每份官方发布材料分开记分数，写明日期和思考档。比如 Gemini 3.1 Pro 模型卡里的 Opus 分数是 Google 跑的对照，不能算作
  Anthropic 自报。
companies:
  - openai
  - anthropic
  - google
  - meta
  - deepseek
  - alibaba
tags:
  - Evaluation
  - OpenAI
  - Anthropic
  - Google
  - Meta
  - DeepSeek
  - Qwen
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Gemini 3.1 Pro Model Card
    url: 'https://deepmind.google/models/model-cards/gemini-3-1-pro/'
    type: primary
  - title: Claude Opus 4.5 System Card
    url: 'https://www.anthropic.com/claude-opus-4-5-system-card'
    type: primary
  - title: Introducing GPT-5
    url: 'https://openai.com/index/introducing-gpt-5/'
    type: primary
  - title: GPT-5.6
    url: 'https://openai.com/index/gpt-5-6/'
    type: primary
  - title: Llama 4 model card
    url: >-
      https://github.com/meta-llama/llama-models/blob/main/models/llama4/MODEL_CARD.md
    type: primary
  - title: The Llama 4 herd
    url: 'https://ai.meta.com/blog/llama-4-multimodal-intelligence/'
    type: primary
  - title: DeepSeek-V3
    url: 'https://arxiv.org/abs/2412.19437'
    type: primary
  - title: Qwen3 Technical Report
    url: 'https://arxiv.org/abs/2505.09388'
    type: primary
  - title: Why we no longer evaluate SWE-bench Verified
    url: 'https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/'
    type: primary
---

## 可以这样回答

比如 Google 卡里的 Sonnet、Opus、GPT 列，是 Google 写进对照表的，思考档写在列名里，不能说成 Anthropic 或 OpenAI 自己报的结果；Anthropic 和 OpenAI 自家博文里的数另列一表。Llama 4 的材料报的是 base model 和指令模型的学术评测，和 2026 年 agent 产品的发布定义不同。各项评测怎么造、测什么能力，见 `dt-frontier-science`、`dt-frontier-code-sets`、`dt-frontier-agent-sets`、`dt-frontier-ctx-mm`。

各列都是 Thinking 档：Gemini 为 High，Claude 为 Max，GPT-5.2 为 xhigh。GPT-5.3-Codex 只出现在部分代码行。

## 技术备查

我按发布材料记分数，不按聚合榜记。下面每张表只属于那一份材料，引用里面任何一个结果，都要同时说出材料日期和思考档。

比如 Google 卡里的 Sonnet、Opus、GPT 列，是 Google 写进对照表的，思考档写在列名里，不能说成 Anthropic 或 OpenAI 自己报的结果；Anthropic 和 OpenAI 自家博文里的数另列一表。Llama 4 的材料报的是 base model 和指令模型的学术评测，和 2026 年 agent 产品的发布定义不同。各项评测怎么造、测什么能力，见 `dt-frontier-science`、`dt-frontier-code-sets`、`dt-frontier-agent-sets`、`dt-frontier-ctx-mm`。

## Google · Gemini 3.1 Pro 模型卡，2026-02-19

各列都是 Thinking 档：Gemini 为 High，Claude 为 Max，GPT-5.2 为 xhigh。GPT-5.3-Codex 只出现在部分代码行。

| Benchmark | 卡上写的能力 | 3.1 Pro | 3 Pro | Sonnet 4.6 | Opus 4.6 | GPT-5.2 |
| --- | --- | --- | --- | --- | --- | --- |
| HLE，无工具 | 学术推理，全文，文本+multimodal | 44.4% | 37.5% | 33.2% | 40.0% | 34.5% |
| HLE，搜索（屏蔽名单）+ 代码 | 同上，允许检索和代码 | 51.4% | 45.8% | 49.0% | 53.1% | 45.5% |
| ARC-AGI-2 | 抽象谜题，ARC Prize Verified | 77.1% | 31.1% | 58.3% | 68.8% | 52.9% |
| GPQA Diamond | 科学知识，无工具 | 94.3% | 91.9% | 89.9% | 91.3% | 92.4% |
| Terminal-Bench 2.0 | 终端，Terminus-2 | 68.5% | 56.9% | 59.1% | 65.4% | 54.0% |
| SWE-bench Verified | 仓库 issue，single attempt | 80.6% | 76.2% | 79.6% | 80.8% | 80.0% |
| SWE-bench Pro Public | 另一套仓库任务，single attempt | 54.2% | 43.3% | - | - | 55.6% |
| LiveCodeBench Pro | 竞赛编程，Elo | 2887 | 2439 | - | - | 2393 |
| SciCode | 科研代码 | 59% | 56% | 47% | 52% | 52% |
| APEX-Agents | 长程职业任务 | 33.5% | 18.4% | - | 29.8% | 23.0% |
| GDPval-AA | 专家任务，Elo | 1317 | 1195 | 1633 | 1606 | 1462 |
| τ² Retail / Telecom | 业务工具，分域 | 90.8 / 99.3 | 85.3 / 98.0 | 91.7 / 97.9 | 91.9 / 99.3 | 82.0 / 98.7 |
| MCP Atlas | 多步 MCP | 69.2% | 54.1% | 61.3% | 59.5% | 60.6% |
| BrowseComp | 搜索+Python+浏览 | 85.9% | 59.2% | 74.7% | 84.0% | 65.8% |
| MMMU-Pro | multimodal 学科，无工具 | 80.5% | 81.0% | 74.5% | 73.9% | 79.5% |
| MMMLU | multilingual 问答 | 92.6% | 91.8% | 89.3% | 91.1% | 89.6% |
| MRCR v2，8-needle，128k | long context 检索 | 84.9% | 77.0% | 84.9% | 84.0% | 83.8% |
| MRCR v2，1M | 同上，point estimate | 26.3% | 26.3% | 不支持 | 不支持 | 不支持 |

同一张卡还写了 GPT-5.3-Codex：Terminal-Bench 2.0 在 Terminus-2 上 64.7%、在 Codex harness 上 77.3%；SWE-bench Pro Public 56.8%。GPT-5.2 在 Codex harness 上是 62.2%。模型卡正文说 3.1 Pro 基于 Gemini 3 Pro，训练数据部分指向 3 Pro 的卡，这一页没有展开新的 data mix。

## Anthropic · Claude Opus 4.5 system card

这是 4.5 自己报的数，和上表里的 4.6 是两代。

| Benchmark | 设定 | 数 |
| --- | --- | --- |
| SWE-bench Verified / Pro / Multilingual | 无 thinking | 80.9% / 52.0% / 76.2% |
| 同上 | 64k thinking | 80.6% / 51.6% / 76.2% |
| Terminal-bench 2.0 | system card 表 | 59.3% |
| τ² Retail / Telecom | system card 表 | 88.9% / 98.2% |
| MCP Atlas | system card 表 | 62.3% |
| OSWorld | system card 表 | 66.3% |
| GPQA Diamond | 64k thinking，200k 上下文，high，5 次平均 | 86.95% |

## OpenAI · GPT-5 发布博文

| Benchmark | 设定 | 数 |
| --- | --- | --- |
| AIME 2025 | 无工具 | 94.6% |
| SWE-bench Verified | 他们基础设施上的 n=477 | 74.9% |
| Aider Polyglot | 博文所写 | 88% |
| MMMU | 博文所写 | 84.2% |
| HealthBench Hard | 健康难子集 | 46.2% |
| GPQA | GPT-5 pro，无工具 | 88.4% |

博文写明，带工具的 AIME 不能和无工具直接比。

## OpenAI · GPT-5.6 博文，2026-07-09

这一代的家族是 Sol、Terra、Luna。下面是博文里 Sol 的绝对分，对照的上一代是他们自己的 GPT-5.5。博文把 Claude Fable 5 当作对手提到分差，但 Fable 的官方评测表我没有逐项读到，这里不转抄对手的隐含分数。

| Benchmark | 博文里的能力定义 | Sol |
| --- | --- | --- |
| Agents' Last Exam | 55 个领域的长程职业流程 | 53.6 |
| BrowseComp | 浏览找事实 | 92.2% |
| OSWorld 2.0 | 电脑操作 | 62.6% |
| Terminal-Bench 2.1 | 复杂命令行 | 博文写达到当时前沿，无绝对分 |
| ExploitBench 2 | 从触及有漏洞的代码到代码执行的进展 | 73.5%（GPT-5.5 为 47.9%，相近输出 token 预算） |
| ExploitGym 3 | 把真实漏洞做成可运行的利用 | 两小时上限 24.9%（5.5 为 15.1%）；六小时 33.7% |
| SEC-Bench Pro | 复杂软件上的概念验证生成 | 71.2%（5.5 为 45.8%） |

生命科学一段只写了相对 5.5 有提升，没有公开数据集名字和分数。

ExploitBench、ExploitGym、SEC-Bench 卡的是网络安全能力。数据组要知道发版在报它们，判分看的是任务完成度，面试里不要展开利用步骤。

## Meta · Llama 4，模型卡 2025-04-05

Scout 每次计算激活 17B 参数，总参数 109B，16 个专家，上下文长度 10M，pre-training 约 40T token。Maverick 激活 17B 参数，总参数 400B，128 个专家，上下文长度 1M，pre-training 约 22T token。两者的训练数据都截止到 2024-08。模型卡写数据来自公开、许可的内容，加上 Meta 产品信息，包括 Instagram 和 Facebook 上公开分享的帖子，以及用户和 Meta AI 的交互。博客另写 Behemoth（288B 激活、16 专家、总参近 2T）还在训练，总 mix 超过 30T，并用它给 Maverick 做 codistill。

指令模型、0-shot，Maverick：MMLU Pro 80.5，GPQA Diamond 69.8，LiveCodeBench（2024-10-01 至 2025-02-01）pass@1 43.4，MMMU 73.4，MMMU Pro 59.6，MathVista 73.7，ChartQA 90.0，DocVQA 94.4，MGSM 92.3。base model 表用的是 MMLU 5-shot、MATH maj@1、MBPP 3-shot，和指令表不是同一套指标。这次发布没有 SWE-bench Pro、BrowseComp、Terminal-Bench，那是 2025 年 4 月开源发布的定义。

## DeepSeek、Qwen，以及这章故意不写的

DeepSeek-V3 技术报告和 Qwen3 技术报告的评测节仍覆盖知识、数学、代码和工具，用来和上一代开源 base model 比，分数以论文表格为准。我这次没有逐格核对到 2026 年秋季的新模型，所以不在这里转抄可能已经过期的排行。

xAI 的发版常同时报竞技场 Elo 和 STEM 榜。2026 年 Grok 的官方逐项表我没有核对进这张卡，所以不写数。

## 追问

**面试里怎么用几句话总结？**
可以这么说：「Gemini 3.1 模型卡分别报告科学推理、仓库任务、终端、浏览和 long context 表现。Verified 已经接近 80%，Pro 仍在 50% 多，MRCR 在 1M 长度下只有约 26%。GPT-5.6 的主要发布指标改为浏览、电脑操作和长程职业任务，OpenAI 也已停止用 Verified 报前沿成绩。Llama 4 仍报 MMLU 和图表题，因为它那次发布的是开源 base model 和指令模型。引用分数时，我会同时说明材料日期和思考档。」

**Opus 4.5 加了 64k thinking，SWE-bench 怎么没涨？**
无 thinking 的 Verified 是 80.9%，64k thinking 是 80.6%，后者并不更高。加思考预算不会在每张榜上都涨，所以报分时要把预算写上。

**GPT-5 的 Verified 74.9% 还能当主指标比吗？**
只能当历史发布记录。2026-02 OpenAI 另发文章说明不再用 SWE-bench Verified 报前沿成绩，见 `dt-agent-verified-stale`，他们后来的主指标已经换了。

**GPT-5.6 博文里研究员每天的 token 用量，能当能力证据吗？**
不能。内部研究加速一节写的是研究员每天的输出 token 数、内部推理算力占比等用量数据，这些说明产品被用得多，不是能力评测结果。

**Llama 4 的 40T、22T 和「超过 30T」能加起来吗？**
不能。它们分别属于 Scout、Maverick 和 Behemoth，加成一个数就错了。

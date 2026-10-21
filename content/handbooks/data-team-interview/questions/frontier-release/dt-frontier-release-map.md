---
id: dt-frontier-release-map
section: frontier-release
order: 1
level: S
title: Frontier 发模型时，主表还在报哪些数据集？
quick: "2026 年闭源模型的发布主表主要报告科学推理、仓库修复、终端操作、浏览、桌面操作、长上下文和多模态，已较少以 MMLU、HumanEval 为重点。比较分数前，要核对思考预算、工具、尝试次数、运行框架、子集和报分方。评测集名称也不能当成训练集名称。"
companies:
  - apple
  - openai
  - anthropic
  - google
  - meta
tags:
  - Evaluation
  - Benchmark
  - OpenAI
  - Anthropic
  - Google
  - Meta
  - 备考地图
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Gemini 3.1 Pro Model Card
    url: https://deepmind.google/models/model-cards/gemini-3-1-pro/
    type: primary
  - title: Introducing GPT-5
    url: https://openai.com/index/introducing-gpt-5/
    type: primary
  - title: GPT-5.6
    url: https://openai.com/index/gpt-5-6/
    type: primary
  - title: Claude Opus 4.5 System Card
    url: https://www.anthropic.com/claude-opus-4-5-system-card
    type: primary
  - title: Llama 4 model card
    url: https://github.com/meta-llama/llama-models/blob/main/models/llama4/MODEL_CARD.md
    type: primary
  - title: Humanity's Last Exam
    url: https://arxiv.org/abs/2501.14249
    type: primary
---

2026 年春季以后，闭源前沿模型的发布主表主要报这几类能力：闭卷科学推理、仓库里修 issue、终端里完成工程任务、浏览查事实、在真桌面上操作、长上下文检索，以及必须看图的学科题，下面的能力轴表逐项列出。MMLU、HumanEval 这类已经饱和的榜，主要还出现在开源基座的发布里。另外，模型在某个评测集上报分，不代表它用这个数据集训练。

这章讲发布材料中的评测集怎么制作、测什么能力；训练配方见 `dt-posttrain-map`。我核对过的材料范围是：Google 的对照表是 2026-02-19 的 Gemini 3.1 Pro 模型卡；Anthropic 自家的表我读的是 Opus 4.5 system card；OpenAI 最新一份我逐项读过的发版是 2026-07-09 的 GPT-5.6。之后的模型以当时的卡为准。

## 先看设定，再看名字

比较「Opus 比 GPT 高两个点」之前，要确认思考预算、可用工具、尝试次数、运行框架（harness）、评测子集和报分方。设定不同，就不能把分差直接归因于模型。聚合博客可能把不同 harness 下的分数放在同一格里，所以引用时应回到写明设定的官方材料。即使基准名称相同，下面任何一项变了，分数就不是同一个实验：

- 思考预算：`no thinking`、64k thinking、`high` / `xhigh` / `max`
- 工具：无工具、搜索、代码解释器、浏览、电脑操作
- 尝试次数：single attempt、maj@k、pass@k、多次试验平均
- harness：同一题用 Terminus-2 和 Codex 可以差十几个点，见 `dt-frontier-code-sets`
- 子集和版本：SWE-bench Verified 和 Pro，OSWorld 和 OSWorld 2.0，LiveCodeBench 和 LiveCodeBench Pro
- 数字是谁写的：Google 模型卡里的 Opus 列，是 Google 放进对照表的，不是 Anthropic 新闻稿原句

## 能力轴

| 能力 | 现在还在发版主表里的 | 怎么造、谁报了 | 对应的数据与检查题目 |
| --- | --- | --- | --- |
| 闭卷理科，搜网页也帮不上忙 | GPQA Diamond、HLE（无工具）、FrontierMath、AIME | `dt-frontier-science` | `dt-rlvr-data`、`dt-math-passk-band` |
| 新题推理，防背旧竞赛 | ARC-AGI-2、AIME 当年新题、LiveCodeBench 时间窗 | `dt-frontier-science`、`dt-frontier-code-sets` | `dt-code-bench-bleed` |
| 仓库里修 issue | SWE-bench Verified / Pro / Multilingual | `dt-frontier-code-sets` | `dt-agent-verified-stale`、`dt-code-hidden-tests` |
| 终端里做完一件工程 | Terminal-Bench 2.0 / 2.1 | `dt-frontier-code-sets` | `dt-agent-env-is-data` |
| 对着人把库状态改对，而且下次还对 | τ²-bench Retail / Telecom | `dt-frontier-agent-sets` | `dt-tau-passk` |
| 在真桌面点到终态 | OSWorld、OSWorld 2.0 | `dt-frontier-agent-sets` | `dt-gui-traj` |
| 根据多条线索在网上查出事实 | BrowseComp | `dt-frontier-agent-sets` | `dt-when-to-search`、`dt-webgpt-cite` |
| 从长上下文取回指定材料 | MRCR v2（8-needle），128k 和 1M 分开报 | `dt-frontier-ctx-mm` | `dt-longctx-data` |
| 必须看图才能答的学科题 | MMMU、MMMU-Pro | `dt-frontier-ctx-mm` | `dt-synth-tool-mm` |
| 长流程职业任务 | GDPval-AA、APEX-Agents、Agents' Last Exam | `dt-frontier-who-reports` | 公开造法不完整，先讲 grader 是什么 |

## 饱和的榜为什么还出现：为了和基座比

HLE 论文写过：前沿模型在 MMLU 上已超过 90%，这张榜分不开代际了。Llama 4 模型卡（2025-04）仍报 MMLU、MMLU-Pro、MATH、MBPP、ChartQA，因为读者要和 Llama 3.1 比，而且那次发的是基座加指令模型，不是 2026 年的 agent 产品。DeepSeek-V3、Qwen3 的技术报告同样把知识、数学、代码、工具榜写进评测节。闭源模型 2026 年春季以后的模型卡，主表已换成上面表里那一列。

HumanEval、GSM8K、MATH-500 在这些前沿发布材料里通常不再作为主要指标。如果有人拿这些结果声称模型达到前沿水平，应先确认它们是不是只用来检查基座模型的常规能力有没有退步。

## 分数变了先查哪类失败

被问到某个分数的涨跌时，先说它对应哪类失败：GPQA 下降，检查闭卷科学知识与推理；BrowseComp 下降，检查能否持续搜索；SWE-bench 上升，先核对测试和泄漏风险（`dt-benchmark-gap`、`dt-agent-verified-stale`）。

逐家、逐次发布的数字见 `dt-frontier-who-reports`。

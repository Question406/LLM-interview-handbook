---
id: dt-frontier-release-map
section: frontier-release
order: 1
level: S
title: Frontier 发模型时，主表还在报哪些数据集？
quick: >-
  2026 年闭源模型的发布主表主要报科学推理、仓库修复、终端操作、浏览、桌面操作、long context 和
  multimodal，MMLU、HumanEval 已经不是重点。比分数前先核对思考预算、工具、尝试次数、运行框架、子集和报分方。evaluation
  set 的名字也不能当成 training set 的名字。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Gemini 3.1 Pro Model Card
    url: 'https://deepmind.google/models/model-cards/gemini-3-1-pro/'
    type: primary
  - title: Introducing GPT-5
    url: 'https://openai.com/index/introducing-gpt-5/'
    type: primary
  - title: GPT-5.6
    url: 'https://openai.com/index/gpt-5-6/'
    type: primary
  - title: Claude Opus 4.5 System Card
    url: 'https://www.anthropic.com/claude-opus-4-5-system-card'
    type: primary
  - title: Llama 4 model card
    url: >-
      https://github.com/meta-llama/llama-models/blob/main/models/llama4/MODEL_CARD.md
    type: primary
  - title: Humanity's Last Exam
    url: 'https://arxiv.org/abs/2501.14249'
    type: primary
---

这张卡用来对照：在下面的能力轴表里，找到某项 benchmark 测的是哪类能力、造法在哪题、对应哪道数据题。简单说，2026 年春季以后，闭源前沿模型的发布主表主要报这几类：闭卷科学推理、仓库里修 issue、终端里完成工程任务、浏览查事实、在真桌面上操作、long context 检索，以及必须看图的学科题。MMLU、HumanEval 这类已经饱和的榜，主要还出现在开源 base model 的发布里。另外，模型在某个 evaluation set 上报了分，不代表它用这个数据集训练过。

这章讲发布材料里的 evaluation set 怎么造、测什么能力，training recipe 见 `dt-posttrain-map`。我核对过的材料范围是：Google 的对照表用的是 2026-02-19 的 Gemini 3.1 Pro 模型卡；Anthropic 自家的表我读的是 Opus 4.5 system card；OpenAI 最新一份我逐项读过的发版是 2026-07-09 的 GPT-5.6。之后的模型以当时的卡为准。逐家、逐次发布的数字见 `dt-frontier-who-reports`。

## 先看设定，再看名字

比如有人说「Opus 比 GPT 高两个点」，先确认思考预算、可用工具、尝试次数、运行框架（harness）、评测子集和报分方。基准名字一样，下面任何一项变了，分数就不是同一个实验，分差也就不能直接算到模型头上。聚合博客可能把不同 harness 下的分数放进同一格，引用时要回到写明设定的官方材料。

| 设定 | 常见的变化 |
| --- | --- |
| 思考预算 | `no thinking`、64k thinking、`high` / `xhigh` / `max` |
| 工具 | 无工具、搜索、代码解释器、浏览、电脑操作 |
| 尝试次数 | single attempt、maj@k、pass@k、多次试验平均 |
| harness | 同一题用 Terminus-2 和 Codex 可以差十几个点，见 `dt-frontier-code-sets` |
| 子集和版本 | SWE-bench Verified 和 Pro，OSWorld 和 OSWorld 2.0，LiveCodeBench 和 LiveCodeBench Pro |
| 报分方 | Google 模型卡里的 Opus 列是 Google 放进对照表的数，不能当成 Anthropic 新闻稿的原话 |

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
| 从 long context 取 backpointer 定材料 | MRCR v2（8-needle），128k 和 1M 分开报 | `dt-frontier-ctx-mm` | `dt-longctx-data` |
| 必须看图才能答的学科题 | MMMU、MMMU-Pro | `dt-frontier-ctx-mm` | `dt-synth-tool-mm` |
| 长流程职业任务 | GDPval-AA、APEX-Agents、Agents' Last Exam | `dt-frontier-who-reports` | 公开造法不完整，先讲 grader 是什么 |

## 追问

**MMLU 这类饱和的榜，为什么还有人报？**
为了和上一代 base model 比。HLE 论文写过，前沿模型在 MMLU 上已超过 90%，这张榜分不开代际了。DeepSeek-V3、Qwen3 的技术报告仍把知识、数学、代码、工具榜写进评测节，也是为了和开源 base model 比；闭源模型 2026 年春季以后的模型卡，主表已经换成上面能力轴表里那一列。

**Llama 4 为什么还报 MMLU 和 ChartQA？**
因为读者要拿它和 Llama 3.1 比，而且那次发的是 base model 加指令模型，不是 2026 年的 agent 产品。Llama 4 模型卡（2025-04）报的是 MMLU、MMLU-Pro、MATH、MBPP、ChartQA。

**有人拿 HumanEval、GSM8K 的分数说模型到了前沿水平，怎么看？**
先确认这些结果是不是只用来检查 base model 的常规能力有没有退步。HumanEval、GSM8K、MATH-500 在这些前沿发布材料里通常已经不作为主要指标。

**被问到某个分数涨了或跌了，先说什么？**
先说它对应哪类失败。GPQA 下降，检查闭卷科学知识与推理；BrowseComp 下降，检查能不能持续搜索；SWE-bench 上升，先核对测试和 leakage 风险，见 `dt-benchmark-gap`、`dt-agent-verified-stale`。

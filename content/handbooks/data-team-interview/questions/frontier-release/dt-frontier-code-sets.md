---
id: dt-frontier-code-sets
section: frontier-release
order: 3
level: S
title: SWE-bench、Terminal-Bench、LiveCodeBench 怎么造，各卡哪段代码能力？
quick: "这三套测的是不同的代码能力：SWE-bench 修真实 GitHub issue，新测试要从失败变成通过，旧测试还得过；Terminal-Bench 在终端里做完工程任务，运行框架对分数影响很大；LiveCodeBench 按比赛日期切新题，测算法编程、减少背题。三种分数不能合成一个比。"
companies:
  - openai
  - anthropic
  - google
  - meta
tags:
  - Evaluation
  - SWE-bench
  - Code
  - Agent
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: SWE-bench
    url: https://arxiv.org/abs/2310.06770
    type: primary
  - title: Introducing SWE-bench Verified
    url: https://openai.com/index/introducing-swe-bench-verified/
    type: primary
  - title: "SWE-bench Pro: Can AI Agents Solve Long-Horizon Software Engineering Tasks?"
    url: https://arxiv.org/abs/2509.16941
    type: primary
  - title: "LiveCodeBench: Holistic and Contamination Free Evaluation of Large Language Models for Code"
    url: https://arxiv.org/abs/2403.07974
    type: primary
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
---

听到代码评测分数，先确认任务是什么。SWE-bench 是在真实仓库里修 issue，Terminal-Bench 是通过终端完成多步工程任务，LiveCodeBench 是按比赛日期切出来的算法新题。写函数、修仓库、跑终端要的能力不一样，一个 coding 分数概括不了。

举个例子，SWE-bench Verified 在 Google 2026-02 的表里已经接近 80%，Pro 还在 50% 出头。站在数据组的角度，去分析 Pro 和 Terminal-Bench 里仍然失败的任务类型，通常比围绕 Verified 的一个百分点去调数据比例更有信息。比较模型增益时，要把运行框架（harness）、工具、重试次数和步数固定住，不然分数变化可能来自执行环境。

## SWE-bench 家族

SWE-bench 考的是模型能不能读懂 issue、找到要改的位置、修好并且保住原有功能。Jimenez 等从真实 PR 里收集原始任务，每条包含 issue 文本、修复前的仓库快照、参考修复补丁（金补丁）和测试。收完还要实际跑一遍：加入测试补丁，确认至少一个测试在修复前失败、修复后通过（fail-to-pass），安装失败或跑不起来的任务丢掉。论文写全集 2294 条。40% 的题有至少两个 fail-to-pass 测试；中位数还有 51 个原有测试，用来确认旧功能没坏（pass-to-pass）。

Verified 是 OpenAI 和原作者在 2024-08 放出的人审子集，500 条。人审看题面清不清楚、测试对不对、给的信息够不够解题。它仍然是原集的子集，里面没有新题。OpenAI 在 2026-02 写了为什么不再用它报前沿成绩：难例里测试过窄或过宽的比例高，而且前沿模型能复述金补丁，机制见 `dt-agent-verified-stale`。更早的 GPT-5 博文还在报 SWE-bench Verified 74.9%，并写明用的是他们基础设施上校验过的 n=477。GPT-5.6 博文（2026-07）我读到的正文已经不把 Verified 当头条了。

Pro（Deng 等）是另一套题，卡的是更长、多文件的工程改动。它有 1865 条，来自 41 个仍在维护的仓库，业务应用、B2B、开发工具都有。公开集来自 11 个仓库，另有 12 个仓库的 holdout 和 18 个有合作协议的商业私有库。题面经过人工整理：问题陈述限制在原始材料里，需求和接口可以对照金补丁和测试补上，减少「说明里没写、测试却在卡」的情况。Google 2026-02 的卡把 Verified 和 Pro（Public）分成两行，都是 single attempt。Pro 的公开分比 Verified 低一截，是因为题更难、子集也不同，不能理解成同一个模型突然退步了。

Multilingual 考不同编程语言的仓库任务，Opus 4.5 system card 把它单独列了出来。只在 Python 仓库里测的分数，代表不了多语言表现。

## Terminal-Bench

Terminal-Bench 要求模型通过命令行做完一件多步工程任务，比如装环境、跑命令、改文件，最后由测试脚本检查结果。模型可以执行 shell 操作，任务也不限于交一个 git patch。Gemini 3.1 模型卡把 Terminal-Bench 2.0 的结果分开报：一组用统一的 Terminus-2 harness，另一组用各模型方自报的最佳 harness。

同一张卡，2026-02：

| 模型 | Terminus-2 | 自报的另一套 harness |
| --- | --- | --- |
| Gemini 3.1 Pro Thinking High | 68.5% | - |
| Gemini 3 Pro Thinking High | 56.9% | - |
| Sonnet 4.6 Thinking Max | 59.1% | - |
| Opus 4.6 Thinking Max | 65.4% | - |
| GPT-5.2 Thinking xhigh | 54.0% | 62.2%（Codex） |
| GPT-5.3-Codex Thinking xhigh | 64.7% | 77.3%（Codex） |

GPT-5.3-Codex 在 Codex harness 上是 77.3%，在 Terminus-2 上是 64.7%，同一个模型差了 12.6 个点，运行框架对分数的影响就有这么大。要判断模型本身是不是变好了，得固定工具、重试次数和步数再比。

GPT-5.6 博文写它在 Terminal-Bench 2.1 上达到当时的前沿，但正文没给出我能引用的绝对分，2.0 和 2.1 也别写成同一列。Anthropic Opus 4.5 system card 报的是 Terminal-bench 2.0 59.3%，那是 4.5，上表里的是 4.6。

## LiveCodeBench 和 LiveCodeBench Pro

LiveCodeBench 考算法竞赛编程。它从竞赛站收题，按比赛日期开窗口，训练截止之后的新题就能单独报。Llama 4 指令模型卡写的窗口是 2024-10-01 到 2025-02-01，pass@1：Maverick 43.4%，Scout 32.8%。

LiveCodeBench Pro 是另一套题，Gemini 3.1 卡用 Elo 报分，题源写的是 Codeforces、ICPC、IOI：Gemini 3.1 Pro 2887，Gemini 3 Pro 2439，GPT-5.2 2393。Elo 和 pass@1 不能相减。

SciCode 在同一张 Google 卡里单独一行，标注是科研代码：Gemini 3.1 Pro 59%，Gemini 3 Pro 56%，Opus 4.6 52%，GPT-5.2 52%。它要求模型针对论文级的科学问题写出能跑的代码，和修 Django 仓库里的 issue 是两种任务。

## 谁还在报 Verified

| 材料 | 模型 | 数据集 | 设定 | 数 |
| --- | --- | --- | --- | --- |
| OpenAI GPT-5 博文 | GPT-5 | SWE-bench Verified | 他们校验过的 n=477 | 74.9% |
| Anthropic Opus 4.5 system card | Opus 4.5，无 thinking | Verified / Pro / Multilingual | system card 表 | 80.9% / 52.0% / 76.2% |
| 同一张卡 | Opus 4.5，64k thinking | 同上 | | 80.6% / 51.6% / 76.2% |
| Google 模型卡，2026-02 | Gemini 3.1 Pro | Verified，single attempt | | 80.6% |
| 同一张卡的对照列 | Opus 4.6 / GPT-5.2 | Verified，single attempt | | 80.8% / 80.0% |
| 同一张卡 | Gemini 3.1 Pro / GPT-5.2 / GPT-5.3-Codex | SWE-bench Pro Public，single attempt | | 54.2% / 55.6% / 56.8% |

## 追问

**函数题 pass@1 高，但仓库任务分数低，该补什么数据？**
补仓库级任务，并固定用来验证修复的测试，见 `dt-code-repo-vs-fn`。继续生成 HumanEval 风格的函数题，练不到定位仓库问题、完成修复的能力。

**金补丁能用于监督微调（SFT）吗？**
评测任务的金补丁不能进训练，否则后面的分数可能只反映模型记住了答案。训练可以选时间更早、和评测隔离的仓库，或者在执行环境里生成操作轨迹，再用测试验证。

**通过了测试的 SWE 轨迹，能直接拿来训练吗？**
先查轨迹有没有改测试，或者利用了不该利用的环境状态，见 `dt-swe-success-noise`。评测仓库和训练仓库还要按时间和哈希隔离，见 `dt-code-hidden-tests`。

**LiveCodeBench 查污染，要看什么？**
看模型有没有见过竞赛题解博客。这和 SWE-bench 里 GitHub issue 的泄漏是两回事，按比赛日期开窗口就是为了把训练截止之后的新题单独拿出来报。

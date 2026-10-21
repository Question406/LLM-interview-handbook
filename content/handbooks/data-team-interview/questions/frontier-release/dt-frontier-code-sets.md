---
id: dt-frontier-code-sets
section: frontier-release
order: 3
level: S
title: SWE-bench、Terminal-Bench、LiveCodeBench 怎么造，各卡哪段代码能力？
quick: "SWE-bench 要求模型修复真实 GitHub issue：新测试要从失败变为通过，旧测试仍要通过。Terminal-Bench 要求通过终端完成工程任务，运行框架会明显影响分数。LiveCodeBench 按比赛日期划分新题，主要测算法编程并减少背题影响。三种分数不能直接合并比较。"
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

听到代码评测分数，先确认任务是什么。SWE-bench 是在真实仓库里修 issue，Terminal-Bench 是通过终端完成多步工程任务，LiveCodeBench 是按比赛日期切出来的算法新题。写函数、修仓库、跑终端需要的能力不同，不能用一个 coding 分数概括。

从数据组的角度看，SWE-bench Verified 在 Google 2026-02 的表里已接近 80%，Pro 仍在 50% 出头。要找还能改进的失败，先分析 Pro 和 Terminal-Bench 里仍然失败的任务类型，通常比围绕 Verified 的一个百分点调整数据比例更有信息。比较模型增益时，要固定运行框架（harness）、工具、重试次数和步数，否则分数变化可能来自执行环境。

## SWE-bench 家族

SWE-bench 考查模型能否读懂 issue，找到需要修改的位置，完成修复并保留原有功能。Jimenez 等从真实 PR 中收集了原始任务。每条任务包含 issue 文本、修复前的仓库快照、参考修复补丁（金补丁）和测试。收集后还要实际运行：加入测试补丁，确认至少一个测试在修复前失败、修复后通过（fail-to-pass）。安装失败或无法运行的任务被丢弃。论文写全集 2294 条。40% 的题有至少两个 fail-to-pass 测试；中位数还有 51 个原有测试，用来确认旧功能没坏（pass-to-pass）。

Verified 是 OpenAI 和原作者在 2024-08 放出的人审子集，500 条。人审看的是题面是否清楚、测试是否正确、给的信息够不够解题。它仍然是原集的子集，不是新题。OpenAI 在 2026-02 写了为什么不再用它报前沿成绩：难例里测试过窄或过宽的比例高，而且前沿模型能复述金补丁，机制见 `dt-agent-verified-stale`。更早的 GPT-5 博文还在报 SWE-bench Verified 74.9%，并写明用的是他们基础设施上校验过的 n=477。GPT-5.6 博文（2026-07）我读到的正文不再把 Verified 当头条。

Pro（Deng 等）是另一套题，卡的是更长的、多文件的工程改动。它有 1865 条，来自 41 个仍在维护的仓库，业务应用、B2B、开发工具都有。公开集来自 11 个仓库，另有 12 个仓库的 holdout 和 18 个有合作协议的商业私有库。题面经过人工整理：问题陈述限制在原始材料里，需求和接口可以对照金补丁和测试补上，减少「说明里没写、测试却在卡」的情况。Google 2026-02 的卡把 Verified 和 Pro（Public）分成两行，都是 single attempt。Pro 的公开分比 Verified 低一截，原因是题更难、子集也不同，不是同一个模型突然退步。

Multilingual 考查不同编程语言的仓库任务，Opus 4.5 system card 将它单独列出。只在 Python 仓库中测得的分数，不能代表多语言表现。

把这类任务用于训练前，还要检查通过测试的操作轨迹是否修改了测试，或利用了不该利用的环境状态，见 `dt-swe-success-noise`。评测仓库与训练仓库要按时间和哈希隔离，见 `dt-code-hidden-tests`。

## Terminal-Bench

Terminal-Bench 要求模型通过命令行完成一项多步工程任务，例如安装环境、运行命令、修改文件，最后由测试脚本检查结果。模型可以执行 shell 操作，任务也不限于提交一个 git patch。Gemini 3.1 模型卡把 Terminal-Bench 2.0 的结果分开报告：一组使用统一的 Terminus-2 harness，另一组使用各模型方自报的最佳 harness。

同一张卡，2026-02：

| 模型 | Terminus-2 | 自报的另一套 harness |
| --- | --- | --- |
| Gemini 3.1 Pro Thinking High | 68.5% | - |
| Gemini 3 Pro Thinking High | 56.9% | - |
| Sonnet 4.6 Thinking Max | 59.1% | - |
| Opus 4.6 Thinking Max | 65.4% | - |
| GPT-5.2 Thinking xhigh | 54.0% | 62.2%（Codex） |
| GPT-5.3-Codex Thinking xhigh | 64.7% | 77.3%（Codex） |

GPT-5.3-Codex 在 Codex harness 上是 77.3%，在 Terminus-2 上是 64.7%。同一个模型两组结果相差 12.6 个点，说明运行框架会明显影响分数。要判断模型本身是否变好，需要固定工具、重试次数和步数后再比较。

GPT-5.6 博文写它在 Terminal-Bench 2.1 上达到当时的前沿，但正文没有给出我能引用的绝对分。2.0 和 2.1 不要写成同一列。Anthropic Opus 4.5 system card 报的是 Terminal-bench 2.0 59.3%，那是 4.5，不是上表里的 4.6。

## LiveCodeBench 和 LiveCodeBench Pro

LiveCodeBench 考查算法竞赛编程。它从竞赛站收题，按比赛日期开窗口，这样训练截止之后的新题可以单独报。检查训练污染时，要关注模型是否见过竞赛题解博客，这和 SWE-bench 中的 GitHub issue 泄漏不是一回事。Llama 4 指令模型卡写的窗口是 2024-10-01 到 2025-02-01，pass@1：Maverick 43.4%，Scout 32.8%。

LiveCodeBench Pro 是另一套题，Gemini 3.1 卡用 Elo 报分，题源写的是 Codeforces、ICPC、IOI。Gemini 3.1 Pro 2887，Gemini 3 Pro 2439，GPT-5.2 2393。Elo 和 pass@1 不能相减。

SciCode 在同一张 Google 卡里单独一行，标注是科研代码。Gemini 3.1 Pro 59%，Gemini 3 Pro 56%，Opus 4.6 52%，GPT-5.2 52%。它要求模型针对论文级的科学问题编写可运行的代码，和修复 Django 仓库里的 issue 是不同的任务。

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

- **函数题 pass@1 高，但仓库任务分数低，该补什么数据？** 补仓库级任务，并固定用于验证修复的测试，见 `dt-code-repo-vs-fn`。继续生成 HumanEval 风格的函数题，练不到定位仓库问题、完成修复的能力。
- **金补丁能用于监督微调（SFT）吗？** 评测任务的金补丁不能进训练，否则后续分数可能反映的是模型记住了答案。训练可以选用时间更早、与评测隔离的仓库，或者在执行环境中生成操作轨迹，再用测试验证。

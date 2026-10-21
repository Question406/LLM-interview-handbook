---
id: dt-agent-verified-stale
section: posttrain-data
order: 24
level: S
title: 为什么 OpenAI 不再用 SWE-bench Verified 报成绩？这对训练数据意味着什么？
quick: "不能直接算赢。分数涨了先查两件事：测试是否在考题面没写的要求，题目和标准补丁是否进了训练。Verified 人审过 500 题，仍然有测试质量和泄漏问题，OpenAI 2026-02 已停报。训练池与评测池要隔离，并保留按时间划分、可刷新的 holdout。"
companies:
  - apple
tags:
  - Apple
  - Agent
  - Evaluation
  - Contamination
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Why we no longer evaluate SWE-bench Verified
    url: https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
    type: primary
  - title: Separating signal from noise in coding evaluations
    url: https://openai.com/index/separating-signal-from-noise-coding-evaluations/
    type: primary
  - title: Introducing SWE-bench Verified
    url: https://openai.com/index/introducing-swe-bench-verified/
    type: primary
  - title: SWE-rebench
    url: https://arxiv.org/abs/2505.20411
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

Verified 涨了不能直接当赢。分数上涨后，先检查测试质量和泄漏，再对外报告。如果测试实际要求的是官方那种修法，而题目又被抓进了训练，分数反映的可能只是模型见过这道题。所以评测数据要单独保护：训练池和评测池隔离，并按时间留出 holdout。

OpenAI 2024-08 人审放出 Verified 500 条，2026-02 停报前沿成绩。停报的原因有两条，下面分开说。

## 原因一：测试本身有质量问题

他们复审了 o3 在 64 次尝试里经常解不出的 138 题（约 27.6%），每题至少 6 个工程师看过。其中 59.4% 有实质性的测试或说明问题：35.5% 测得过窄，卡的是说明里没写的实现细节，比如必须叫某个函数名；18.8% 测得过宽，测了说明里没有的功能。功能等价的补丁被拒，分数就低估了能力。

## 原因二：训练可能见过题目

题目来自大家都会抓取的开源仓库。他们测到前沿模型能复述金补丁或题面原句，说明至少见过一部分。见过题的模型更容易通过那些 underspecified 的测试，因为这些测试考的恰好是官方修法。两条原因就这样叠在一起，让分数偏高。

## 数据组该怎么做

**把评测集当稀缺资产。** Verified 这种人审过的 500 条，一旦进过训练或合成教师的检索库，就作废了。用 n-gram 和补丁指纹去污，见 `dt-ngram-contam-code`、`dt-code-bench-bleed`。

**训练用可刷新的池。** SWE-rebench 按 GitHub 时间持续收新 issue；2025-08 那篇 SWE 强化学习（RL）把某两个月留作 holdout。持续更新评测题，可以减少反复优化固定 500 题带来的偏差。公开 SWE 分数只当参考，内部门禁用许可仓库的私有 holdout。

**新榜单不会自动免疫。** OpenAI 一度让社区改报 SWE-bench Pro，随后在 Separating signal from noise 里估计 Pro 约 30% 的题是坏的，又收回了推荐。根源在于 GitHub issue 本来是给人协作用的，说明、合入的代码和单测本来就对不齐。多语言 rebench 等新集也一样，我会先问它是否进过抓取器，以及测试是否在考说明里的事。

**发现泄漏或测试有问题时，** 先停报、换 holdout、把问题写进 datasheet。这时候去调超参把分调回来，只会把问题盖住。

## 追问

- **那 Verified 还有用吗？** 有。它的人审清单（说明够不够、测试是否过窄或过宽、环境能否复现）可以在过滤训练池时当样例。我只是不会拿它当唯一的对外数字。

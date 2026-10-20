---
id: dt-agent-verified-stale
section: posttrain-data
order: 24
level: S
title: 为什么 OpenAI 不再用 SWE-bench Verified 报成绩？这对训练数据意味着什么？
quick: "评测分数提高后，先查测试是否考了题面没说明的要求，再查题目和标准补丁是否进入训练。Verified 曾人工审查 500 题，但仍存在测试质量和泄漏问题。训练池与评测池应隔离，并保留按时间划分、可更新的 holdout。"
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

评测数据需要单独保护：隔离训练池和评测池，并按时间留出 holdout。分数上涨后，先检查测试质量和泄漏，再对外报告。

常见误区是：Verified 涨了就当赢。如果测试要求采用官方修法，题目又被抓入训练，分数便可能反映模型见过这道题。公开锚点是 OpenAI 2024-08 做人审放出 Verified 500 条，2026-02 停报前沿成绩。两条原因，不是一句「太简单」。

## 两类问题

测试仍有质量问题。他们审了 o3 在 64 次里经常解不出的 138 题（约 27.6%），至少 6 个工程师看。59.4% 有实质性测试 / 说明问题：35.5% 过窄（测在卡没写进说明的实现细节，比如必须叫某个函数名），18.8% 过宽（测了说明里没有的功能）。功能等价的补丁被拒，分数低估能力。

训练可能见过题目。题来自大家都会抓的开源仓。他们测到前沿模型能复述金补丁或题面原句，说明至少见过一部分。见过的模型更可能过那些 underspecified 的测，因为测在考官方修法。

## 对数据组

评测集当稀缺资产。Verified 这种人审过的 500 条，一旦进过训练或合成教师的检索库，就废了。n-gram / 补丁指纹去污，见 `dt-ngram-contam-code`、`dt-code-bench-bleed`。

训练用可刷新池。SWE-rebench 按 GitHub 时间收新 issue。2025-08 那篇 SWE 强化学习（RL） 把某两个月留作 holdout。持续更新评测题，能减少反复优化固定 500 题带来的偏差。

新的榜单也可能有同样问题。他们一度让社区改报 SWE-bench Pro，随后在 Separating signal from noise 里估计 Pro 约 30% 的题是坏的，收回推荐。GitHub issue 当初是给人协作的，说明、合入代码、单测本来就对不齐。

苹果：公开 SWE 分数只能当参考。内部用许可仓库的私有 holdout。用户工单默认不进基础模型，也不能拿来刷公开榜。

## 追问

- **那 Verified 还有没有用？** 有：人审清单（说明够不够、测是否过窄过宽、环境能否复现），过滤训练池时当样例。我不会拿它当唯一对外数字。
- **SWE-bench Pro / 多语言 rebench？** 同样会被污染，测试同样可能过窄。我会先问它是否进过抓取器，以及测试是否在考说明里的事。
- **发现泄漏或测有病怎么办？** 我会停报、换 holdout、把问题写进 datasheet。不要先调超参把分调回来。

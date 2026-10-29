---
id: dt-code-bench-bleed
section: labs
order: 24
level: A
title: 开源代码合成集自称 HumanEval +9%，你先查什么？
quick: 假设开源合成集宣称让公开 benchmark 提升很多。我会先查训练 seed、生成 prompt 和筛选规则，有没有直接使用测试题、参考答案或它们的改写。
companies:
  - apple
tags:
  - Coding
  - Contamination
  - LiveCodeBench
  - Apple
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: On Leakage of Code Generation Evaluation Datasets
    url: 'https://arxiv.org/abs/2407.07565'
    type: primary
  - title: LiveCodeBench
    url: 'https://arxiv.org/abs/2403.07974'
    type: primary
  - title: LessLeak-Bench
    url: 'https://arxiv.org/abs/2502.06215'
    type: primary
---

## 回答思路

> **问题与场景：** 假设开源合成集宣称让公开 benchmark 提升很多。
>
> **做法与原因：** 再对训练与评测做多种重叠检查，并抽查命中样本。
>
> **检查与取舍：** 确认来源后，用独立任务和匹配预算做对照。

## 可以这样回答

假设开源合成集宣称让公开 benchmark 提升很多。我会先查训练 seed、生成 prompt 和筛选规则，有没有直接使用测试题、参考答案或它们的改写。

再对训练与评测做多种重叠检查，并抽查命中样本。只换名字、数字或语言，并不保证是独立任务；同一题的变体需要一起处理。

确认来源后，用独立任务和匹配预算做对照。不能把整个数据集先加进去，再用同一个公开榜单证明它有效。

## 技术备查

先查涨分是不是来自 leakage，排除之后再谈执行过滤和 teacher 质量。代码合成集涨分是有前科的：Rando 等（2024）比较过 evol-instruct、StarCoder-Instruct 和 HumanEval / MBPP 的 embedding nearest neighbors，加入 evol-instruct 后 HumanEval 约涨 9%，MBPP 涨 2%，更难的 LBPP 却不变。

这几乎就是题目里的情况。一个合成集说自己 HumanEval +9%，换到更难、更新的题上却不涨，最可能的解释是合成题和 HumanEval 长得太像。

我会先把 HumanEval、MBPP、LiveCodeBench 和内部检查集的题面及 canonical 解固定下来，再拿去和训练数据比：精确匹配、13-gram、去注释并重命名变量之后的代码，以及 embedding nearest neighbors。

然后用 LiveCodeBench 看泛化，它只用训练截止之后的竞赛题。旧题涨、新题不动，报告里就算写着提高了 15%，也证明不了 generalization。

SWE 类任务还要多查几样：issue URL、PR diff、测试文件路径，都和 training set deduplication。模型改了测试补丁里的文件，整段 trajectories 直接丢掉，见 `dt-swe-success-noise`。

## 追问

**作者说已经去过污了，还要再查吗？**
要。开源合成集的作者可能只针对 2023 年那版 HumanEval 查过，下载混进训练之前，要用自己的评测版本再核一遍。

**为什么代码题光靠 n-gram 不够？**
代码题短、变体多，单靠 n-gram 会漏掉改了变量名或注释的版本，所以要加上规范化代码和 embedding nearest neighbors。

**SWE-bench Verified 有人审过，还会 leakage 吗？**
会。GitHub issue 早就进了 pre-training 抓取。LessLeak-Bench 扫了 83 个软件工程基准，SWE-bench leakage 约 8.7%，SWE-bench-verified 约 10.6%。Verified 的人审主要看任务能不能解，不保证模型训练时没见过 issue，这是两项不同的检查。

**内部评测也要防吗？**
要。生成 prompt 里要是带了内部评测题，内部榜一样失效。所以生成器不能接触评测题，评测要和生成器隔离，见 `dt-contamination`。

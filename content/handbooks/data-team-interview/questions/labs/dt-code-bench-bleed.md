---
id: dt-code-bench-bleed
section: labs
order: 24
level: A
title: 开源代码合成集自称 HumanEval +9%，你先查什么？
quick: "先查是不是泄漏，再谈质量。固定评测题与参考解，用精确匹配、13-gram、代码规范化与 embedding 近邻和训练集比对；再用训练截止后的 LiveCodeBench 新题验证泛化。旧题涨、新题不变，就不能把涨分当作能力提升。SWE 类还要查 issue、PR 和测试文件。"
companies:
  - apple
tags:
  - Coding
  - Contamination
  - LiveCodeBench
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "On Leakage of Code Generation Evaluation Datasets"
    url: https://arxiv.org/abs/2407.07565
    type: primary
  - title: LiveCodeBench
    url: https://arxiv.org/abs/2403.07974
    type: primary
  - title: LessLeak-Bench
    url: https://arxiv.org/abs/2502.06215
    type: primary
---

先查涨分是不是来自泄漏，确认不是之后，再讨论执行过滤和教师质量。代码合成集涨分有前科：Rando 等（2024）比较过 evol-instruct、StarCoder-Instruct 与 HumanEval / MBPP 的 embedding 近邻，加入 evol-instruct 后 HumanEval 约涨 9%，MBPP 涨 2%，更难的 LBPP 却不变。

## 作者的去污声明要重查

开源合成集作者可能只针对 2023 年那版 HumanEval 做过检查。下载混入训练前，要用自己的评测版本重新核对一遍。

代码题还特别容易漏检：题短、变体多，单靠 n-gram 匹配会漏掉改了变量名或注释的版本。另一条泄漏路径是 GitHub issue 早已进入预训练抓取。LessLeak-Bench 扫描了 83 个软件工程基准，SWE-bench 泄漏约 8.7%，SWE-bench-verified 约 10.6%。Verified 的人审主要检查任务是否可解，不保证模型没在训练时见过 issue，这是两项不同的检查。

## 怎么查

1. 固定 HumanEval、MBPP、LiveCodeBench 和内部检查集的题面及 canonical 解，再与训练数据对比。
2. 检查精确匹配、13-gram、去注释与重命名变量后的代码，以及 embedding 近邻。
3. 用 LiveCodeBench 验证泛化。它只使用训练截止后的竞赛题；如果旧题涨而新题不变，即使报告提高了 15%，也不能证明泛化能力。
4. SWE 类任务还要检查 issue URL、PR diff、测试文件路径，并与训练集去重。模型修改了测试补丁中的文件，整段轨迹应丢弃，见 `dt-swe-success-noise`。

## 内部评测也一样

内部评测也会被污染：如果生成 prompt 带了内部评测题，内部榜同样失效。所以生成器不能接触评测题，评测必须与生成器隔离，见 `dt-contamination`。

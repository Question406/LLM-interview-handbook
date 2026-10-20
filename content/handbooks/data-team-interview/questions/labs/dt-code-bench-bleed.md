---
id: dt-code-bench-bleed
section: labs
order: 24
level: A
title: 开源代码合成集自称 HumanEval +9%，你先查什么？
quick: "先固定评测题与参考解，再检查精确匹配、13-gram、代码规范化与 embedding 近邻。用训练截止后的 LiveCodeBench 新题验证泛化。SWE 类还要查 issue、PR 和测试文件；旧题涨、新题不变时，不能把涨分直接当作能力提升。"
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

先固定 HumanEval、MBPP、LiveCodeBench 和内部检查集的题面及 canonical 解，再与训练数据对比。检查精确匹配、13-gram、去注释与重命名变量后的代码，以及 embedding 近邻。代码题短、变体多，单靠 n-gram 容易漏掉。

LiveCodeBench 只使用训练截止后的竞赛题。如果旧题涨而新题不变，即使报告提高了 15%，也不能据此证明泛化能力。SWE 类任务还要检查 issue URL、PR diff、测试文件路径，并与训练集去重。模型修改了测试补丁中的文件，整段轨迹应丢弃，见 `dt-swe-success-noise`。这些检查通过后，再讨论执行过滤和教师质量。

## 不要直接相信外部去污声明

开源合成集作者可能只针对 2023 年那版 HumanEval 做过检查。下载混入训练前，要用自己的评测版本重新核对，不能仅凭「已经去污」就接受。

AFM 的 mid-training 公开写了经过验证的合成数据，没有写把 WizardCoder 数据直接混入。生成 prompt 如果带了内部评测题，内部榜同样会污染；生成器不能获取评测题，见 `dt-contamination`。SWE-bench-verified 的人审主要检查任务是否可解，不保证模型没在训练时见过 issue。轨迹来源仍应是许可仓库或合成环境。

## 公开案例

Rando 等（2024）比较过 evol-instruct、StarCoder-Instruct 与 HumanEval / MBPP 的 embedding 近邻。加入 evol-instruct 后，HumanEval 约涨 9%，MBPP 涨 2%，更难的 LBPP 却不变。

LessLeak-Bench 扫描了 83 个软件工程基准：SWE-bench 泄漏约 8.7%，SWE-bench-verified 约 10.6%。主要原因是 GitHub issue 早已进入预训练抓取。

## 追问

- 作者已对 HumanEval 去污，还要再查吗？要，用自己的评测版本核对。
- Verified 已经人审，为什么仍会泄漏？任务可解与训练中未见过任务，是两项不同检查。
- 内部题也会污染吗？会，尤其是把题面放入生成 prompt 时。评测必须与生成器隔离。

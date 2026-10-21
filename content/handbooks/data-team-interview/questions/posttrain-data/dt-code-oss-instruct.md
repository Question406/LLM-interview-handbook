---
id: dt-code-oss-instruct
section: posttrain-data
order: 6
level: S
title: 代码指令数据：从开源片段造题（OSS-Instruct），比让教师空手编好在哪？
quick: "从许可仓库抽真实代码片段让教师据此出题，题目会覆盖 API、并发、文件和错误处理这些实际问题，比教师凭空反复生成教材题更能保持多样性。仍要检查片段许可证、用执行测试把关、扫描与 HumanEval 的重叠。OSS-Instruct 管覆盖，Evol-Instruct 管难度，两者可以叠用。"
companies:
  - apple
tags:
  - Apple
  - Coding
  - Synthetic Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "Magicoder: Empowering Code Generation with OSS-Instruct"
    url: https://arxiv.org/abs/2312.02120
    type: primary
  - title: WizardCoder Evol-Instruct
    url: https://arxiv.org/abs/2306.08568
    type: primary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

我会从许可仓库里抽真实代码片段，让教师据此生成题目，这样题目的多样性来自仓库里的实际用法。之后还要检查片段的许可证，固定用于验证的测试，并扫描和 HumanEval 的重叠。

## 为什么种子要用真实代码

教师凭空出题，题目容易集中在教材里的常见题。空手做 Self-Instruct 会反复出排序、斐波那契、两数之和；Evol-Instruct（WizardCoder 的做法）是在 GPT 文风里把已有指令改难，覆盖面仍然塌在教材题上。真实仓库里有 API、并发、文件和错误处理，能提供更多实际问题。Magicoder 的 OSS-Instruct 就是这个思路，75k 量级的数据就能把 7B 模型推得很高。

用片段当种子还有两个好处：

- **可控。** 片段决定主题。想补 SQL 就去抽 SQL 文件，不用指望教师自己想起来。
- **偏置更轻。** 教师的文风还在，但题面被片段钉住了，假多样性少一些。教师偏差（`dt-teacher-bias`）依然存在，只是轻一点。

OSS-Instruct 和 Evol-Instruct 是正交的：前者扩覆盖，后者抬难度，Magicoder 也把两者叠起来用过。顺序上先用 OSS 做多样化，再用 evol 变难，相当于 `dt-math-passk-band` 的代码版。

## 仍然要挡的三件事

**许可。** 片段来自什么许可证的仓库，生成的指令数据就继承什么问题。不能用于训练的数据，效用为零，见 `dt-license-is-quality`。

**泄漏。** 种子如果来自 HumanEval 或 MBPP 的副本，就会污染评测，见 `dt-code-bench-bleed`。

**没有测试的解。** OSS-Instruct 的数据常常没有单测，这种解只能当弱监督微调（SFT）数据。主集仍然要跑测试，教师写得「看起来对」不够。Llama 3 的代码合成是另一条路：从片段造题、造解、造测试，再用执行反馈修改。两条路可以接起来用：OSS-Instruct 提供多样性，执行门保证质量，见 `dt-code-exec-synth`。

## 追问

- **75k 算不算 LIMA 那种少量精标？** 不算一回事。代码有 grader，75k 条过了执行的轨迹，和 1000 条聊天精标的稀缺性不同，见 `dt-lima-vs-scale`。
- **要蒸给小模型怎么用？** 蒸馏过了执行的短轨迹，整个仓库的 diff 对小模型太长，见 `dt-ondevice-distill-data`。

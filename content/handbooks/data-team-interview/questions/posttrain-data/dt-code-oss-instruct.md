---
id: dt-code-oss-instruct
section: posttrain-data
order: 6
level: S
title: 代码指令数据：从开源片段造题（OSS-Instruct），比让教师空手编好在哪？
quick: "从许可仓库的真实代码片段生成题目，能覆盖 API、并发、文件和错误处理等实际问题，比教师凭空反复生成教材题更容易保持多样性。仍要检查许可证、执行测试和 HumanEval 重叠。OSS-Instruct 增加覆盖，Evol-Instruct 可以进一步增加难度。"
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

我会从许可仓库抽取真实代码片段，让教师据此生成题目。这样题目多样性来自仓库中的实际用法。仍要检查片段许可证，固定用于验证的测试，并扫描与 HumanEval 的重叠。

不这么选的理由：空手 Self-Instruct 会反复出排序、斐波那契、两数之和。Evol-Instruct 在 GPT 文风里把已有指令改难，覆盖仍塌在教材题。Magicoder 的 OSS-Instruct，75k 量级就能把 7B 推得很高。WizardCoder 的 Evol-Instruct 是把已有指令改难。两条正交，他们也叠过。

苹果：许可片段才能进。用户日志不进基础模型。OSS-Instruct 出多样性，执行门当质量，见 `dt-code-exec-synth`。

## 为什么种子要真实代码

真实仓库包含 API、并发、文件和错误处理，能提供更多实际问题。教师凭空生成时，题目容易集中在教材中的常见题。

可控：片段决定主题。想补 SQL 就抽 SQL 文件，不必盼着教师自己想起。

偏置：教师文风仍在，但题面被片段钉住，假多样性少一点。`dt-teacher-bias` 还在，只是轻一些。

Llama 3 代码合成是另一条：从片段造题、造解、造测，执行反馈改。OSS-Instruct 常没有单测。苹果这轮要把两条接上。

## 仍要挡的

许可。片段来自什么许可证的仓库，指令数据继承问题。不能训的效用是零，见 `dt-license-is-quality`。

泄漏。种子若来自 HumanEval / MBPP 的副本，见 `dt-code-bench-bleed`。

没有测试的解。只能当弱 监督微调（SFT）。主集仍要跑测试。教师写的「看起来对」不够。

## 追问

- **Evol-Instruct 还要不要？** 要，用来抬难度带，见 `dt-math-passk-band` 的代码版。先 OSS 多样化，再 evol 变难。
- **75k 是不是 LIMA？** 代码有 grader，75k 过执行的轨迹和 1000 条聊天精标不是同一稀缺，见 `dt-lima-vs-scale`。
- **端侧代码助手？** 蒸过执行的短轨迹，不要蒸整个仓库 diff，见 `dt-ondevice-distill-data`。

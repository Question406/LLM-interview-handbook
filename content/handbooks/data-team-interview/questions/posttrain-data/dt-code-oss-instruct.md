---
id: dt-code-oss-instruct
section: posttrain-data
order: 6
level: S
title: 代码指令数据：从开源片段造题（OSS-Instruct），比让 teacher 空手编好在哪？
quick: >-
  从许可仓库抽真实代码片段，让 teacher 照着片段出题，题目会覆盖 API、并发、文件和错误处理这些实际问题，比 teacher
  凭空反复出教材题更能保持多样性。片段许可证、执行测试和与 HumanEval 的重叠仍然要查。OSS-Instruct 管覆盖，Evol-Instruct
  管难度，两者可以叠着用。
companies:
  - apple
tags:
  - Apple
  - Coding
  - Synthetic Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: 'Magicoder: Empowering Code Generation with OSS-Instruct'
    url: 'https://arxiv.org/abs/2312.02120'
    type: primary
  - title: WizardCoder Evol-Instruct
    url: 'https://arxiv.org/abs/2306.08568'
    type: primary
  - title: The Llama 3 Herd of Models
    url: 'https://arxiv.org/abs/2407.21783'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

我会从许可仓库里抽真实代码片段，让 teacher 照着片段出题，题目的多样性就来自仓库里的实际用法。之后还要查片段的许可证，固定用于验证的测试，扫描和 HumanEval 的重叠。

teacher 空手出题，题目会集中在教材常见题上。空手做 Self-Instruct 会反复出排序、斐波那契、两数之和；Evol-Instruct（WizardCoder 的做法）是在 GPT 文风里把已有指令改难，覆盖面还是塌在教材题上。真实仓库里有 API、并发、文件和错误处理，实际问题多得多。Magicoder 的 OSS-Instruct 就是这个思路，75k 量级的数据就能把 7B 模型推得很高。

用片段当 seed 还有两个好处。一是可控，片段决定主题，想补 SQL 就去抽 SQL 文件，不用指望 teacher 自己想起来。二是偏置更轻，teacher 的文风还在，但题面被片段钉住了，假多样性少一些；teacher 偏差（`dt-teacher-bias`）依然存在，只是轻一点。

OSS-Instruct 和 Evol-Instruct 是正交的，前者扩覆盖，后者抬难度，Magicoder 也把两者叠起来用过。

剩下要挡的是许可、leakage 和没有测试的解。片段来自什么许可证的仓库，生成的指令数据就继承什么问题，不能用于训练的数据效用为零（见 `dt-license-is-quality`）。seed 要是来自 HumanEval 或 MBPP 的副本，就会 contamination 评测（见 `dt-code-bench-bleed`）。OSS-Instruct 的数据常常没有单测，这种解只能当弱 SFT 数据，主集还是要跑测试，teacher 写得「看起来对」不够。

## 追问

**OSS-Instruct 和 Evol-Instruct 先用哪个？**
先用 OSS 做多样化，再用 evol 变难，相当于 `dt-math-passk-band` 的代码版：先把覆盖面铺开，再在上面抬难度。

**Llama 3 的代码合成和这个是什么关系？**
是另一条路：从片段造题、造解、造测试，再用执行反馈修改。两条路可以接起来用，OSS-Instruct 提供多样性，执行门保证质量，见 `dt-code-exec-synth`。

**75k 算不算 LIMA 那种少量精标？**
算不上一回事。代码有 grader，75k 条过了执行的 trajectories，和 1000 条聊天精标的稀缺性不同，见 `dt-lima-vs-scale`。

**要蒸给 small model 怎么用？**
distillation 过了执行的短 trajectories，整个仓库的 diff 对 small model 太长，见 `dt-ondevice-distill-data`。

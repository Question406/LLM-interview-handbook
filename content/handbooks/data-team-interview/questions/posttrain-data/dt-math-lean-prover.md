---
id: dt-math-lean-prover
section: posttrain-data
order: 4
level: A
title: Lean / 形式化证明能不能当数学后训练的 oracle？
quick: "能，但只覆盖形式化证明。Lean 的 kernel 逐步检查证明，比只看最终 boxed 答案可靠，通过编译和证明检查的才算正例。DeepSeek-Prover 先用成功证明和子目标冷启动，再用 Lean 反馈做 RL。自然语言计算题仍要靠 TIR 等方法验证，两类数据和 grader 分开记录、分开评测。"
companies:
  - apple
tags:
  - Apple
  - Math
  - Verifier
  - RLVR
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: DeepSeek-Prover-V1.5
    url: https://arxiv.org/abs/2408.08152
    type: primary
  - title: DeepSeek-Prover-V2
    url: https://arxiv.org/abs/2504.21801
    type: primary
  - title: MiniF2F
    url: https://arxiv.org/abs/2109.00110
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

能，但它只覆盖形式化证明这一类任务。Lean 的 kernel 会逐步检查形式化证明，通过编译和证明检查的才算正例，可靠性比只检查最终数字强。小学应用题这类自然语言计算题它帮不上，仍要用 TIR 等方法验证，两类 grader 分开记录。

## 为什么比检查答案可靠

只检查 boxed 答案时，中间推理错了、碰巧答案对的回答，也可能被自然语言 verifier 放过。Lean 4 的 kernel 检查的是每一步形式化推导，过不了就不算正例，不存在「答案对但证明错」的漏洞。

公开配方以 DeepSeek-Prover-V2 为代表：用大模型把定理拆成子目标，把成功的形式化步骤拼起来做冷启动数据，再做强化学习（RL）。MiniF2F 是常用的门禁。AlphaProof 那条线结构相同，面试不需要讲它的内部细节。

## 数据怎么组织

先定正例：完整可编译的证明，或者通过检查的子目标 tactic 序列。失败 tactic 在 infoview 里的报错可以放进观察，但不进交叉熵损失（CE），处理方式和工具返回一样。

再做冷启动。如果模型完全不会 Lean，先用人写或教师写的成功证明做监督微调（SFT）。从零开始纯 RL，格式会崩，这和 R1-Zero 需要冷启动是同一个教训，见 `dt-rlvr-data`。

然后拆子目标。把大定理切成若干 lemma，每个 lemma 有自己的 grader。要抽查切分结果：如果切出来的 lemma 比原题还强，模型学到的就是用不上的引理。

## 覆盖边界

竞赛计算题、应用题、需要单位换算的题，Lean 数据帮不上，走 `dt-math-tir-data`。形式化库（mathlib）的许可要核实。另外，MiniF2F 一旦写进训练集，这道门禁就作废了，见 `dt-math-rewrite-leak`。

## 追问

- **自然语言思维链（CoT，即分步推理过程）和 Lean 能混在一条 SFT 样本里吗？** 可以。Prover-V2 就把非正式推理和正式证明接在一起，但 loss mask 仍按角色：Lean 代码进 CE，kernel 输出不进。
- **过了 MiniF2F 就等于数学变好了？** 只说明形式化证明任务有改善，GSM8K 可能没变化。两类结果要分开报告。
- **tactic 搜出来的证明人看不懂怎么办？** 当 RL 正例可以。但 SFT 主集要可读，否则学生只学到搜索痕迹。

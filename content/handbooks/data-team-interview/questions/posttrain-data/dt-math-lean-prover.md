---
id: dt-math-lean-prover
section: posttrain-data
order: 4
level: A
title: Lean / 形式化证明能不能当数学后训练的 oracle？
quick: "能。Lean 的 kernel 可以验证形式化证明，可靠性比只检查最终数字更强。DeepSeek-Prover 先用成功证明和子目标冷启动，再用 Lean 反馈做 RL。不过它覆盖形式化证明，自然语言计算题仍需要 TIR 等验证方法，两类数据分别评价。"
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

形式化证明单独处理，通过编译和证明检查的才作正例。这类数据覆盖证明任务，不能替代小学应用题等自然语言计算题；后者仍可以使用 TIR。两类 grader 分别记录。

只检查 boxed 答案时，中间证明错误的回答也可能被自然语言 verifier 放过。Lean 4 的 kernel 则检查形式化步骤，不能通过的证明不作正例。DeepSeek-Prover-V2：大模型拆子目标，成功的形式化步骤拼成冷启动，再 强化学习（RL）。MiniF2F 是常见门禁。AlphaProof 那条线同构，面试不需要内部细节。

AFM 没有公开 Lean 管线。面试中可以把形式化证明作为可验证奖励的一种方案，但不能声称苹果已经使用它。用户日志不进基础模型。

## 数据合同

正例：完整可编译证明，或通过的子目标 tactic 序列。失败 tactic 的 infoview 报错可以进观察，不进 交叉熵损失（CE），和工具返回一样。

冷启动：完全不会 Lean 时先 监督微调（SFT） 人写 / 教师写的成功证明。纯 RL 从零，格式会崩，和 R1-Zero 要冷启动是同一教训，见 `dt-rlvr-data`。

子目标：把大定理切成 lemma。每个 lemma 自己有 grader。切错（lemma 比原题更强）会让模型学到不可用的引理，抽查。

## 覆盖边界

竞赛计算题、应用题、需要单位换算的，Lean 数据帮不上，走 `dt-math-tir-data`。形式化库（mathlib）许可要核。把 MiniF2F 写进训练，门禁作废，见 `dt-math-rewrite-leak`。

## 追问

- **自然语言 思维链（CoT，即分步推理过程） 和 Lean 混在一条 SFT？** Prover-V2 把非正式推理和正式证明接到一起，但 mask 仍按角色。Lean 代码进 CE，kernel 输出不进。
- **过了 MiniF2F 等于数学好了？** 说明形式化证明任务有改善，GSM8K 可能没有变化。两类结果分开报告。
- **tactic 搜出来的证明人看不懂？** 当 RL 正例可以。SFT 主集要可读，否则学生只学搜索痕迹。

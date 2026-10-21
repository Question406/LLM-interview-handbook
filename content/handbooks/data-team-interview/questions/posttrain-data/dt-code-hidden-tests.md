---
id: dt-code-hidden-tests
section: posttrain-data
order: 7
level: S
title: 代码数据：公开测过了就算正例吗，隐藏测和额外测干什么？
quick: "三套测试分三种用途：公开测试给模型当改代码的反馈，隐藏测试决定能否当正例和 RL 奖励，EvalPlus 或新竞赛题做独立评测。隐藏测试要固定哈希，改测试的轨迹要隔离；只过了公开样例或只是编译成功，都不能算正确解。"
companies:
  - apple
tags:
  - Apple
  - Coding
  - Verifier
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "EvalPlus: HumanEval+ / MBPP+"
    url: https://arxiv.org/abs/2305.01210
    type: primary
  - title: LiveCodeBench
    url: https://arxiv.org/abs/2403.07974
    type: primary
  - title: "RLEF: Grounding Code LLMs in Execution Feedback with Reinforcement Learning"
    url: https://arxiv.org/abs/2410.02089
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

公开测试用来给模型提供修复反馈；一条解能不能算成功正例，要看固定的隐藏测试。原因很简单：模型可能写出只通过公开样例、却不满足整体要求的解。

## 为什么公开测试不够

很多「过了官方测试」的解其实是过拟合了样例。EvalPlus 给 HumanEval 和 MBPP 补了大量自动测试后，pass@$1$ 会掉一截。如果单测和解由同一个教师合成，公开测试就等于教师自己给自己打分。LiveCodeBench 用新题来挡题面泄漏。RLEF 把执行反馈放进对话，但奖励仍然看私有测试，见 `dt-rlef-split`。

## 三套测试，三种用途

| 套 | 模型能不能看见 | 用途 |
| --- | --- | --- |
| 样例 / 公开测 | 可以进 观测结果（observation） | 训练时改代码的反馈 |
| 隐藏测 | 训练看不到正文 | 是否当 监督微调（SFT） 正例、强化学习（RL） 奖励 |
| 评测加严测（EvalPlus、新竞赛） | 永远不见 | 门禁 |

Llama 3 的报告写过，改代码或者改测试都能让门禁通过。所以隐藏测试要冻结哈希，改过测试的轨迹要隔离，见 `dt-code-exec-synth`。

隐藏测试至少要换一个生成种子，或者由人来写。如果它和公开测试同分布，隐藏测试也就失效了。

## 正例门

进入 SFT 的成功轨迹应通过全部隐藏测试。只通过公开测试的轨迹，可以当修复过程的示范，或者直接丢弃。RL 奖励看隐藏测试的通过率，编译成功不等于功能正确。

stderr 可以作为对话里的工具反馈，但不计入模型生成部分的交叉熵损失（CE）。

## 追问

- **没有隐藏测试的开源题怎么办？** 按 EvalPlus 的思路自己扩测试；扩不了就不当正例，只当种子。
- **隐藏测试泄漏进权重怎么办？** 和题面泄漏一样去查，测例字符串也要进污染表。
- **竞赛题能给部分分吗？** 按测试点给稠密的奖励分数（reward）可以。SFT 仍然建议全过才留，避免学到半对的解。

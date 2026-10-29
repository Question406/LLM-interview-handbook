---
id: dt-code-hidden-tests
section: posttrain-data
order: 7
level: S
title: 代码数据：公开测过了就算正例吗，隐藏测和额外测干什么？
quick: >-
  三套测试三种用途：公开测试给模型当改代码的反馈，hidden tests 决定能不能当正例和 RL 奖励，EvalPlus
  或新竞赛题做独立评测。hidden tests 要固定哈希，改过测试的 trajectories 要隔离；只过了公开样例或只是编译成功，都不算正确解。
companies:
  - apple
tags:
  - Apple
  - Coding
  - Verifier
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: 'EvalPlus: HumanEval+ / MBPP+'
    url: 'https://arxiv.org/abs/2305.01210'
    type: primary
  - title: LiveCodeBench
    url: 'https://arxiv.org/abs/2403.07974'
    type: primary
  - title: >-
      RLEF: Grounding Code LLMs in Execution Feedback with Reinforcement
      Learning
    url: 'https://arxiv.org/abs/2410.02089'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

公开测试用来给模型提供修复反馈，一条解能不能算成功正例，要看固定的 hidden tests。模型可能写出只通过公开样例、却不满足整体要求的解。

比如一道题给了三个样例，模型写了个只对这三个输入返回正确结果的特判，公开测试全过。EvalPlus 给 HumanEval 和 MBPP 补了大量自动测试后，pass@$1$ 会掉一截，说明很多「过了官方测试」的解其实是 overfitting 了样例。如果单测和解由同一个 teacher 合成，公开测试就等于 teacher 自己给自己打分。

所以我会分三套测试，各管一件事：

| 套 | 模型能不能看见 | 用途 |
| --- | --- | --- |
| 样例 / 公开测 | 可以进 observation | 训练时改代码的反馈 |
| 隐藏测 | 训练看不到正文 | 是否当 SFT 正例、RL 奖励 |
| 评测加严测（EvalPlus、新竞赛） | 永远不见 | evaluation gate |

Llama 3 的报告写过，改代码或者改测试都能让 evaluation gate 通过。所以 hidden tests 要冻结哈希，改过测试的 trajectories 要隔离（见 `dt-code-exec-synth`）。hidden tests 至少要换一个生成 seed，或者由人来写；它要是和公开测试同分布，也就失效了。

positive-example criteria 就按 hidden tests 来。进 SFT 的成功 trajectories 要通过全部 hidden tests，只过了公开测试的 trajectories，可以当修复过程的示范，或者直接丢掉。RL 奖励看 hidden tests 的通过率，编译成功不等于功能正确。stderr 可以作为对话里的工具反馈，但不计入模型生成部分的 cross-entropy 损失（CE）。

## 追问

**执行反馈放进对话以后，奖励看什么？**
还是看私有测试。RLEF 把执行反馈放进对话，奖励仍然由私有测试决定，见 `dt-rlef-split`。

**没有 hidden tests 的开源题怎么办？**
按 EvalPlus 的思路自己扩测试；扩不了就不当正例，只当 seed。

**hidden tests leakage 进权重怎么办？**
和题面 leakage 一样去查，测例字符串也要进 contamination 表。题面 leakage 那头，LiveCodeBench 用新题来挡。

**竞赛题能给部分分吗？**
按测试点给稠密的奖励分数（reward）可以。SFT 还是建议全过才留，免得学到半对的解。

---
id: dt-code-hidden-tests
section: posttrain-data
order: 7
level: S
title: 代码数据：公开测过了就算正例吗，隐藏测和额外测干什么？
quick: "三套测试三种用途：公开测试给模型当改代码的反馈，隐藏测试决定能不能当正例和 RL 奖励，EvalPlus 或新竞赛题做独立评测。隐藏测试要固定哈希，改过测试的轨迹要隔离；只过了公开样例或只是编译成功，都不算正确解。"
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

公开测试用来给模型提供修复反馈，一条解能不能算成功正例，要看固定的隐藏测试。模型可能写出只通过公开样例、却不满足整体要求的解。

比如一道题给了三个样例，模型写了个只对这三个输入返回正确结果的特判，公开测试全过。EvalPlus 给 HumanEval 和 MBPP 补了大量自动测试后，pass@$1$ 会掉一截，说明很多「过了官方测试」的解其实是过拟合了样例。如果单测和解由同一个教师合成，公开测试就等于教师自己给自己打分。

所以我会分三套测试，各管一件事：

| 套 | 模型能不能看见 | 用途 |
| --- | --- | --- |
| 样例 / 公开测 | 可以进观测结果（observation） | 训练时改代码的反馈 |
| 隐藏测 | 训练看不到正文 | 是否当监督微调（SFT）正例、强化学习（RL）奖励 |
| 评测加严测（EvalPlus、新竞赛） | 永远不见 | 门禁 |

Llama 3 的报告写过，改代码或者改测试都能让门禁通过。所以隐藏测试要冻结哈希，改过测试的轨迹要隔离（见 `dt-code-exec-synth`）。隐藏测试至少要换一个生成种子，或者由人来写；它要是和公开测试同分布，也就失效了。

正例门就按隐藏测试来。进 SFT 的成功轨迹要通过全部隐藏测试，只过了公开测试的轨迹，可以当修复过程的示范，或者直接丢掉。RL 奖励看隐藏测试的通过率，编译成功不等于功能正确。stderr 可以作为对话里的工具反馈，但不计入模型生成部分的交叉熵损失（CE）。

## 追问

**执行反馈放进对话以后，奖励看什么？**
还是看私有测试。RLEF 把执行反馈放进对话，奖励仍然由私有测试决定，见 `dt-rlef-split`。

**没有隐藏测试的开源题怎么办？**
按 EvalPlus 的思路自己扩测试；扩不了就不当正例，只当种子。

**隐藏测试泄漏进权重怎么办？**
和题面泄漏一样去查，测例字符串也要进污染表。题面泄漏那头，LiveCodeBench 用新题来挡。

**竞赛题能给部分分吗？**
按测试点给稠密的奖励分数（reward）可以。SFT 还是建议全过才留，免得学到半对的解。

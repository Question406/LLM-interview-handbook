---
id: dt-code-hidden-tests
section: posttrain-data
order: 7
level: S
title: 代码数据：公开测过了就算正例吗，隐藏测和额外测干什么？
quick: "公开测试用于让模型修改代码，隐藏测试决定是否成功和如何给 RL 奖励，EvalPlus 或新竞赛题用于独立评测。固定测试哈希，隔离修改测试的轨迹；只通过公开样例或编译成功，还不能作为完整正确解。"
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

公开测试用于提供修复反馈；是否作为成功正例，还要看固定的隐藏测试。模型可能只写出通过公开样例、却不符合整体要求的解。

不这么选的理由：很多「过了官方测」的解是过拟合样例。EvalPlus 给 HumanEval / MBPP 加大量自动测试，pass@$1$ 会掉一截。合成单测和合成解同一教师，公开测等于教师自嗨。LiveCodeBench 用新题挡题面泄漏。RLEF 把执行反馈放进对话，奖励仍看私有测，见 `dt-rlef-split`。

苹果：许可仓库或合成环境里的隐藏测。用户会话默认不进基础模型，也不能拿用户「看起来跑通了」当正例。

## 三套测试，三种用途

| 套 | 模型能不能看见 | 用途 |
| --- | --- | --- |
| 样例 / 公开测 | 可以进 观测结果（observation） | 训练时改代码的反馈 |
| 隐藏测 | 训练看不到正文 | 是否当 监督微调（SFT） 正例、强化学习（RL） 奖励 |
| 评测加严测（EvalPlus、新竞赛） | 永远不见 | 门禁 |

Llama 3 写过改代码或改测试都能过门。所以隐藏测要冻哈希，改测试的轨迹隔离，见 `dt-code-exec-synth`。

隐藏测至少换生成种子，或人写。两边同分布，隐藏测也废。

## 正例门

进入 SFT 的成功轨迹应通过全部隐藏测试。只通过公开测试的轨迹，可当作修复过程示范或丢弃。RL 奖励看隐藏测试通过率，编译成功不等于功能正确。

stderr 可以作为对话中的工具反馈，但不计入模型生成的交叉熵损失（CE）。

## 追问

- **没有隐藏测的开源题怎么办？** 自己用 EvalPlus 思路扩测，或不当正例，只当种子。
- **隐藏测泄漏进权重？** 和题面泄漏一样查。测例字符串也要进污染表。
- **竞赛题部分分？** 按测试点给 dense 奖励分数（reward） 可以。SFT 仍建议全过再留，避免学半对解。

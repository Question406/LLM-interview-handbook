---
id: dt-rlef-split
section: labs
order: 29
level: A
title: RLEF：执行反馈进对话，奖励却看私有测试，数据怎么切？
quick: >-
  每题准备两套测试：公开测试的结果可以作为 observation
  返回给模型，最终奖励只由不展示的私有测试决定。两套混用，模型会背公开测试、改代码迎合样例。两套测试分别记录哈希，stderr 不进
  cross-entropy 训练目标，公开测试全过但私有测试失败，奖励仍为 0。
companies:
  - apple
tags:
  - Meta
  - Coding
  - RLVR
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: >-
      RLEF: Grounding Code LLMs in Execution Feedback with Reinforcement
      Learning
    url: 'https://arxiv.org/abs/2410.02089'
    type: primary
  - title: The Llama 3 Herd of Models
    url: 'https://arxiv.org/abs/2407.21783'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

数据按「给模型看的」和「给评分程序看的」切成两套测试。公开测试的结果可以当 observation 返回给模型，让它读反馈改代码；私有测试只交给评分程序，不写进 prompt，最终奖励只看它。

比如一道题的公开样例只有三个小输入，模型可能直接对这三个输入写特判，公开测试全绿；私有测试里有空输入、大数这些 edge cases，一跑就挂。两套要是同一套，模型会背下公开测试，或者改测试去迎合，学到的是骗过样例。所以中途公开全绿、私有却失败的 trajectories，奖励是 0。

这正是 Gehring 等人（Meta，CodeContests）的设计：模型先交一版代码，公开测试失败就把用例结果和报错拼回对话再改；公开测试全过或到达轮次上限，才用私有测试打 0/1 奖励，用 PPO 更新。这样奖励的是读懂反馈后改对的 trajectories，多采几次碰巧做对在这里得不到额外奖励。

切数据时，公开测试偏重样例，私有测试覆盖 boundary conditions，各自记录哈希。训练 loss 只计算助手生成的下一版代码，不算编译器报错；stderr 留在上下文里，不当 SFT 正文算 cross-entropy 损失（CE），见 `dt-packed-sft-code`。奖励由私有测试决定 0/1，到了轮次上限仍未提交有效代码（交白卷）也是 0。靠修改测试本身通过 checks 的 trajectories 直接丢掉，见 `dt-code-exec-synth`。

## 追问

**RLEF 和 RLVR 有什么区别？**
RLVR 通常一题一轮，只看终局对错；RLEF 把中间的失败变成了合法的 observation。基于 verifiable reward 的 RL（RLVR）的数据怎么做，见 `dt-rlvr-data`。

**公开测试和私有测试能用同一个生成器造吗？**
最好不要。同一个生成器切出来的两套，公开测试也会 leakage 私有测试，所以题面演化和 assertion 要来自不同来源。

**没有私有测试怎么办？**
至少留一小批人写的冻结测试当 evaluation gate，assertion 要避开对话里出现过的内容。

**工具 / agent 任务也能这么切吗？**
能，结构一样：环境返回的结果给模型看、让它改，奖励看状态核验，模型自己说「我改好了」不算数。AFM 2025 报告的工具树就是这样做的，题目用许可题或验证过的合成。

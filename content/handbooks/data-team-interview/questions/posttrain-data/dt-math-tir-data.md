---
id: dt-math-tir-data
section: posttrain-data
order: 3
level: S
title: 数学后训练：纯 CoT、PAL 程序、还是 ToRA 那种边想边跑代码？
quick: "需要计算的步骤交给解释器：PAL / PoT 把题意转成程序，ToRA / OpenMathInstruct 让自然语言推理和代码调用交替。代码要在沙箱中真实执行，最终答案再与金标核对；解释器输出作为输入，不计入 CE。"
companies:
  - apple
tags:
  - Apple
  - Math
  - Tool Use
  - Synthetic Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "PAL: Program-aided Language Models"
    url: https://arxiv.org/abs/2211.10435
    type: primary
  - title: Program of Thoughts Prompting
    url: https://arxiv.org/abs/2211.12588
    type: primary
  - title: ToRA
    url: https://arxiv.org/abs/2309.17452
    type: primary
  - title: OpenMathInstruct-1
    url: https://arxiv.org/abs/2402.10176
    type: primary
---

需要计算的步骤可以采用 TIR：自然语言分析题意，代码交给解释器执行，再读取输出继续作答。没有可执行沙箱，就不应生成这类训练轨迹。

纯 CoT 让模型自己完成算术，容易出现错误步骤，见 `dt-math-verifier-code`。所有题都改用 PAL 也不合适，几何证明等任务未必适合转成程序。PAL / PoT 把题编译成程序，数字交给 Python。ToRA 把理由和工具调用交错。NVIDIA 的 OpenMathInstruct-1 用 Mixtral 造了 180 万条带代码解释器的轨迹，选解时偏代码。

苹果：能验证先验证。用户日志不进基础模型。教师版本和种子是否碰过门禁要记。

## 数据长什么样

一轮合法 TIR：

1. 自然语言分析（可进 交叉熵损失（CE））。
2. 代码调用（进 CE）。
3. 解释器 stdout / stderr（mask，和工具 观测结果（observation） 同一条纪律，见 `dt-packed-sft-code`）。
4. 根据输出继续想或给出 `\boxed{}`。

门：最终量对金标，并且代码真的跑过。只抄了一个 `print(标准答案)` 的程序要扔掉。OpenMathInstruct 写了用参考解答时要遮住，避免模型直接泄露金标进代码。

沙箱：超时、禁网络、限 CPU。这些限制用于确保执行安全、结果可验证。跑不了的轨迹不进 监督微调（SFT）。

## 和纯 CoT 怎么配

心算、不等式、证明思路仍要自然语言。数值计算、解方程、求和走 TIR。这是在数学任务中落实 AFM「能验证先验证」的一种方法。

## 追问

- **执行对了但程序不可读？** 当 强化学习（RL） 正例可以，SFT 主集要可读。抽查看是否在背金标。
- **和 Lean 谁先？** 竞赛应用题先 TIR。需要证明检查再 Lean，见 `dt-math-lean-prover`。
- **教师用 GPT-4 造 TIR？** OpenMathInstruct 刻意用可许可的 Mixtral。苹果这轮还要记教师版本和种子是否碰过门禁。

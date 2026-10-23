---
id: dt-math-tir-data
section: posttrain-data
order: 3
level: S
title: 数学后训练：纯 CoT、PAL 程序、还是 ToRA 那种边想边跑代码？
quick: "按任务分，需要计算的步骤用 TIR 交给解释器，心算、不等式、证明思路仍用自然语言。PAL / PoT 把题意转成程序，ToRA / OpenMathInstruct 让推理和代码调用交替。代码必须在沙箱里真实执行，最终答案再对金标；解释器输出作为输入，不计入 CE。"
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

不选一种，按任务分。需要算数的步骤用 TIR：先用自然语言分析题意，把计算写成代码交给解释器执行，读到输出再继续作答。心算、不等式、证明思路仍然用自然语言。前提是有可执行的沙箱，没有沙箱就不该生成这类训练轨迹。

比如一道题前面的建模很简单，后面要做一长串多位数运算。纯 CoT 让模型自己算，很容易在某一步算错，见 `dt-math-verifier-code`；把这一步写成几行 Python 交给解释器，就不会错。反过来，所有题都改成 PAL 也有问题，几何证明这类任务未必能转成程序。

几种公开做法的区别在于代码和推理怎么组合。PAL / PoT 把整道题编译成程序，数字全交给 Python。ToRA 让推理和工具调用交错进行。NVIDIA 的 OpenMathInstruct-1 用 Mixtral 造了 180 万条带代码解释器的轨迹，挑选解答时偏向代码解。

一轮 TIR 先是自然语言分析，再是代码调用，这两段都进交叉熵损失（CE）。解释器的 stdout / stderr 要 mask 掉，和工具观测结果（observation）是同一条纪律，见 `dt-packed-sft-code`。最后根据输出继续推理，或给出 `\boxed{}`。

轨迹能不能留，看两条：最终答案和金标一致，并且代码确实跑过。只写了一个 `print(标准答案)` 的程序要扔掉。OpenMathInstruct 也写了，用参考解答引导生成时要把它遮住，免得模型直接把金标写进代码。跑不了的轨迹不进监督微调（SFT），教师版本、种子有没有碰过门禁，都要记下来。

## 追问

**沙箱要怎么设？**
设超时、禁网络、限 CPU。这既保证执行安全，也保证结果可验证。

**执行结果对了，但程序不可读？**
当强化学习（RL）正例可以，SFT 主集要可读。抽查时看它是不是在背金标。

**和 Lean 谁先上？**
竞赛应用题先上 TIR，需要证明检查的再上 Lean，见 `dt-math-lean-prover`。

**教师能用 GPT-4 造 TIR 吗？**
要先看许可。OpenMathInstruct 刻意用了许可更宽松的 Mixtral。不管用哪个教师，版本都要记录。

相关：`dt-math-verifier-code`、`dt-packed-sft-code`、`dt-math-lean-prover`

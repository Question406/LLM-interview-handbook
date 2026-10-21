---
id: dt-self-improve
section: senior
order: 2
level: A
title: Director：模型怎么给自己造训练数据，边界在哪？
quick: "可以，但判对错的门要放在模型外面：当前模型生成多个候选，由独立的验证器筛出正确结果，再用于训练下一版。STaR、ReST 和拒绝采样都是这个思路。边界有三条：同一个模型默认不同时出答案和定标签，限制回流代数，并保留真实来源的数据做对照。"
companies:
  - apple
tags:
  - Apple
  - Self-improvement
  - Synthetic Data
  - Model Collapse
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "STaR: Bootstrapping Reasoning With Reasoning"
    url: https://arxiv.org/abs/2203.14465
    type: primary
  - title: "Reinforced Self-Training (ReST)"
    url: https://arxiv.org/abs/2308.08998
    type: primary
  - title: Self-Rewarding Language Models
    url: https://arxiv.org/abs/2401.10020
    type: primary
  - title: The Curse of Recursion / Model Collapse
    url: https://arxiv.org/abs/2305.17493
    type: primary
  - title: Applebot model training and individual privacy rights
    url: https://support.apple.com/en-us/120320
    type: primary
---

模型可以给自己造训练数据，但正确与否的标准不能由它自己定。做法是让当前模型生成候选，用独立的检查筛选，再把通过的样本用于训练下一版模型。模型可以修改候选数据，标签定义仍然属于验证器、人工和产品契约。

岗位 guideline 要求能讨论 model self-improvement / self-iteration。回答时要讲清三件事：谁生成，谁把门，回流几代之后要停。没有外部的门，模型的错误会跟着正确样本一起进入下一轮。

## 能工作的回路

讲每种回路时，都要说清生成器是谁、门是谁。

STaR：对有标准答案的题采样，做对的轨迹留下做监督微调（SFT），做错的可以给提示再试。能力的提升来自强化那些模型偶尔能碰到的正确推理链。

ReST：多轮执行采样、用奖励过滤、离线强化学习或 SFT。奖励来自执行器时，这套流程是稳的；奖励来自模型自己的奖励模型（RM）时，要当作研究，不当默认的生产做法。

拒绝采样：同一道题采 $k$ 条，用验证器（verifier）留下 1 条。实现简单，但负例被扔掉了，信息量不如组内相对优势。

过程监督：AFM 的工具平台上，参考模型先跑，人和环境当门，成功的主要执行路径进入 SFT。生成器可以是自己或教师，但门不是自己。

「模型生成并 refinement」可以发生在题面（evol）、答案（重采样）或过程（回滚改一步）三个层面，每一层都要说清门是谁。

## 不能当默认的回路

Self-Rewarding 让模型既写答案又当评判。论文表明这样可以提升，但现场要主动讲风险：评判器和生成器共享盲点，风格会收敛到模型自己爱看的样子。生产中最多用它给候选排序，门禁仍要靠人和真实来源。

Model collapse（Shumailov et al.）说的是：用自己的输出当下一轮的「真实数据」，分布尾部会消失，错误会被当成事实。检测时看生成代数、错误指纹，以及和新鲜人类数据对照的散度，合成条数说明不了什么。Collapse 主要出现在多代、无验证的回流里；单代、强教师、硬验证的蒸馏一般不会出现。

还有一个前提：如果当前模型在这类题上 pass@$k\approx 0$，就几乎没有成功示范可用于自我改进。这时先降难度、换教师，或者改走人写数据，不要加大 $k$ 空转。

## 追问

- **教师和学生能是同一个 checkpoint 吗？** 做一代拒绝采样可以，但门必须外置。多代迭代时，要把教师固定在更强或更新、验证过的版本上，并注入新鲜的真实来源数据。
- **这和 mid-training 的验证合成是不是一回事？** 同源。Mid 通常是更强的教师加验证；自迭代是用当前策略当生成器。门相同，生成器不同。
- **要不要把失败轨迹也喂回去？** 当负例或恢复示范可以，当下一轮的「正确答案」不行。

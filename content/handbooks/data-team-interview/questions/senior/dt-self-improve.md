---
id: dt-self-improve
section: senior
order: 2
level: A
title: Director：模型怎么给自己造训练数据，边界在哪？
quick: "可以，但判对错的门要放在模型外面：当前模型生成候选，独立的验证器筛出对的，再拿去训下一版，STaR、ReST 和拒绝采样都是这个思路。边界有三条：同一个模型默认不同时出答案和定标签，回流代数要有上限，还要留真实来源的数据做对照。"
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

模型可以给自己造训练数据，但对错的标准不能由它自己定。当前模型生成候选，独立的检查筛一遍，通过的样本拿去训下一版。模型可以修改候选，标签定义还是归验证器、人工和产品契约。

举个例子，数学题有标准答案，让模型对每道题采样几条推理，做对的轨迹留下做 SFT，做错的给点提示再试，这就是 STaR。能力的提升来自强化那些模型偶尔能碰到的正确推理链，门是标准答案，模型自己说了不算。岗位 guideline 要求能讨论 model self-improvement / self-iteration，我会把每种回路都讲清三件事：谁生成，谁把门，回流几代之后要停。没有外部的门，模型的错误会跟着正确样本一起进入下一轮。

别的回路也按这个看。AFM 工具平台上的过程监督，是参考模型先跑，人和环境当门，成功的主要执行路径进入 SFT，生成器可以是自己或教师，门不是自己。「模型生成并 refinement」可以发生在题面（evol）、答案（重采样）或过程（回滚改一步）三个层面，每一层都要说清门是谁。

边界在回流。Model collapse（Shumailov et al.）说的是，拿自己的输出当下一轮的「真实数据」，分布尾部会消失，错误会被当成事实。它主要出现在多代、无验证的回流里，单代、强教师、硬验证的蒸馏一般不会。检测时看生成代数、错误指纹，以及和新鲜人类数据对照的散度，合成了多少条说明不了什么。

还有一个前提：当前模型在这类题上 pass@$k\approx 0$ 的话，就几乎没有成功示范可用于自我改进。这时先降难度、换教师，或者改走人写数据，别加大 $k$ 空转。

## 追问

**ReST 和拒绝采样有什么不一样？**
ReST 是多轮执行采样、用奖励过滤、再做离线强化学习或 SFT。奖励来自执行器时这套流程是稳的，来自模型自己的奖励模型（RM）时要当研究看，不当默认的生产做法。拒绝采样是同一道题采 $k$ 条、用验证器（verifier）留下 1 条，实现简单，但负例被扔掉了，信息量不如组内相对优势。

**让模型自己当评判行不行？**
不能当默认做法。Self-Rewarding 让模型既写答案又当评判，论文表明这样可以提升，但评判器和生成器共享盲点，风格会收敛到模型自己爱看的样子。生产中最多用它给候选排序，门禁还是靠人和真实来源。

**教师和学生能是同一个 checkpoint 吗？**
做一代拒绝采样可以，但门必须外置。多代迭代时，要把教师固定在更强或更新、验证过的版本上，并注入新鲜的真实来源数据。

**这和 mid-training 的验证合成是不是一回事？**
同源。Mid 通常是更强的教师加验证，自迭代是用当前策略当生成器，门相同，生成器不同。

**要不要把失败轨迹也喂回去？**
当负例或恢复示范可以，当下一轮的「正确答案」不行。

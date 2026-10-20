---
id: dt-self-improve
section: senior
order: 2
level: A
title: Director：模型怎么给自己造训练数据，边界在哪？
quick: "模型可以生成多个候选，用独立验证器筛出正确结果，再用于训练。STaR、ReST 和拒绝采样都采用相关思路。要限制回流代数、保留真实来源对照；不能默认让同一模型既出答案又定义正确标签，也不能把用户点击直接当自我改进数据。"
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

让当前模型生成候选，用独立检查筛选，再把通过的样本用于训练下一版模型。模型可以修改候选数据，但正确与否的标准仍应由验证器、人工和产品要求决定。

不这么选的理由：guideline 要你能讨论 model self-improvement / self-iteration。把「模型生成再训练」说成无条件越训越强，或把用户点击当自我改进，通道都不成立。苹果还多一条：用户交互默认不能当自我改进语料。

## 能工作的回路

STaR。对有标准答案的题采样；做对的轨迹留下做 监督微调（SFT），做错的可以给提示再试。能力涨在「模型偶尔能碰到的正确链」被强化。

ReST。多轮：采样、用奖励过滤、离线强化学习或 SFT。奖励若是执行器，这一套稳；奖励若是自己的 奖励模型（RM），要当研究，不当默认生产。

拒绝采样。同题 $k$ 条，验证器（verifier） 留 1。实现简单，负例被扔掉，信息量不如组内相对优势。

过程监督。AFM 工具平台：参考模型先跑，人 + 环境当门，成功的主要执行路径进 SFT。生成器是自己或教师，门不是自己。

「模型生成并 refinement」可以发生在题面（evol）、答案（重采样）或过程（回滚改一步）。每一层都要说门是谁。

## 不能当默认的回路

Self-Rewarding：模型既写答案又写评判。论文证明可以涨，现场要主动讲风险：评判器和生成器共享盲点，风格会收敛到自己爱看的样子。生产里最多当候选排序，门禁仍要人和真源。

Model collapse（Shumailov et al.）：用自己的输出当下一轮的「真实数据」，尾部分布消失，错误被当成事实。检测看代数、错误指纹、和新鲜人类对照的散度，不是看合成条数。单代、强教师、硬验证的蒸馏通常不是 collapse；多代无验证回流才是。

如果当前模型在这类题上 pass@$k\approx 0$，就几乎没有成功示范可用于自我改进。先降难度、换教师，或走人写，不要加大 $k$ 空转。

## 苹果约束下的自我改进

用户私有数据和交互默认不训基础模型。所以「线上失败 → 原样进下一轮 SFT」这条业界常见飞轮，在这里对基础模型不成立。还能做的自我改进：

- 许可 / 公开 / 合成域里的 STaR / 拒绝采样。
- 内部标注平台上的参考模型迭代（AFM 工具树）。
- 端上 adapter 用的是用户选中的、留在设备上的信号，不回灌全球 FM。
- 聚合统计若离开设备，要走差分隐私，见 `dt-privacy-feedback`。

标签定义属于 verifier、人和产品契约。

## 追问

- **教师和学生是同一个 checkpoint 行吗？** 可以做一代拒绝采样，门必须外置。多代要把教师钉在更强或更新的验证过版本，并注入新鲜真源。
- **和 mid-training 的验证合成是不是一回事？** 同源。Mid 常是更强教师 + 验证；自迭代是当前策略当生成器。门相同，生成器不同。
- **要不要把失败轨迹也喂回去？** 当负例或恢复示范可以，当下一轮的「正确答案」不行。

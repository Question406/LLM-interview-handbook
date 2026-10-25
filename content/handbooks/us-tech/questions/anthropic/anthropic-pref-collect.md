---
id: anthropic-pref-collect
section: anthropic
order: 24
level: S
title: Anthropic：偏好数据怎么采？双盲、平局、多轴 HH
quick: "我会隐藏模型名和采样温度、随机左右顺序，并提供「一样好、一样差、无法比较」。Helpful、harmless、honest 的标准要分开写，有害冲突明确伤害优先；再用重复标注和平局率检查一致性，避免让标注员自行把多个目标混成一个偏好。"
tags:
  - Anthropic
  - Preference
  - RLHF
  - Data
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Training a Helpful and Harmless Assistant with RLHF
    url: https://arxiv.org/abs/2204.05862
    type: primary
  - title: Constitutional AI — Harmlessness from AI Feedback
    url: https://arxiv.org/abs/2212.08073
    type: primary
  - title: Claude's Constitution
    url: https://www.anthropic.com/news/claudes-constitution
    type: primary
---

我会先把比较标准分开，再设计隐藏模型身份、随机左右、允许平局的界面。例如两条回复都答对、只有文风不同，标注员应该能选「无法比较」。HH-RLHF 分别采 helpful 和 harmless，CAI 后来让模型按条款标 harmlessness；Bradley-Terry 如何使用这些数据见 `anthropic-pref-bt`。

## 双盲和界面

标注员每次看一个 prompt 和两条回复，我会把下面这些规则写进采集协议：

- 随机左右。人偏爱左边、偏爱先出现的。位置要进随机化，事后做位置偏差切片。CAI 的 AI 评委同样要左右对调，胜率不对称就说明评委在看位置。
- 不露模型名、不露采样温度。「GPT 总是更好」会污染。
- 同一次只问一个主问题。Helpful 任务写：更有帮助、更清楚、更不啰嗦、更诚实。Harmless / 红队任务写：哪条更无害（或论文里红队选「更有害」再在训练时翻转，面试要说清标签方向，搞反则 PM 会学坏）。
- 多轮对话。HH 是对话里逐步展开的。每一步两条续写，上下文包含已选轨迹，否则偏好对不上真实部署。

长度偏差：人爱长文。配对时长度分层，或在说明里写「更长不等于更好」。否则 PM 会奖励啰嗦，强化学习（RL） 再放大。

## 用平局和一致率检查数据质量

两条都拒得一样干净、或两条都有害、或两条都答对只是文风不同：提供「一样好 / 一样差 / 无法比较」。不要产品经理说必须点一个。硬选把噪声写进 BT，见 `anthropic-pref-bt` 的平局通道。

平局率本身是仪表盘：helpful 普通任务平局应较低；harmless 对常更高。平局突然消失，多半是界面逼选或标注员赶工。丢掉平局最干净但浪费；样本贵时用软标签 0.5。

不同目标分别采集。Askell 的 HHH 有三轴，Bai 的工作主要使用下面两套池，诚实几乎没有独立数据集：

1. Helpful。尽量完成用户意图；诚实条款写进说明（别编来源），但主任务不是安全。
2. Harmless / 红队。标注员主动诱导有害行为。冲突样本在这里：伤害优先于完成任务，不是 50/50。

如果让同一个人先打「有用 4 分、安全 2 分」再选赢家，每个人心里的权重会不同，标签很难比较。我会分轴打分或分轴对比，到训练时再决定权重，见 `anthropic-hh-rlhf`。诚实单独采更贵，但 constitution 把不说白谎、校准不确定抬得很高；至少要有「承认不知道」vs「编一个自信答案」的对比，见 `anthropic-eval-honesty`。

红队的一致率通常低于摘要偏好。重复标一小部分，报 disagreement；丢掉永远点左边、标得飞快的人。循环偏好 $A \succ B \succ C \succ A$ 说明多轴或噪声，一个标量 $r$ 装不下。标注员要黄金集定期回标，漂移就停工复训。红队有心理负担，协议里要写退出通道，不要靠加班堆 harmless 量。

到了 CAI，人负责写条款、抽查失败模式，对比标签可以交给模型。评委也要允许「无法决定」，也要左右对调。人没退出，是从高带宽标注退到原则和审计，见 `anthropic-rlaif`。

## 追问

**为什么红队选「更有害」？**
论文设定是攻击者视角，训练时再翻成「更无害为 chosen」。方向必须在数据卡上写死。

**能用模型自标完全替代人吗？**
Harmlessness 可以走 RLAIF；helpful 和诚实的细风格仍常靠人。评委模型和被训模型要隔离版本。

**多模型比较怎么双盲？**
瑞士轮或随机配对，隐藏名字，定期用黄金集校准标注员。

**和 直接偏好优化（DPO） 还要不要这套协议？**
要。换损失不修复位置偏差和轴冲突。垃圾对比进 DPO 一样坏。

## 相关题

- [[anthropic-hh-rlhf]]：专讲 helpful 和 harmless 冲突时标哪个、训练时怎么加权，和这里「多轴分开采」一节高度重叠。
- [[anthropic-pref-bt]]：采回来的平局和噪声标签进 BT 偏好模型时怎么处理。
- [[align-llm-judge]]：用模型代替人做对比时同样有位置偏差，交换顺序和这里的随机左右是一个思路。
- [[align-cai]]：CAI 把人从逐条标偏好挪到写原则和抽查，是这套人工协议的替代方案。

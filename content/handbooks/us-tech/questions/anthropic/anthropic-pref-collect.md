---
id: anthropic-pref-collect
section: anthropic
order: 24
level: S
title: Anthropic：偏好数据怎么采？双盲、平局、多轴 HH
quick: >-
  对比界面随机左右、不露模型名，避免位置偏好。提供平局，不要逼人选。Helpful / harmless / honest
  分开采、分开写说明；冲突时伤害优先，但不要让同一个人脑内加权。红队那轴往往更吵，要测一致率。
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

HH-RLHF 把助手拆成 helpful 和 harmless 两套对比数据；CAI 后来把 harmlessness 的对比交给模型按条款标。对齐岗会问采集协议，而不只是 Bradley-Terry 公式（公式见 `anthropic-pref-bt`）。Bai 等人写得很清楚：两轴分开采，crowdworker 各自理解条款。诚实几乎没有独立数据集。面试讲协议：双盲、平局、多轴。

## 双盲和界面

标注员一次看一个 prompt、两条回复。我会坚持：

- 随机左右。人偏爱左边、偏爱先出现的。位置要进随机化，事后做位置偏差切片。CAI 的 AI 评委同样要左右对调，胜率不对称就说明评委在看位置。
- 不露模型名、不露采样温度。「GPT 总是更好」会污染。
- 同一次只问一个主问题。Helpful 任务写：更有帮助、更清楚、更不啰嗦、更诚实。Harmless / 红队任务写：哪条更无害（或论文里红队选「更有害」再在训练时翻转——面试要说清标签方向，搞反则 PM 会学坏）。
- 多轮对话。HH 是对话里逐步展开的。每一步两条续写，上下文包含已选轨迹，否则偏好对不上真实部署。

长度偏差：人爱长文。配对时长度分层，或在说明里写「更长不等于更好」。否则 PM 会奖励啰嗦，RL 再放大。

## 平局不是失败，是信号

两条都拒得一样干净、或两条都有害、或两条都答对只是文风不同：提供「一样好 / 一样差 / 无法比较」。不要产品经理说必须点一个。硬选把噪声写进 BT，见 `anthropic-pref-bt` 的平局通道。

平局率本身是仪表盘：helpful 普通任务平局应较低；harmless 对常更高。平局突然消失，多半是界面逼选或标注员赶工。丢掉平局最干净但浪费；样本贵时用软标签 0.5。

## 多轴 HH，不要脑内加权

Askell 的 HHH 是三轴。Bai 的采集是两套池：

1. Helpful。尽量完成用户意图；诚实条款写进说明（别编来源），但主任务不是安全。
2. Harmless / 红队。标注员主动诱导有害行为。冲突样本在这里：伤害优先于完成任务，不是 50/50。

不要让同一个人在一条上同时打「有用 4 分、安全 2 分」再让他选赢家——那是把 Pareto 压成脑内超参，人与人不可比。更好：分轴打分或分轴对比，训练时再加权，见 `anthropic-hh-rlhf`。诚实单独采更贵，但 constitution 把不说白谎、校准不确定抬得很高；至少要有「承认不知道」vs「编一个自信答案」的对比，见 `anthropic-eval-honesty`。

一致率：红队低于摘要偏好。重复标一小部分，报 disagreement；丢掉永远点左边、标得飞快的人。循环偏好 $A \succ B \succ C \succ A$ 说明多轴或噪声，一个标量 $r$ 装不下。标注员要黄金集定期回标，漂移就停工复训。红队有心理负担，协议里要写退出通道，不要靠加班堆 harmless 量。

CAI：人写条款、抽查失败模式，对比可由模型做。评委也要允许「无法决定」，也要左右对调。人没退出，是从高带宽标注退到原则和审计，见 `anthropic-rlaif`。

## 追问

- **为什么红队选「更有害」？** 论文设定是攻击者视角，训练时再翻成「更无害为 chosen」。方向必须在数据卡上写死。
- **能用模型自标完全替代人吗？** Harmlessness 可以走 RLAIF；helpful 和诚实的细风格仍常靠人。评委模型和被训模型要隔离版本。
- **多模型比较怎么双盲？** 瑞士轮或随机配对，隐藏名字，定期用黄金集校准标注员。
- **和 DPO 还要不要这套协议？** 要。换损失不修复位置偏差和轴冲突。垃圾对比进 DPO 一样坏。

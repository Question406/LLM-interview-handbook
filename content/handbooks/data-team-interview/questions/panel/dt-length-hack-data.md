---
id: dt-length-hack-data
section: panel
order: 17
level: A
title: Panel：偏好和 RM 爱上长答案，数据侧怎么拆？
quick: "问题出在偏好数据里长回答总是赢，只调优化参数压不住。数据侧要构造信息相同、长度不同的回答对，协议写明同等忠实且完整时选短的；人评和 RM 结果按长度分层分析，BoN 候选中保留简短的 SFT 回答。平均长度增加不代表能力提高。"
companies:
  - apple
tags:
  - Apple
  - Length Bias
  - Preference
  - Reward Model
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Training language models to follow instructions with human feedback
    url: https://arxiv.org/abs/2203.02155
    type: primary
  - title: "Direct Preference Optimization"
    url: https://arxiv.org/abs/2305.18290
    type: primary
  - title: "AlpacaEval 2.0"
    url: https://arxiv.org/abs/2404.04475
    type: primary
---

平均回答长度增加，不能直接当成进步。我会在数据里造反例：同一输入配两个回答，信息量相近、长度明显不同，同等忠实且完整时选短的。只调 $\beta$ 压不住这个偏差。

## 为什么要从数据下手

如果训练对里长回答总是更好，奖励模型（RM）就会把长度学成质量信号。只在损失函数里加长度惩罚、不调整数据，这个信号还在，偏差仍可能存在。所以要数据和对齐方法一起处理。

## 怎么拆

先在协议里写明「同等忠实选短」。这类对进入 RM 或直接偏好优化（DPO），模型才学到长度本身不加分。

标注时按长度分层抽样，避免候选池里长的本来就多。一致率分析也要按长度切开：如果人只在「一长一短」的对上吵，说明协议没写清。按维度打分的人评，也比单一的「哪个更好」更难被长度带跑，AFM 的人评就是分维度的。

评测上用 AlpacaEval 一类的 length-controlled 变体，或按长度桶报 win-rate。摘要这类任务更应该奖励短而全的回答。

强化学习（RL）采样之后画一张散点图：横轴是长度，纵轴是 RM 分。如果大量样本长度和 RM 分都很高，金标质量却低，就说明 RM 可能在奖励长度。BoN 里强制保留几条监督微调（SFT）的短样本，防止策略完全偏离参考文风。

## 实践中的变化

长度惩罚会伤到推理链，数学题的过程长是必要的。所以要按任务区分：推理看对错，摘要看信息密度，全局罚长会误伤推理题。

## 追问

- **DPO 没有 RM，还会 hack 长度吗？** 会，只要偏好对里长的总是 chosen。问题在数据上。
- **教师示范普遍很长怎么办？** 把可学性和长度一起看，见 `dt-teacher-bias`。先精简冗长的示范，再做偏好训练。

---
id: dt-length-hack-data
section: panel
order: 17
level: A
title: Panel：偏好和 RM 爱上长答案，数据侧怎么拆？
quick: "构造信息相同、长度不同的回答对，明确标注同等忠实且完整时选简短的。人评与 RM 结果按长度分层分析，BoN 候选中保留简短的 SFT 回答。平均长度增加不代表能力提高，调整优化参数也解决不了偏好数据中的长度偏差。"
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

平均回答长度增加，不能直接当成进步。先为同一输入构造两个回答，让它们包含近似的信息，但长度明显不同；同等忠实且完整时选择短的。只调 $\beta$ 压不住这条。

只在损失函数里增加长度惩罚，却不调整数据，偏差仍可能存在。如果训练对中长回答总是更好，奖励模型（RM）就可能把长度学成质量信号。这需要数据和对齐方法一起处理。

## 先在数据里制造反例

人标协议写明：同等忠实选短。这类对进 RM / 直接偏好优化（DPO），模型才知道「长」不是特征。

标注时按长度分层抽样，避免池子里长的本来就多。一致率分析要切长度：若人只在「一长一短」上吵，协议没写清。AFM 人评分维度，比单一「更好」难被长度带跑。

评测：AlpacaEval 一类 length-controlled 变体、或按长度桶报 win-rate。产品侧通知摘要更该奖短而全。

强化学习（RL） 采样后画散点：横轴长度，纵轴 RM。如果大量样本长度和 RM 分都很高，金标质量却低，就说明 RM 可能在奖励长度。BoN 里强制留几条 监督微调（SFT） 短样本，防止完全离开参考文风。

## 追问

- **长度惩罚会不会伤推理链？** 数学过程长是必要的。按任务分：推理看对错，摘要看信息密度。不要全局罚长。
- **DPO 没有 RM，还会 hack 长度吗？** 会，如果偏好对里长的总是 chosen。hack 在数据上。
- **教师示范普遍很长怎么办？** 可学性和长度一起看，见 `dt-teacher-bias`。先精简冗长的示范，再做偏好训练。

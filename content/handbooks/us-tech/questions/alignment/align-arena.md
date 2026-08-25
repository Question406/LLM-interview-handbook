---
id: align-arena
section: alignment
order: 16
level: A
title: 对齐：Chatbot Arena / 在线 ELO 的偏差
quick: >-
  Arena 是众包成对战加 Bradley-Terry / ELO，测的是「自愿用户在自选 prompt 上的观感」，不是能力全集。长度、文风、
  选样本、曝光名、非平稳都会改分数。差几个 ELO 当发版依据不够。
tags:
  - LMSYS
  - Arena
  - ELO
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena
    url: https://arxiv.org/abs/2306.05685
    type: primary
  - title: Chatbot Arena — An Open Platform for Evaluating LLMs by Human Preference
    url: https://arxiv.org/abs/2403.04132
    type: primary
  - title: Length-Controlled AlpacaEval
    url: https://arxiv.org/abs/2404.04475
    type: primary
---

LMSYS 的 Arena 把「两个匿名模型打一场、人点赢」做成活榜。MT-Bench 论文先说明人偏好和 LLM judge 能对上；后续 Arena 论文把平台、ELO、置信区间写清楚。对齐 / 评测岗问这题，是怕你把公开榜当内部发版金标。不是某次现场逐字题。LLM judge 偏差见 `align-llm-judge`；长度见 `align-length-bias`。在线 A/B 产品闸门见 `design-eval-platform`。

## 它测的是什么分布

样本不是随机从能力空间抽的。用户自带 prompt：偏聊天、写代码、比文风，英语多，愿意打的人已经是「关心模型」的子群。难 prompt 更常扔给当时的头名，新模型吃到的题分布和旧模型不同。这是 **选择偏差**，不是 ELO 公式写错。

成对比较假设近似可传递，用 Bradley-Terry 估强度，再报 ELO 和区间。传递性在文风上经常破：A 赢写作、B 赢代码、C 赢安全拒答，三个环可以不传递。一个标量排行把切片压扁。平局、跳过、用户只打自己在行的题，都会进估计。面试先说「我把它当开放偏好的活探针」，再说「我不会用它替代私有切片」。采样不是均匀的：热门模型对战多，冷门模型区间永远宽，不能拿点估计硬排。

匿名很重要。UI 露出模型名，粉丝和声誉会进点击。位置也要随机，否则先出现的赢，和 judge 位置偏差同源。

## 文风、长度、非平稳

人点「更愿意用」时，markdown 列表、客套、更长、更像助手腔都加分。能力没涨、排版涨，ELO 也能涨。这和 RM 长度 hack 是同一条缝，训练若对着 Arena 调提示，等于用活榜当 RM，见 `align-reward-hack`。

在线 ELO 是非平稳的：用户群在变、对手池在变、默认温度在变、新模型进来把分数重新标。新旧分不能当同一把尺子。新模型早期场次少，区间宽，点估计乱跳。报分必须带对战场次和置信区间；差 5 分且区间重叠，说「并列」。

提示污染：用户把评测题、内部套话、jailbreak 模板打进 Arena。模型若在别处见过这些，分数虚。公开活榜做训练信号，等于把测试用户当标注员还泄漏分布，见 `align-eval-contam`。

投票不是专家标注：同一用户反复打同一类题，等于把那个人的文风权重放大。去重按用户、按 prompt 近邻。Glicko / 贝叶斯区间比裸 ELO 点估计更适合报「还不显著」。内部若要学 Arena，复制协议（盲、换位、固定题库），不要复制公开活流量。

## 面试里怎么用、怎么不用

我会用 Arena：看开放对话有没有明显变蠢、文风有没有翻车、和竞品的观感差。我不会用 Arena：替代 GSM / 代码单测 / 安全红队；决定 KL 或 $\beta$；证明「我们对齐进步了」。内部对照要用盲测、固定 prompt 集、长度匹配。Style control、length control 是后来榜上的补丁，承认偏差存在，不是消掉所有选择偏差。

发版表：私有能力切片 + 安全 + 污染报告 + 长度匹配人偏好 + 再看 Arena 方向。Arena 单独新高新低，只触发调查，不触发发版。

场次太少时点估计会跳。新模型必须报对战场次和区间；区间重叠就说并列。后期 LMSYS 加过 style control / length control，那是承认偏差，不是消掉自选 prompt 和用户子群。内部复现 Arena 协议（盲、换位、固定题库）可以，直接把公开活榜当回归门禁不行。

白板画两个轴：横轴真实任务成功率，纵轴 Arena ELO。理想是一起升。只升 ELO、任务不动，多半是文风和长度。只升任务、ELO 掉，可能是变短、变硬、少套话——不一定是失败。

## 追问

- **ELO 和 BT 差在哪？** 实现上都在估成对强度。ELO 有对局顺序和更新步长；静态 BT 一次拟合全部对。非平稳时两者都会漂。
- **为什么不把 Arena 当 RL 奖励？** 分布是自选 prompt，奖励延迟、可刷文风，而且泄漏测试。最多当稀疏探针。
- **小幅领先能写进发布说明吗？** 看区间和切片。写作赢、安全输，不能报一个「全面领先」。
- **和离线人偏好什么关系？** 离线集可分层、可复现、会过时。Arena 活、偏、不可复现到同一场。要两套，见 `design-offline-eval`。
- **匿名坏了怎么办？** 当声誉赛，分数作废。补救是重跑盲测，不要调温度「再刷一场」。
- **和 MT-Bench 怎么一起报？** MT-Bench 固定题、可复现；Arena 活分布。一个涨一个掉，先查文风和长度，再查题是否泄漏。

报分模板：模型版本、对战场次、区间、平均长度、是否 style-controlled。缺一项就把 ELO 当逸闻。和 `align-llm-judge` 一样，协议比模型名更重要。切片至少拆写作 / 代码 / 拒绝；总分领先、拒绝切片崩，仍是事故。

不要用公开 Arena 做训练循环。那是把测试用户写进 RM。内部盲测集要轮换，见 `align-eval-contam`。

---
id: afm-rm-soft-target-ties
section: alignment
order: 101
level: A
title: 偏好分歧：6 比 4 的投票，soft labels、confidence weight 和 tie 是同一件事吗？
quick: 我会保留6比4这个分歧，先查它是标注出了问题，还是两种回答各有合理之处，再决定怎么训练。
companies:
  - apple
tags:
  - Apple
  - AFM 补全 2026-10
  - Reward Modeling
  - 口述版
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-26'
sources:
  - title: 'HelpSteer2-Preference: Complementing Ratings with Preferences'
    url: 'https://arxiv.org/abs/2410.01257'
    type: primary
  - title: Aligning Crowd Feedback via Distributional Preference Reward Modeling
    url: 'https://arxiv.org/abs/2402.09764'
    type: primary
---

## 面试官可能这样问

六个人选 A、四个人选 B，这个标签你怎么用？

## 可以这样回答

我会先把十张票保留下来，而不是只存一个“A 赢了”。6比4和10比0表达的信息不同，尤其是在两条回答都合理的时候。

如果标注目标清楚、这些人也代表目标用户，我可以把0.6作为偏好 A 的 soft labels。但它和“这条数据有多可信”是两回事：十个人的6比4，和一个人的一次选择，证据量不同。遇到平票，我还会区分“都很好”“都很差”和“我看不懂”，因为这三种情况不能都变成同一个训练信号。

## 技术备查

## 场景与问题
十位 annotator 六人选 A、四人选 B；另一对只有一人选 A。两对都写 chosen=A、weight=0.6 合理吗？再讨论真正 tie、两条都差和无法判断。

## 参考答案
不合理。第一对的 0.6 可作为 $P(A\succ B)$ 的估计；第二对的样本量与证据不同。preference probability q 应进 soft-label BCE，权重 w 决定样本贡献，不能用 w=q 的单向 chosen loss 替代。若总体人群定义清楚，保留投票比例、标注人数与分组；否则混合比例连目标人群都不清楚。

“同样好”可按协议建 q=0.5 或显式 tie 模型；“都差”还需绝对质量标签，否则相对排序会把坏答案当正例；“看不懂”应弃权并转专家，不能硬算 tie。HelpSteer2-Preference 为比较评分与偏好提供同源数据，不能据此 assertion 任一目标普遍最优。

## 追问
**是否应该删掉全部 50/50？** 先抽查协议、知识不足与真实价值分歧；删除会让模型只见简单极端对，失去真实的 ambiguous cases。
**如何防止一个重度用户占据所有票？** 明确按用户还是按交互定义目标，对用户聚合或加权，并按用户做数据切分。


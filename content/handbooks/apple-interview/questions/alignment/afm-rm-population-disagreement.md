---
id: afm-rm-population-disagreement
section: alignment
order: 110
level: A
title: 群体偏好冲突：英语 annotator 共识很高，是否代表所有用户？
quick: 我会先弄清分歧来自理解错误，还是合理的偏好差异。多数票能定义一个总体目标，但不自动代表每组用户。
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
  - title: Aligning Crowd Feedback via Distributional Preference Reward Modeling
    url: 'https://arxiv.org/abs/2402.09764'
    type: primary
---

## 面试官可能这样问

不同用户群体喜欢相反的回答，要不要按多数票统一？

## 可以这样回答

我会先看大家为什么不同意。有时是翻译不自然，有时是标注规则没说清，也可能确实有人喜欢直接、有人喜欢详细。这些问题不能都靠多数票解决。

如果是合理偏好差异，我会保留分组和投票信息，明确产品到底服务谁。可以比较一个统一模型、按任务或 locale 调整，以及输出多个评价维度的办法。最后要看各组表现；总体涨了，但某一组持续变差，我会把这个结果摆出来，而不是只报一个平均数。

## 技术备查

## 场景与问题
两个 locale 对简洁、直接和拒绝措辞偏好相反。混合数据后总体准确率提高，小语种满意度下降。怎么决定统一 RM 还是条件化 RM？

## 参考答案
先让当地专家区分语言理解问题与价值偏好。固定同一任务的自然表达，不机械翻译；记录标注群体、协议和同意用途，避免不必要的敏感信息。比较统一模型加分层权重、按任务或 locale 条件化、多属性输出，再在各组独立 holdout set 上看收益。

Distributional Preference Reward Modeling 是表示偏好分布的一种公开研究路线，不保证自动公平。本题要求明确产品服务人群、最低可用标准、统一安全约束，以及冲突无法同时满足时的决策者。不能靠删掉少数票制造一致。

## 追问
**每组样本少怎么办？** 报告不确定性，优先专家 re-annotation 和主动补样，避免把噪声直接写成群体特征。
**个性化能改变所有安全标准吗？** 不能，偏好层和不可突破的产品约束应分别定义。


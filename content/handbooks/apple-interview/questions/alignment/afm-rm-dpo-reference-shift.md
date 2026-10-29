---
id: afm-rm-dpo-reference-shift
section: alignment
order: 114
level: A
title: DPO 深挖：chosen 概率也下降，为什么 loss 仍然改善？
quick: 因为 DPO 关心的是 chosen 相对 rejected、再相对 reference 的差距。两条概率都下降时，这个差距仍然可能变大。
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
  - title: Direct Preference Optimization
    url: 'https://arxiv.org/abs/2305.18290'
    type: primary
---

## 面试官可能这样问

chosen 的概率也下降，DPO loss 为什么还能变好？

## 可以这样回答

因为它优化的不是单独把 chosen 概率推高。比如 chosen 的 logprob 从负10变成负12，rejected 从负11变成负18，两条都降了，但它们的差距反而从1变成6。reference 固定时，DPO 目标仍然可能改善。

所以只看 loss 下降或 chosen 概率变化都不够。我会检查两边的概率、reference 是不是固定、回答长度和实际生成质量。如果模型在旧 preference pairs 上越学越好，当前回答却变差，还要查数据是不是已经跟不上新策略。

## 技术备查

## 场景与问题
chosen 的 logprob 从 −10 降到 −12，rejected 从 −11 降到 −18，reference policy 固定。DPO loss 下降但用户感觉退化，如何解释？

## 参考答案
相对差从 1 变成 6，因此参考差固定时 DPO margin 变大，即使两条绝对概率都下降。DPO 的隐式奖励与策略/reference policy log-ratio 有关，不是直接最大化 chosen 的监督似然。正常策略 normalization 会让其他回答分配发生变化，需看实际生成。

诊断分别记录 chosen/rejected logprob、长度、KL 的估计、输出风格与新策略任务成功。检查 reference 是否冻结、模板与 tokenization 是否一致、只在回答 token 上计分。补 current policy nearest neighbors 偏好、修数据覆盖，或有依据地组合 SFT；不能仅凭 chosen 概率下降就 assertion 训练错了。

## 追问
**beta 只是 learning rate 吗？** 不是，它进入偏好 logit 并关联 regularization 解释；改变后还需控制 optimizer 与 margin 分布。
**DPO 不训 RM 是否就没有 reward hacking？** 不会免疫错误偏好与 out-of-distribution (OOD) 利用，独立评价仍然必要。


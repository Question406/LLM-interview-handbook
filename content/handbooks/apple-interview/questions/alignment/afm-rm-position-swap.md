---
id: afm-rm-position-swap
section: alignment
order: 107
level: A
title: position bias：AB 和 BA 都选第一个，如何计分和分配人审？
quick: 这说明判断随顺序变了，不能直接叫 tie。我会先还原到底选了哪条回答，再单独统计不一致。
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
  - title: Large Language Models are not Fair Evaluators
    url: 'https://arxiv.org/abs/2305.17926'
    type: primary
---

## 面试官可能这样问

AB 时选第一个，BA 时也选第一个，这题怎么算？

## 可以这样回答

这两次其实选了不同的回答。AB 时第一个是 A，BA 时第一个是 B，所以我会记成顺序不一致，而不是说两条内容一样好。

如果要算交换顺序后的平均得分，A 可以拿0.5分，但我会同时报告不一致比例。否则，一个永远选第一个的 judge，看起来也能给出很“平衡”的总分。对于重要或不一致的题，我会再交给人看；两次都选同一条，也还需要检查它是不是选对了。

## 技术备查

## 场景与问题
同一对内容，AB 时 judge 选 first，BA 时仍选 first。你会把 A 的胜率记成 50% 还是记为错误？

## 参考答案
先还原身份：第一次 A 胜、第二次 B 胜，属于顺序不一致，不能称为内容 tie。预先定义指标：稳定 A 胜率、稳定 B 胜率、tie、inconsistent 比例；若算交换平均 A 得分可为 0.5，但必须同时报告不一致率。不同定义不可偷偷替换。

Balanced Position Calibration 是公开研究方向。实战中对全部或分层样本交换，保留原始判决、版本和成本；不一致且高风险的样本转人审。随机顺序只能消除固定展示的系统性优势，不能确认 judge 会判断正确性。

## 追问
**两次一致就一定对？** 不是，可能稳定偏爱同样的错误答案。
**能用总体 50% 判断位置无偏？** 不行，prompt 子组可能相反，必须看配对一致性及 evaluation slices。


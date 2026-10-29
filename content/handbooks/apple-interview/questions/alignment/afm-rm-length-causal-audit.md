---
id: afm-rm-length-causal-audit
section: alignment
order: 106
level: A
title: length bias：把奖励除以 token 数，为什么可能惩罚正确推理？
quick: 我会先查它喜欢的是必要信息，还是重复套话。直接除长度，可能把需要解释清楚的好答案也压下去。
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
  - title: Length-Controlled AlpacaEval
    url: 'https://arxiv.org/abs/2404.04475'
    type: primary
---

## 面试官可能这样问

RM 喜欢长答案，直接除以长度行吗？

## 可以这样回答

我会先看长答案为什么赢。有些题确实需要更长的解释；直接把分数除以长度，可能把必要的信息也惩罚掉。

我会挑一批题做内容对照。比如同一个正确答案，一版保留必要步骤，另一版只是多加客套和重复；再补一些“短但漏关键信息”的例子。这样才能看出 RM 是在认有用内容，还是单纯认长度。训练以后我会同时看正确性、完整性和长度，避免把偏长改成了偏短。

## 技术备查

## 场景与问题
RM 偏爱长回答。工程师提议 reward/length，并把每道题的长回答截成 100 token 再评。如何反驳并给可做的对照？

## 参考答案
长解释有时包含必要证据，截断会破坏内容。先按任务与正确性 evaluation slices；制作保留结论和证据的简洁版、原版，以及只添加重复套话的版本，核验编辑没有改变质量，再盲评。回归控制长度的指标可辅助比较，但依赖模型与数据支持，不能自动证明 causal 去偏。

Length-Controlled AlpacaEval 提出在统计模型中控制回答长度差；本题的内容等价干预是补充练习。训练侧补“短而正确胜过长而错”和“长而必要胜过短而缺失”两类对，保留任务要求。验收同时看长度分布、正确率与完整性，避免从偏长变成偏短。

## 追问
**长度匹配后能宣布无偏吗？** 只能排查一项因素，风格、来源和任务难度仍可能混杂。
**简洁本来就是产品偏好呢？** 明确写进协议，不能把明确的产品效用和意外捷径混为一谈。


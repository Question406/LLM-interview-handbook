---
id: afm-rm-safety-multiobjective
section: alignment
order: 116
level: A
title: 安全与帮助性：拒绝所有请求的 RM 为什么可能拿高分？
quick: 我会把不该回答却回答，和应该回答却拒绝，分开看。一个安全总分很容易把后者藏起来。
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
  - title: RewardBench
    url: 'https://arxiv.org/abs/2403.13787'
    type: primary
  - title: HelpSteer2
    url: 'https://arxiv.org/abs/2406.08673'
    type: primary
---

## 面试官可能这样问

安全分数提高了，但正常问题也一律拒绝，怎么处理？

## 可以这样回答

我会把两类错误分开报：危险请求没有拒绝，以及正常请求被错误拒绝。如果总是拒绝，第一项可能很好看，但产品已经没法正常帮助用户。

数据上我会补一些很接近的对照，比如真正有害的请求、讨论风险的教育内容，以及只需要澄清就能回答的问题，让模型学会区别。评价也用这几类独立任务。对于不可接受的风险，我会单独设限制，再看帮助性；不能让更多正常题的收益把严重违规平均掉。

## 技术备查

## 场景与问题
RM 选出的回答有害遵从率降低，但把正常化学作业、引用坏例子的批判分析也拒掉。如何设计数据与 release criteria？

## 参考答案
将“识别风险”和“给出合适帮助”分别标注，补最小差异的安全/不安全请求、允许的教育内容、部分可答请求和必要澄清。记录 over-refusal 与不当遵从，按语言和领域 evaluation slices，不把某种关键词出现等同于有害。

RewardBench 的分技能评价与多属性数据可作为设计参照；本题 threshold 为原创产品方案：不可接受的违规单独设上限，再在满足约束的候选中优化帮助性与成本。线性加权只是选择的一种方式，权重变化可能让关键风险被其他收益抵消。发布用独立安全 nearest neighbors 和正常任务验收。

## 追问
**拒绝率越低越好吗？** 不，目标是适当拒绝与适当帮助。
**一个总 RM 还是多头？** 多头更便于检查冲突，但共享表示仍可偏，需看 calibration、容量和实际决策方式。


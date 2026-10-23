---
id: dt-label-noise
section: good-data
order: 9
level: A
title: 监督数据「好」吗，怎么发现标签本身是错的？
quick: "先查标注协议和人际一致性 $\\kappa$，再用模型找可疑标签、交给人复核。Confident Learning 能估计标签噪声，找出来的样本由人确认后再改，别让模型自动翻转全部标签。训练集和评测集都要查，错标多的时候，加样本只会放大问题。"
companies:
  - apple
tags:
  - Apple
  - Annotation
  - Data Quality
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "Confident Learning: Estimating Uncertainty in Dataset Labels"
    url: https://arxiv.org/abs/1911.00068
    type: primary
  - title: Pervasive Label Errors in Test Sets
    url: https://arxiv.org/abs/2103.14749
    type: primary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
---

我会先查标注协议和人际一致性 $\kappa$，再用模型找出可疑标签，交给人复核。监督数据除了内容有用，标签也得可靠，标签错了，继续加样本只会把错误放大。

标签错误比想象中常见。Northcutt 等在 ImageNet、MNIST 和评论数据里，找出了不少原本被当作可靠的错标，后续研究还专门分析了测试集里的标签错误。测试集标签错了，模型看起来泛化更好，实际上可能只是更贴合错误答案。LLM 后训练也一样，只是标签换成了 chosen/rejected、要不要调用工具、要不要拒答。

$\kappa$ 低的时候，先看标注说明写得清不清楚，见 `dt-kappa-code`。协议没问题，再上算法。Confident Learning 在类条件噪声的假设下，用模型预测去估计「观测标签和可能的真实标签」的联合分布，适合质量分档、安全分类这类有监督的多类别任务。

不同标签还有各自要看的地方。偏好对通常要去掉打平的样本，以及只靠回答更长取胜的样本，见 `dt-pref-pair-code`。过程标签也会错，比如最终答案对了、推理步骤是编的，只检查结果的规则验证器（verifier）照样放行，见 `dt-math-verifier-code`、`dt-prm-steps`。评测集也要抽查：污染检查回答「模型见没见过这道题」，标签检查回答「参考答案是不是写错了」，两种问题都会让你误判模型，接着补错数据。

## 找到可疑标签以后

交给人复核，不要自动翻转全部标签。模型可能只是偏爱某个类别，它的判断不等于真实标签，安全拒答尤其不能让当前策略独自当裁判。改动要留审计记录，写清哪些标签改了、谁批准的。

## 追问

**预训练也有标签噪声吗？**
有，弱监督标签就是，比如语言 id、质量分和重复标记。语言分错了，文档就会进错训练分组和配比。

**cleanlab 能直接处理 10B 文档吗？**
不适合拿来做全量实时处理。优先用在 SFT、人标数据和评测参考标签上，网页数据靠抽查和分位数分析。

**5% 的错标严重吗？**
看类别。把安全拒绝和遵从标反 5%，通常比网页质量分错 5% 严重得多。

**可疑样本一定要改标签吗？**
不一定，有时候直接丢掉就行。Llama 3 丢弃差别很小的偏好对，就是为了减少不可靠的监督信号，条数变少，换来的是噪声降低。

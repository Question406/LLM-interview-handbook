---
id: dt-label-noise
section: good-data
order: 9
level: A
title: 监督数据「好」吗，怎么发现标签本身是错的？
quick: "先检查标注协议和人际一致性 $\\kappa$，再用模型找可疑标签、交给人复核。Confident Learning 可以估计标签噪声，找出的样本由人确认后再改，不要让模型自动翻转全部标签。训练集和评测集都要查：错误标签越多，增加样本越可能放大问题。"
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

监督数据除了内容要有用，标签也必须可靠。我会先检查标注协议和人际一致性 $\kappa$，再用模型找出可疑标签，交给人复核。标签错了，继续加样本只会放大错误。

标签错误比想象中常见。Northcutt 等在 ImageNet、MNIST 和评论数据里，找出了不少原本被当作可靠标签的错标；后续研究也专门分析了测试集里的标签错误。测试集标签错了，模型看起来泛化更好，实际上可能只是更贴合错误的答案。LLM 后训练也有同样的问题，只是标签变成了 chosen/rejected、是否调用工具、是否拒答。

## 先查协议，再用算法筛

人际一致性 $\kappa$ 低时，先检查标注说明写得是否清楚，见 `dt-kappa-code`。协议没问题，再用算法筛查。Confident Learning 在类条件噪声的假设下，用模型预测估计「观测标签和可能的真实标签」的联合分布，适合有监督的多类别任务，比如质量分档和安全分类。

不同类型的标签还有各自的检查：

- 偏好对通常要去掉评分打平的样本，以及只靠回答更长取胜的样本，见 `dt-pref-pair-code`。
- 过程标签也可能错。例如最终答案正确，推理步骤却是编的，只检查最终结果的规则验证器（verifier）仍会放行，见 `dt-math-verifier-code`、`dt-prm-steps`。
- 评测集也要抽查。污染检查回答的是「模型是否见过这道题」，标签检查回答的是「参考答案是否写错了」。两种问题都会让你误判模型，进而补错数据。

## 找到可疑标签后怎么做

把样本交给人复核，不要自动翻转全部标签。模型可能只是偏爱某个类别，它的判断不等于真实标签。安全拒答尤其不能让当前策略独自当裁判。改动要留审计记录，写清哪些标签改了、由谁批准。

有时候直接丢掉也是一种处理。Llama 3 丢弃差别很小的偏好对，就是为了减少不可靠的监督信号；这里条数变少，换来的是噪声降低。

## 追问

- 预训练也有标签噪声吗？有，弱监督标签就是，例如语言 id、质量分和重复标记。语言分错了，文档就会进入错误的训练分组和配比。
- cleanlab 能直接处理 10B 文档吗？不适合作为全量实时处理的路径。优先用在 SFT、人标数据和评测参考标签上；网页数据靠抽查和分位数分析。
- 5% 的错标严重吗？要看类别。把安全拒绝和遵从标反 5%，通常比网页质量分错 5% 严重得多。

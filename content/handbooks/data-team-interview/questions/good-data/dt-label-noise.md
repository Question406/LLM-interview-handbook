---
id: dt-label-noise
section: good-data
order: 9
level: A
title: 监督数据「好」吗，怎么发现标签本身是错的？
quick: "先检查标注协议和人际一致性 $\\kappa$，再用模型找可疑标签、交给人复核。Confident Learning 可以估计标签噪声，但不能直接相信模型、自动翻转全部标签。训练集和评测集都要查：错误标签越多，增加样本越可能放大问题。"
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

监督数据除了内容要有用，标签也必须可靠。先检查标注协议和人际一致性 $\kappa$，再考虑自动发现噪声的方法。标签错了，继续增加样本只会放大错误。

Northcutt 等在 ImageNet、MNIST 和评论数据中找出了不少原本被当作可靠标签的错标，后续研究也分析了测试集标签错误。模型可能看似泛化得更好，实际上只是更符合错误的测试答案。LLM 后训练也有同类问题，只是标签变成了 chosen/rejected、是否调用工具、是否拒答。

## 先检查协议，再用算法筛查

人际一致性 $\kappa$ 低时，先检查标注说明是否清楚，见 `dt-kappa-code`。Confident Learning 在类条件噪声假设下，用模型预测估计「观测标签与可能真实标签」的联合分布，适合有监督的多类别任务，例如质量分档和安全分类。

偏好对通常还要去掉评分打平的样本，以及仅靠回答长度取胜的样本，见 `dt-pref-pair-code`。

过程标签也可能错。例如最终答案正确，推理步骤却是编的；只检查最终结果的规则验证器（verifier）仍可能放行。这类问题见 `dt-math-verifier-code`、`dt-prm-steps`。

评测集也要抽查。污染检查回答的是「模型是否见过这道题」，标签检查回答的是「参考答案是否写错」。两者都可能让你误判模型，补错数据。

## 找到可疑标签后怎么做

把样本交给人复核，不能直接自动翻转全部标签。模型可能只是偏爱某个类别，并不代表它判断的就是真实标签。安全拒答尤其不能让当前策略独自当裁判。保存审计记录，写清哪些标签改了、由谁批准。

Llama 3 丢弃差别很小的偏好对，是为了减少不可靠的监督信号。这里减少条数，是在降低噪声。

## 追问

- 预训练也有标签噪声吗？有弱监督标签，例如语言 id、质量分和重复标记。语言分错，会让文档进入错误的训练分组和配比。
- cleanlab 能直接处理 10B 文档吗？不适合作为全量实时处理路径。优先用于 SFT、人标数据和评测参考标签；网页数据侧使用抽查和分位数分析。
- 5% 的错标严重吗？取决于类别。把安全拒绝和遵从标反 5%，通常比网页质量分错 5% 更严重。

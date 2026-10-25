---
id: ml101-metric-uncertainty
section: metrics
order: 9
level: A
title: "两个模型只差一个百分点，怎么判断是否可靠？"
quick: "先让两个模型在同一独立测试集上做配对比较，再对指标差值估计置信区间；一个百分点是否可靠取决于样本量、相关性和差异分布。用户或时间数据要按合适单位重采样，并把训练随机性和反复挑模型造成的偏差分开检查。"
tags:
  - ML101
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "SciPy: bootstrap"
    url: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html
    type: primary
  - title: "scikit-learn: Cross-validation"
    url: https://scikit-learn.org/stable/modules/cross_validation.html
    type: primary
---

一个百分点不能单独说明胜负，我会先检查两个模型是否在同一份、符合上线分布的独立测试集上评估，再估计指标差值的不确定性。对于可按样本重采样的情况，可以做配对 bootstrap：每次抽同一组样本索引，同时重算两个模型及其差值。SciPy 的 `paired=True` 就保留了这种索引配对。[SciPy: bootstrap](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html)。

配对很重要，因为同一个难样本可能让两个模型都失败，分别给两个分数做区间再比较，会丢掉这种相关性。比如两模型准确率是 90% 和 91%，可能只是很少几条预测不同，也可能在大量样本上互有胜负；需要保留逐样本结果才能判断差异有多稳定。

若一名用户产生多行记录，就不能把每行当作独立证据。可以按用户整体重采样；时间相关的数据则要采用符合依赖结构的分块方案，或在多个时间窗口重复验证。scikit-learn 的交叉验证指南也强调按群组和时间结构切分，避免普通随机切分造成乐观结果。[scikit-learn: Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)。

最终报告差值、区间、样本单位和测试规模，再问这点收益是否足以覆盖部署成本。测试样本重采样主要反映评估样本的不确定性，不能自动涵盖重新训练的随机性，也修复不了在同一测试集反复挑最好模型的偏差。

## 追问

**差值区间包含零，是不是证明两个模型一样？**
不是。它说明当前数据和方法不足以排除没有差异等可能性；要证明实用上的相近，需要先定义可接受差异，并做相应的等效性分析。

**换几个随机种子就够了吗？**
不够。种子主要反映训练过程的波动，测试样本和上线分布的不确定性仍在。可以分别报告跨种子与跨评估样本的变化。

**交叉验证五折的五个分数能当独立样本做普通检验吗？**
不能直接这样假设。不同折的训练数据大量重叠，分数相关；需要采用适合比较流程的方法，或保留最终独立测试作确认。

**统计显著就一定值得上线吗？**
不一定。非常大的样本也能检出微小差异，还要对照实际收益、错误代价、延迟与维护成本。

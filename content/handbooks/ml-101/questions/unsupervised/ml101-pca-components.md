---
id: "ml101-pca-components"
section: "unsupervised"
order: 7
level: "A"
title: "PCA 保留多少维？解释方差高就一定适合预测吗？"
quick: "PCA 的维度先按累计解释方差和资源预算选候选，再在训练折内拟合，用下游验证指标决定。解释方差只衡量输入信息保留多少，低方差方向也可能含有预测标签的关键信号。"
tags: ["ML101", "unsupervised"]
realInterview: false
status: published
format: "markdown"
updatedAt: "2026-10-22"
sources:
  - title: "scikit-learn: PCA"
    url: https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html
    type: primary
  - title: "scikit-learn: Pipelines and composite estimators"
    url: https://scikit-learn.org/stable/modules/compose.html#pipeline
    type: primary
---

PCA（主成分分析）保留多少维，要由用途决定：做压缩可以看累计解释方差，做预测还要验证下游模型。主成分按输入的方差排序，计算时没有用标签，因此高解释方差无法保证高预测分数。 [scikit-learn: PCA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html)

若协方差特征值是 $\lambda_1\ge\lambda_2\ge\cdots$，前 $k$ 维累计解释方差是 $\sum_{i=1}^k\lambda_i/\sum_i\lambda_i$。例如第一维是波动很大的测量噪声，第二维波动很小却恰好区分正负类，只保留第一维会留下大量方差、丢掉分类线索。

我会比较几个维度及不做 PCA 的基线，把标准化、PCA 和预测器放在同一条交叉验证流水线中。每折只在训练部分拟合，再变换验证部分；维度更低但验证分数相近时，才考虑计算与存储收益。 [scikit-learn: Pipelines and composite estimators](https://scikit-learn.org/stable/modules/compose.html#pipeline)

## 追问

**PCA 会自动标准化吗？**
常见 sklearn PCA 会中心化，但不自动把各特征缩到单位方差。单位不同且不希望量纲主导时，要先考虑标准化。

**解释方差留到 95% 就够吗？**
这是候选标准，不能普遍保证效果。图像重建、异常检测和预测任务可能需要不同维度。

**whitening 有什么变化？**
它把保留成分缩放到相近方差，可能有利于下游估计器，也会改变原先各方向的相对尺度，需要验证。

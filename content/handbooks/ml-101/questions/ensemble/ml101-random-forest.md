---
id: ml101-random-forest
section: ensemble
order: 3
level: S
title: 随机森林为什么要同时 random sampling 样本和特征？
quick: >-
  随机森林训练多棵树，再平均回归预测或分类概率。样本自助 sampling
  让树看到不同数据，分裂时随机选特征进一步降低树之间的相关性；只有各树犯错不完全同步，平均才能明显降低方差，单棵树过弱也会损失效果。
tags:
  - Machine Learning
  - ensemble
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'scikit-learn: Ensembles'
    url: 'https://scikit-learn.org/stable/modules/ensemble.html'
    type: primary
---

随机森林的思路是让多棵有差异的树一起预测。深树单独看容易随训练样本变化，但不同树的波动可以在平均时部分抵消。

只对样本做有放回抽样时，特别强的特征仍可能被每棵树选作根节点，树之间很相似。每次分裂只让一部分随机特征参与竞争，就能得到更多不同的分裂结构。

用简化的等方差假设看平均效果：若每棵树的预测方差为 $\sigma^2$，任意两棵树相关系数都为 $\rho$，平均 $B$ 棵树的方差为：

$$\operatorname{Var}(\bar f)=\rho\sigma^2+\frac{1-\rho}{B}\sigma^2.$$

树数增加只能压低第二项，降低相关性也很重要。不过把可选特征压得太少会让每棵树变差，所以需要验证。该公式是帮助理解的简化模型，真实树之间的方差与相关性并不完全相等。

## 面试追问

**随机森林树数越多越容易 overfitting 吗？**
增加树数主要减少有限棵树平均的随机波动，通常不会像不断加深单棵树那样明显加重 overfitting，但收益会趋稳，训练和预测成本继续增加。

**随机森林能预测训练范围之外的目标值吗？**
普通回归森林的叶子输出训练标签均值，平均后仍在训练标签范围内，因此不擅长线性趋势外推。预测未来持续增长的数据时需要特别验证。

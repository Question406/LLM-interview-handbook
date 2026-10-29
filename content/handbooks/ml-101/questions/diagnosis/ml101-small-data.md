---
id: ml101-small-data
section: diagnosis
order: 11
level: A
title: 小样本和高维数据怎么建立稳健的建模流程？
quick: >-
  小样本高维时，先用简单且有正则的模型建立基线，把
  standardization、特征选择和降维都放进训练折。按实体或时间划分、报告不确定性，再用学习曲线判断该增加数据还是调整模型，避免反复试验消耗唯一的测试集。
tags:
  - ML101
  - diagnosis
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-22'
sources:
  - title: 'scikit-learn: Common pitfalls and recommended practices'
    url: 'https://scikit-learn.org/stable/common_pitfalls.html'
    type: primary
  - title: 'scikit-learn: Validation and learning curves'
    url: 'https://scikit-learn.org/stable/modules/learning_curve.html'
    type: primary
---

小样本高维建模要先控制泄漏和估计波动，再谈模型复杂度。简单线性模型配合 regularization 通常是值得比较的基线；缺失填充、standardization、特征选择和 PCA 都必须只在训练部分拟合，否则验证分数会偏乐观。 [scikit-learn: Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html)

学习曲线把训练样本数与训练、验证表现放在一起看。若数据增加后验证还在改善，可以优先补代表性数据；若训练和验证都很差，则检查特征、目标与模型假设。曲线是诊断依据，不能保证每种任务补数据都有相同收益。 [scikit-learn: Validation and learning curves](https://scikit-learn.org/stable/modules/learning_curve.html)

例如只有少量用户、每人很多记录时，要按用户划分；随机拆记录会让同一个人同时进入训练与验证，虚增有效样本量。高维特征先清理重复和明显无效列，再在交叉验证内选择正则强度；报告各折或重复实验的波动，别只报最好一次。

## 追问

**能先对全部数据选特征再交叉验证吗？**
不能，尤其按标签选特征时会把验证信息提前用进去。筛选也应放在训练折内。

**必须做 PCA 吗？**
不必须。PCA 保方差不保标签信号，可以与正则模型和不降维基线一起比较。

**交叉验证次数越多，真实样本就越多吗？**
不会。它能帮助估计划分波动，但数据没有新增，折间也并非独立样本。

---
id: ml101-logistic-regression
section: linear-models
order: 3
level: S
title: "逻辑回归为什么能做分类？系数怎么解释？"
quick: "逻辑回归先对特征做线性打分，再用 sigmoid 映射成正类概率。它假设对数优势（log-odds）与特征线性相关，因此系数表示其他变量固定时对数优势的变化，指数化后表示优势乘以多少倍（odds ratio）；最后还要用阈值决定类别。"
tags:
  - Machine Learning
  - linear-models
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Linear Models"
    url: https://scikit-learn.org/stable/modules/linear_model.html
    type: primary
---

逻辑回归建模的是二分类的概率。线性分数可以取任意实数，sigmoid 把它变到 0 和 1 之间，便于表示某件事发生的可能性。

设特征向量为 $x$，系数为 $w$，截距为 $b$，则正类概率为：

$$p=\frac{1}{1+e^{-(w^\top x+b)}},\qquad\log\frac{p}{1-p}=w^\top x+b.$$

$p/(1-p)$ 叫优势，表示发生与不发生的概率之比。某特征系数为 $\log2$ 时，其他特征不变、该特征增加一个单位，优势会乘以 2；概率本身不会简单地乘以 2。例如原概率 0.2，优势是 0.25，翻倍后优势为 0.5，概率变成约 0.333。

训练通常用交叉熵并加入正则，阈值则按任务选择。线性的是对数优势和决策边界；如果原始特征关系复杂，需要交互特征或其他模型。

## 面试追问

**系数可以直接解释成因果效应吗？**
不能。系数描述给定模型和其他变量后的统计关联，混杂、选择偏差和特征相关都会影响它；因果解释需要额外设计和假设。

**独热编码后，一个类别的系数怎么解释？**
有参考类别时，系数表示在其他变量不变的条件下，该类别相对参考类别的对数优势差。要说明参考类别以及是否有正则。

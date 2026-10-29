---
id: ml101-svm-logistic
section: classical-models
order: 6
level: A
title: 线性 SVM 和逻辑回归的损失与输出有什么区别？
quick: >-
  线性 SVM 用间隔损失推动样本远离 decision boundaries，逻辑回归用对数损失拟合类别概率；两者都能加正则并得到 linear
  decision boundary。SVM 原始输出是决策分数，不天然等于概率，逻辑回归把分数经 sigmoid 转成概率。是否
  calibration、分类效果和成本仍要用验证数据比较。
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'scikit-learn: Support Vector Machines'
    url: 'https://scikit-learn.org/stable/modules/svm.html'
    type: primary
  - title: 'scikit-learn: SGDClassifier loss functions'
    url: >-
      https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.SGDClassifier.html
    type: primary
---

线性支持向量机（SVM）更直接优化分类间隔，逻辑回归则用概率的 negative log likelihood 训练。它们都对输入做线性打分，但损失对“已经分对”的样本处理不同。

设分数 $f(x)=w^\top x+b$，x 是特征、w 是系数、b 是截距，标签 $y\in\{-1,1\}$。经典 SVM 用合页损失（hinge loss） $\max(0,1-yf(x))$：正确且超过单位间隔后，这个样本的损失为零。逻辑回归用 $\log(1+e^{-yf(x)})$，随正确方向的分数增大平滑下降，但不会在有限间隔后直接归零。实现也可能使用 squared hinge，比较时要确认具体损失。见 [SVM 数学形式](https://scikit-learn.org/stable/modules/svm.html#mathematical-formulation) 和 [SGDClassifier 的损失定义](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.SGDClassifier.html)。

例如两条记录都分类正确，一条刚过 decision boundary、一条离 decision boundary 很远，SVM 主要还关心间隔不足的那条。逻辑回归仍会按概率误差更新两者。需要风险概率时，可优先把逻辑回归作为基线；SVM 的原始距离分数要额外做 probability calibration。

## 追问

**逻辑回归输出概率就一定 calibration 吗？**
不一定。模型设定、正则和分布变化都会影响概率，应查看可靠性曲线等 calibration 指标。

**SVM 能做非线性分类吗？**
可以用核方法，但这里比较的是线性 SVM。换核以后，decision-boundary expressiveness 和计算成本都变了。

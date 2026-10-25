---
id: ml101-adaboost
section: ensemble
order: 7
level: A
title: "AdaBoost 怎样改变样本权重？为什么怕标签噪声？"
quick: "AdaBoost 依次训练弱分类器，让上一轮分错的样本在下一轮更重要，再按弱分类器表现加权投票。难样本因此得到更多学习机会，错误标签也可能反复被加权。要看验证误差、异常高权重样本和标签质量，不能把增加轮数当成修复噪声的方法。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: AdaBoost"
    url: https://scikit-learn.org/stable/modules/ensemble.html#adaboost
    type: primary
  - title: "scikit-learn: AdaBoostClassifier"
    url: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.AdaBoostClassifier.html
    type: primary
---

AdaBoost 通过改变样本权重，让后面的弱分类器重点修正前面的错误，最后把各轮预测加权组合。开始时样本通常等权，之后分错的样本相对权重上升。

以经典二分类版本为例，标签和弱分类器输出取 $\{-1,1\}$。第 t 轮弱分类器记为 $h_t$，样本权重记为 $w_i$；当加权错误率满足 $0<\epsilon_t<1/2$ 时，计算 $\alpha_t=\tfrac12\log((1-\epsilon_t)/\epsilon_t)$，再更新 $w_i\propto w_i\exp(-\alpha_t y_i h_t(x_i))$ 并归一化。正确预测使指数为负，错误预测使指数为正；这是经典二分类公式，多分类 SAMME 的系数形式有所不同。[scikit-learn 的 AdaBoost 说明](https://scikit-learn.org/stable/modules/ensemble.html#adaboost) 介绍了逐轮重加权的机制。

例如大部分特征相近的样本都是正类，某条却被误标为负类。模型反复分错这条记录，它就可能获得很高权重，迫使后续树追逐难以泛化的噪声。因此我会检查高权重样本，限制弱学习器复杂度，并依据验证结果选择轮数和学习率。

## 追问

**难样本和错标签怎么区分？**
仅靠模型分错无法区分。要结合标注复核、特征质量和独立验证，不能直接删除全部难样本。

**每轮必须重采样吗？**
不一定。支持 sample weight 的弱学习器可以直接按权重训练，重采样只是实现加权训练的一种方式。

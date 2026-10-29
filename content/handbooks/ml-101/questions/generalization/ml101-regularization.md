---
id: ml101-regularization
section: generalization
order: 10
level: S
title: regularization 为什么能改善泛化？
quick: >-
  regularization
  把对模型复杂度的偏好加入训练目标，减少模型为了贴合少量噪声而大幅调整参数。它通常用一点训练拟合能力换取更稳定的预测，强度要通过验证集选择，过强也会
  underfitting。
tags:
  - Machine Learning
  - generalization
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'Google ML Crash Course: L2 regularization'
    url: >-
      https://developers.google.com/machine-learning/crash-course/overfitting/regularization
    type: primary
---

regularization 限制模型过于灵活的解，让它对样本噪声没那么敏感。在线性模型里，常用惩罚较大系数的办法：同样能解释训练数据时，更偏向参数较小的解。

以平方损失加 L2 正则为例，训练目标可以写成：

$$J(w)=\frac{1}{n}\sum_{i=1}^n(y_i-w^\top x_i-b)^2+\lambda\lVert w\rVert_2^2.$$

$n$ 是训练样本数，$w$ 是特征系数，$b$ 是截距，$\lambda$ 控制约束强度。通常不惩罚截距。增加 $\lambda$ 会让模型更不愿意用很大的系数去追逐个别样本。

比如两个特征几乎重复时，无正则模型可能给它们很大的正负系数，训练结果却差不多。加入正则后，这种相互抵消的解成本更高，估计通常更稳定。选择强度前要统一特征尺度，否则同一个惩罚对不同单位的特征约束不公平。

## 面试追问

**regularization 一定会降低测试误差吗？**
不会。模型本来就太简单，或数据量充足且无明显 overfitting 时，进一步约束可能增加偏差。应该比较验证表现。

**早停也算 regularization 吗？**
可以。训练太久可能逐渐拟合噪声，按独立验证表现停止能限制这种拟合；停止轮数也属于开发阶段选择，测试集不能参与。

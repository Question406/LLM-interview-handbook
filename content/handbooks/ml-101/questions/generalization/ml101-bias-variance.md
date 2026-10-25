---
id: ml101-bias-variance
section: generalization
order: 8
level: S
title: "偏差和方差分别是什么？能推一下误差分解吗？"
quick: "偏差表示模型平均预测离真实规律有多远，方差表示换一批训练样本后预测变化多大。在平方误差和零条件均值噪声的假设下，期望测试误差等于偏差平方、方差与不可约噪声之和。"
tags:
  - Machine Learning
  - generalization
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Validation curves and learning curves"
    url: https://scikit-learn.org/stable/modules/learning_curve.html
    type: primary
---

偏差描述模型长期学偏了多少，方差描述它对训练样本变化有多敏感。用直线拟合明显弯曲的关系，常有较高偏差；用复杂曲线紧贴少量带噪声样本，常有较高方差。

固定一个输入 $x$，设真实标签为 $y=f(x)+\epsilon$，其中噪声满足 $\mathbb{E}[\epsilon\mid x]=0$，并与训练集独立。对不同训练集 $D$ 和新标签噪声取期望，平方误差为：

$$\mathbb{E}_{D,\epsilon}[(y-\hat f_D(x))^2]=(f(x)-\mathbb{E}_D[\hat f_D(x)])^2+\operatorname{Var}_D(\hat f_D(x))+\operatorname{Var}(\epsilon\mid x).$$

这里 $\hat f_D$ 是在训练集 $D$ 上学到的模型。推导时在括号里加减平均预测 $\mathbb{E}_D[\hat f_D(x)]$，再展开平方；两个中心化随机量的均值为零，交叉项就消掉了。

这解释了为什么一味增加复杂度未必更好：它可能减小偏差，也可能放大样本扰动。实际用验证曲线比较模型复杂度，寻找独立验证误差较低的区域。

## 面试追问

**分类问题也直接用这个公式吗？**
这个等式针对平方误差。分类的零一损失有其他分解方式，不能把它当成所有损失的同一个定理。

**增加数据能消除偏差吗？**
通常不能消除模型表达能力带来的偏差。再多样本也无法让一条直线完整表示复杂曲线，但有代表性的额外数据往往能降低估计方差。

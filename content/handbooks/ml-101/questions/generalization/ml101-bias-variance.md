---
id: ml101-bias-variance
section: generalization
order: 8
level: S
title: 偏差和方差分别是什么？能推一下误差分解吗？
quick: >-
  假设模型无论换什么训练样本都只能学出一条过于简单的关系，这是高 bias 的直观情形。另一种情况是换一批样本，预测就变化很大，这是高 variance
  的直观情形。
tags:
  - Machine Learning
  - generalization
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: 'scikit-learn: Validation curves and learning curves'
    url: 'https://scikit-learn.org/stable/modules/learning_curve.html'
    type: primary
---

## 回答思路

> **问题与场景：** 假设模型无论换什么训练样本都只能学出一条过于简单的关系，这是高 bias 的直观情形。
>
> **做法与原因：** 前者可能需要更合适的特征或模型能力；后者可能需要更多独立数据、regularization 或降低复杂度。
>
> **检查与取舍：** 我会结合 training/validation 表现和重复划分后的稳定性判断，而不是只凭一次训练结果给模型贴标签。

## 可以这样回答

假设模型无论换什么训练样本都只能学出一条过于简单的关系，这是高 bias 的直观情形。另一种情况是换一批样本，预测就变化很大，这是高 variance 的直观情形。

前者可能需要更合适的特征或模型能力；后者可能需要更多独立数据、regularization 或降低复杂度。实际任务还包含无法由输入解释的 noise，不能指望所有误差都通过换模型消除。

我会结合 training/validation 表现和重复划分后的稳定性判断，而不是只凭一次训练结果给模型贴标签。正式误差分解及其假设放在后面的推导中说明。

## 技术备查

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

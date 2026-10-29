---
id: ml101-unbiased-variance
section: probability
order: 15
level: A
title: 样本方差为什么除以 n−1？什么情况下用 n？
quick: >-
  用同一批样本估计均值后，围绕样本均值的平方偏差和平均只有 (n−1)σ²，因此除以 n−1 才是总体方差的 unbiased
  estimate。这个结论要求独立同分布、有限方差且 n≥2，不要求正态。若总体均值已知，或只计算这批数据的描述性方差，可以使用不同的分母；正态模型的方差
  MLE 也除以 n。
tags:
  - ML Fundamentals
  - Statistics
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-23T00:00:00.000Z
sources:
  - title: 'NumPy var, ddof and sample variance'
    url: 'https://numpy.org/doc/stable/reference/generated/numpy.var.html'
    type: primary
---

除以 n−1 是为了补偿用样本均值替代未知总体均值带来的偏小，而不是所有“方差”都必须采用的计算规则。

设 $X_1,\ldots,X_n$ 独立同分布，总体均值为 $\mu$、方差为有限的 $\sigma^2$，n≥2。把平方偏差展开，有

$$
\sum_i(X_i-\bar X)^2=\sum_i(X_i-\mu)^2-n(\bar X-\mu)^2.
$$

取期望，第一项为 $n\sigma^2$，第二项为 $n\operatorname{Var}(\bar X)=\sigma^2$，所以左侧期望是 $(n-1)\sigma^2$。因此 $S^2=\sum_i(X_i-\bar X)^2/(n-1)$ 满足 $E[S^2]=\sigma^2$，不要求数据服从正态。

“少一个自由度”也可以帮助理解：残差之和恒为零，前 n−1 个残差一旦确定，最后一个就被约束住。上面的期望推导说明这个直觉为何恰好给出 n−1，而不是把它当作一句需要背下来的规则。

例如数据 [1,2,3] 的样本均值为 2，平方偏差和为 2。除以 n 得到 2/3，除以 n−1 得到 1。两个数分别对应不同的估计目标；单次得到 1 不代表它一定更接近未知真实方差，无偏说的是重复抽样的平均结果。

如果总体均值 $\mu$ 已知，$\sum_i(X_i-\mu)^2/n$ 已经是 unbiased estimate，不需要再为估计均值补偿。正态模型均值未知时，方差 maximum likelihood estimation 使用分母 n，虽然有偏，却直接对应似然优化目标。若只是把眼前有限列表当作全部对象描述，也常用分母 n。

**NumPy 的 ddof 应怎样设？**
`np.var(x)` 默认 ddof=0，分母为 n；`np.var(x, ddof=1)` 使用 n−1。应根据目标选择，并保证有效样本数大于 ddof。只有一个样本时无法用这种方式估计未知均值下的总体方差。

**开平方后也是无偏的吗？**
通常不是。平方根是非线性函数，$E[\sqrt{S^2}]$ 一般不等于 $\sqrt{E[S^2]}$；方差无偏不能直接推出标准差无偏。

**相关样本还能直接用这个推导吗？**
不能。样本均值方差包含协方差项，未必是 $\sigma^2/n$，上面的抵消关系随之改变。时间序列、重复测量或加权样本都需要根据具体抽样结构处理。

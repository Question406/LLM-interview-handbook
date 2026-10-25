---
id: ml101-poisson-regression
section: linear-models
order: 11
level: A
title: "为什么计数预测可能需要泊松回归？"
quick: "计数是非负整数，普通线性回归可能预测负数，也不符合计数随均值变化的噪声结构。泊松回归常用 log link，让条件均值等于线性分数的指数，天然为正。还要处理观察时长等暴露量，并检查过度离散和过多零值，不能只凭目标是整数就认定泊松假设成立。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: PoissonRegressor"
    url: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.PoissonRegressor.html
    type: primary
  - title: "scikit-learn: Poisson regression and non-normal loss"
    url: https://scikit-learn.org/stable/auto_examples/linear_model/plot_poisson_regression_non_normal_loss.html
    type: primary
---

泊松回归适合把事件次数的条件均值建成正值，例如预测一天收到多少请求。其中 x 是输入特征、w 是系数、b 是截距，$\mu(x)$ 是条件平均次数。模型使用 $\log\mu(x)=w^\top x+b$，所以 $\mu(x)=e^{w^\top x+b}$，不会像普通线性回归那样给出负的平均次数。

标准泊松模型还假设给定特征后，方差与均值相等。计数经常随均值增大而更波动，这比固定方差平方误差更贴近一些问题；但现实数据可能过度离散或零值过多，要根据诊断考虑其他模型。预测值是期望次数，可以是 2.5，不要求四舍五入成整数。[PoissonRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.PoissonRegressor.html) 给出 log link 的定义。

例如两家店开门时长不同，直接预测订单数会把营业更久误解成经营更强。可建模单位时间发生率，再乘暴露量；相应计数模型把 log 暴露量作为固定 offset。比较模型时应使用符合业务目标的计数损失和留出集，示例见 [泊松回归与非正态损失](https://scikit-learn.org/stable/auto_examples/linear_model/plot_poisson_regression_non_normal_loss.html)。

## 追问

**目标包含 0 可以用吗？**
可以。泊松分布允许零计数，log link 作用在预测均值上，不是要求对每个观测 y 取对数。

**目标是整数就一定选泊松吗？**
不一定。先看条件均值形式、离散程度、暴露量和验证效果，整数只是目标支持集的信息。

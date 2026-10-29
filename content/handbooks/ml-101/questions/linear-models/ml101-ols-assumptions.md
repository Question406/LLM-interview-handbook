---
id: ml101-ols-assumptions
section: linear-models
order: 7
level: A
title: OLS 的哪些假设用于 unbiased estimate，哪些用于统计推断？
quick: >-
  普通最小二乘（OLS）无偏的关键是线性模型、设计矩阵满列秩和误差条件均值为零；误差正态不是无偏的必要条件。同方差与不相关误差支撑经典效率和标准误公式，正态假设进一步给出有限样本的精确
  t/F 推断。异方差或相关数据下，要使用匹配结构的标准误和推断方法。
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'MIT: Fundamentals of Regression and OLS'
    url: >-
      https://ocw.mit.edu/courses/14-382-econometrics-spring-2017/29d3e55c546c9927eff0035735b35aa9_MIT14_382S17_14381notes.pdf
    type: primary
  - title: 'Berkeley STAT 151A: Test statistics under normality'
    url: 'https://stat151a.berkeley.edu/spring-2026/lectures/unit2/ols_normal.html'
    type: primary
---

普通最小二乘（OLS）在模型对系数线性、设计矩阵满列秩且误差条件均值为零时，得到条件无偏的系数估计。写成 $y=X\beta+\varepsilon$，其中 y 是观测目标向量，X 是特征矩阵，$\beta$ 是待估系数，$\varepsilon$ 是误差向量；条件均值为零表示 $E[\varepsilon\mid X]=0$。

原因直接来自 $\hat\beta=\beta+(X^\top X)^{-1}X^\top\varepsilon$：给定 $X$ 后，误差那项期望为零。若遗漏变量与已用特征相关，条件均值可能不为零，样本再大也不能靠经典标准误修好偏差。

同方差、误差间不相关时，经典协方差为 $\sigma^2(X^\top X)^{-1}$，并有 Gauss–Markov 的线性无偏最有效结论。再假设条件误差正态，才得到经典有限样本 t/F 分布；大样本推断可在适当正则条件下依靠渐近理论。推导见 [MIT 计量课程笔记](https://ocw.mit.edu/courses/14-382-econometrics-spring-2017/29d3e55c546c9927eff0035735b35aa9_MIT14_382S17_14381notes.pdf) 与 [Berkeley 正态模型推断](https://stat151a.berkeley.edu/spring-2026/lectures/unit2/ols_normal.html)。

例如大户型房价误差更分散，只要条件均值仍为零，OLS 系数仍可无偏，但沿用同方差标准误会错估不确定性。

## 追问

**异方差怎么办？**
独立观测且满足相应条件时可用异方差稳健标准误；分组相关或时间相关还要考虑聚类或时间相关的协方差估计。

**特征必须正态分布吗？**
不需要。经典正态假设针对给定特征后的误差，不能用特征的直方图代替检验。

---
id: ml101-common-distributions
section: probability
order: 4
level: A
title: "伯努利、二项、泊松和正态分布适合什么问题？"
quick: "伯努利描述一次二元结果，二项描述固定次数独立同分布试验中的成功数，泊松描述给定强度下的事件计数，正态描述连续量的钟形波动。选分布先看取值范围和产生过程，再检查独立性、概率或强度是否稳定。"
tags:
  - Machine Learning
  - probability
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Pishro-Nik: Special Discrete Distributions"
    url: https://www.probabilitycourse.com/chapter3/3_1_5_special_discrete_distr.php
    type: primary
  - title: "SciPy: Normal Distribution"
    url: https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html
    type: primary
---

我会先问随机变量是在数成功次数，还是测连续数值，再按生成过程选分布。只因为直方图看起来相似就套公式，很容易忽略试验之间的相关性或强度变化。

伯努利变量 $X\sim\operatorname{Bernoulli}(p)$ 只取 0、1，$P(X=1)=p$，均值为 $p$、方差为 $p(1-p)$。若做固定 n 次相互独立、成功概率都为 p 的试验，总成功数服从二项分布：

$$
P(K=k)=\binom nk p^k(1-p)^{n-k},\quad k=0,\ldots,n.
$$

它的均值是 $np$，方差是 $np(1-p)$。一次点击可以建模为伯努利；在这些假设成立时，100 次独立展示里的点击数就是二项。[离散分布教材](https://www.probabilitycourse.com/chapter3/3_1_5_special_discrete_distr.php)用对应随机试验解释了这两种分布。

泊松变量 $K\sim\operatorname{Poisson}(\lambda)$ 取非负整数，$P(K=k)=e^{-\lambda}\lambda^k/k!$，均值和方差都是 $\lambda$。例如用它描述一段固定时间的独立到达计数，要检查强度是否近似稳定；若来自齐次泊松过程，不相交时间段的计数独立。二项分布在 n 大、p 小且 np 接近固定值时可以近似为泊松。

正态变量 $X\sim N(\mu,\sigma^2)$ 取连续实数，$\mu$ 是中心，$\sigma>0$ 控制宽度；standardization 后 $(X-\mu)/\sigma\sim N(0,1)$。例如平均测量误差可在适当条件下用正态近似，但非负计数不能直接当精确正态模型。SciPy 的[正态分布文档](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html)里，`loc` 对应均值，`scale` 对应标准差。

## 追问

**方差明显大于均值，泊松还合适吗？**
需要怀疑。强度随人群或时间变化、事件聚集都可能造成过度离散；先查生成机制，再考虑能描述额外变异的计数模型。

**用户重复曝光，点击总数一定是二项吗？**
不一定。同一用户的反应可能相关，各用户的点击概率也可能不同，这会破坏独立同分布伯努利的前提。

**样本多了，原始数据就会变正态吗？**
不会。中心极限定理讨论的是 standardization 样本和或均值的分布，原始的二元结果仍然只有 0 和 1。

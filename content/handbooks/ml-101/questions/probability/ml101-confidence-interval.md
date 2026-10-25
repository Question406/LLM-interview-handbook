---
id: ml101-confidence-interval
section: probability
order: 8
level: A
title: "置信区间和预测区间有什么区别？"
quick: "置信区间描述总体参数估计的不确定性，预测区间覆盖未来新观测，还包括新观测自身的随机波动。95% 置信度是重复抽样时这套构造方法的覆盖率，不能解释成算出的区间有 95% 概率包含固定参数。相同条件下，预测区间通常更宽。"
tags:
  - Machine Learning
  - probability
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "NIST: Confidence Limits for the Mean"
    url: https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm
    type: primary
  - title: "NIST: Prediction Limits"
    url: https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/predlimi.htm
    type: primary
---

置信区间估计的是总体均值等参数，预测区间关心的是未来一次观测。平均值能估得很准，不意味着下一个个体也会紧贴平均值，所以两个区间不能互换。

以独立同分布的正态样本为例，样本量 $n\ge2$、均值 $\bar X$、样本标准差 s，均值的 $1-\alpha$ 置信区间为

$$
\bar X\pm t_{1-\alpha/2,n-1}\frac{s}{\sqrt n}.
$$

t 是自由度 n−1 的 t 分布分位数。95% 覆盖的意思是：按同样设计反复抽样、每次重新构造区间，长期约 95% 的区间包含固定的真均值。拿到某一次样本后，区间是否包含参数已经确定，不能据此赋予参数 95% 的后验概率，见 [NIST 的置信区间解释](https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm)。

若要预测一个来自相同总体、且独立于当前样本的新观测，区间变成

$$
\bar X\pm t_{1-\alpha/2,n-1}s\sqrt{1+\frac1n}.
$$

多出来的 1 来自新观测本身的方差。这个正态模型下的预测公式和假设见 [NIST Prediction Limits](https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/predlimi.htm)。

比如测量某种标准任务的耗时，100 次独立测量的标准差是 10 毫秒。均值估计的标准误是 1 毫秒，而下一次耗时的预测标准差约为 10.05 毫秒。增加测量次数能让均值区间持续变窄，却消除不了每次运行自带的波动。

## 追问

**95% 置信区间是否包含 95% 的样本点？**
不是。它是参数区间，不是观测分布的覆盖范围；预测区间和容忍区间也分别对应不同目标。

**数据不正态，还能用上面的公式吗？**
均值在适当大样本条件下可能有近似区间，但单个新观测的分布不会因为训练样本多就变正态。预测区间必须对误差分布或预测方法另做验证。

**换成贝叶斯可信区间，解释会不同吗？**
会。给定明确的模型和先验后，可信区间可以描述参数后验概率；它和频率学覆盖率是不同定义，不能只换名称。

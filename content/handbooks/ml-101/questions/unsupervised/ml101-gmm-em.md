---
id: "ml101-gmm-em"
section: "unsupervised"
order: 5
level: "A"
title: "GMM 和 EM 怎么交替估计隐变量与参数？"
quick: "GMM 把数据看成多个高斯分布的混合，每个点属于哪一组是隐变量。EM 先按当前参数算归属概率，再用这些软权重更新均值、协方差和混合比例，反复进行，结果依赖初始化。"
tags: ["ML101", "unsupervised"]
realInterview: false
status: published
format: "markdown"
updatedAt: "2026-10-22"
sources:
  - title: "scikit-learn: Gaussian mixture models"
    url: https://scikit-learn.org/stable/modules/mixture.html
    type: primary
---

GMM（高斯混合模型）用多个高斯分布解释数据；EM（期望最大化）则交替估计每个样本来自哪个分量，以及各分量的参数。它得到的是软归属，一个点可以对多个分量都有贡献。 [scikit-learn: Gaussian mixture models](https://scikit-learn.org/stable/modules/mixture.html)

设分量权重为 $\pi_k$，均值、协方差为 $\mu_k,\Sigma_k$。E 步计算责任度，也就是给定样本后的归属概率：

$$
r_{ik}=\frac{\pi_k\mathcal N(x_i\mid\mu_k,\Sigma_k)}{\sum_j\pi_j\mathcal N(x_i\mid\mu_j,\Sigma_j)}.
$$

设样本数为 $n$。M 步令 $N_k=\sum_i r_{ik}$，用加权均值更新 $\mu_k=\sum_i r_{ik}x_i/N_k$，再更新加权协方差及 $\pi_k=N_k/n$。例如点 5 位于两个分量之间，责任度是 0.6、0.4，它对两个中心的更新分别贡献这些权重；k-means 则只把它交给一个中心。

理想的精确 EM 更新不会降低观测数据的似然，但会停在局部解。实践中比较多个初始化，并给协方差加正则，防止一个分量收缩到单点、似然虚高。

## 追问

**分量越多越好吗？**
训练似然往往会增大，但泛化可能变差。用留出集似然或 BIC 这类兼顾复杂度的标准选数量。

**对角协方差省在哪？**
每个分量只估计各维方差，减少参数和计算，代价是无法表达分量内部的特征相关。

**EM 能保证找到真实分组吗？**
不能。模型假设、分量数量和初始化都会影响结果；高斯分量也不必等于业务类别。

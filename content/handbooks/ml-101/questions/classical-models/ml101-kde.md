---
id: ml101-kde
section: classical-models
order: 9
level: A
title: 核密度估计 KDE 怎么工作？带宽与分类有什么关系？
quick: KDE 在每个样本周围放一个平滑核，再平均得到概率密度。带宽决定平滑范围：过小会追着样本噪声起伏，过大会抹掉不同峰。用于分类时，分别估计各类条件密度，再结合类别先验比较后验概率，不能直接把密度值当成类别概率。
companies:
  - google
tags:
  - Machine Learning
  - Density Estimation
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: Google L5 MLE 候选人面经：高斯核密度方法讨论
    url: https://www.1point3acres.com/interview/thread/1116207
    type: secondary
  - title: scikit-learn Kernel Density Estimation
    url: https://scikit-learn.org/stable/modules/density.html
    type: primary
---

核密度估计（Kernel Density Estimation，KDE）用每个观测点附近的一小团密度来估计总体分布。样本密集的地方，许多核重叠，估计密度就高。它不预先限定整个分布只有一个高斯峰。

一维情况下，样本为 $x_1,\ldots,x_n$，带宽为正数 $h$，估计式为

$$
\hat p(x)=\frac{1}{nh}\sum_{i=1}^{n}K\left(\frac{x-x_i}{h}\right).
$$

$K$ 是积分为 1 的核函数；高斯核就是标准正态密度。$h$ 把核拉宽或缩窄，外面的 $1/h$ 保持积分为 1。密度描述单位区间内概率的集中程度，因此密度值可以大于 1；某个区间的概率需要积分。

例如样本集中在 0、0.1、3、3.1 附近，较小的合适带宽可以保留左右两团结构。带宽非常小，四个点各自形成尖峰；带宽很大，两团可能被连成宽峰。应在训练集内用交叉验证等方法选择带宽，避免查看测试集后反复调整。高维中每一维都要平滑，需要更多样本才能可靠估计局部分布。

用于分类时，对每一类估计 $\hat p(x\mid y=c)$，再计算与后验概率成比例的分数：

$$
s_c(x)=\hat\pi_c\hat p(x\mid y=c),\qquad
\hat P(y=c\mid x)=\frac{s_c(x)}{\sum_j s_j(x)}.
$$

$\hat\pi_c$ 是对应预测人群的类别先验。两类在某处的密度分别为 0.2 和 0.1，先验分别为 0.1 和 0.9，则未归一化分数是 0.02 和 0.09，应选第二类。直接比较密度会得到不同结论。若误判代价不同，还需要在后验概率上应用相应决策规则。

**KDE 与 KNN 有什么关系？**
二者都依赖局部样本。KDE 固定带宽来平滑密度；KNN 固定邻居数，邻域大小随局部数据密度变化。常见 KNN 分类直接投票，不必显式估计完整密度。

**数据特别大怎么办？**
直接计算一个查询的密度要遍历样本，d 维距离计算约为 $O(nd)$。可以考虑树索引、近似方法或更紧凑的分布模型，同时验证误差；高维下索引的收益可能有限。

面经只确认讨论了 Gaussian kernel density 是否更合适。带宽、公式、先验和数值例子是手册补充的教学解释，未披露为逐项原题。

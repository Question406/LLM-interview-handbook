---
id: ml101-mle-map
section: linear-models
order: 5
level: S
title: "最大似然 MLE 和最大后验 MAP 有什么区别？"
quick: "MLE 选择最能解释已观察数据的参数；MAP 再乘上参数先验，选择后验密度最大的参数。取负对数后，先验会表现为额外惩罚，例如零均值高斯先验对应 L2 形式；MAP 仍是点估计，并没有保留完整后验不确定性。"
tags:
  - Machine Learning
  - linear-models
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Dive into Deep Learning: Maximum Likelihood"
    url: https://d2l.ai/chapter_appendix-mathematics-for-deep-learning/maximum-likelihood.html
    type: primary
  - title: "scikit-learn: Linear Models"
    url: https://scikit-learn.org/stable/modules/linear_model.html
    type: primary
---

MLE 只根据似然选择参数，MAP 把先验偏好也放进去。这里数据已经观察到，优化时改变的是参数，不是在比较哪批数据更可能发生。

设参数为 $\theta$、数据为 $D$，则：

$$\hat\theta_{MLE}=\arg\max_\theta p(D\mid\theta),\qquad\hat\theta_{MAP}=\arg\max_\theta p(D\mid\theta)p(\theta).$$

贝叶斯公式中的 $p(D)$ 对固定数据与参数无关，找最大值时可以去掉。取负对数后，MAP 目标是负对数似然加负对数先验。

例如抛硬币五次全是正面，正面概率的 MLE 是 1。若先验为 Beta(2,2)，后验为 Beta(7,2)，MAP 是 $(7-1)/(7+2-2)=6/7$。这个小例子说明先验能缓和少量样本带来的极端估计；先验不合适时也会带来偏差。

在线性高斯回归中，给系数独立零均值高斯先验，会得到平方误差加 L2 惩罚的 MAP 目标。惩罚系数还取决于噪声方差、先验方差以及目标用求和还是平均。

## 面试追问

**MAP 和后验均值相同吗？**
通常不同。MAP 找后验密度最高的位置，后验均值对全部参数值按后验加权；偏斜或多峰分布下可能差得很大。

**数据足够多，先验就完全没影响了吗？**
在可辨识且满足一定正则条件的模型中，似然通常逐渐占主导。高维、弱识别或模型设定错误时，不能无条件说先验影响一定消失。

---
id: ml101-entropy-kl
section: probability
order: 12
level: A
title: 熵、cross entropy 和 KL 散度有什么关系？
quick: >-
  熵衡量分布自身的不确定性，cross entropy 衡量用预测分布 q 编码真实分布 p 的平均代价，KL 是相对最优编码多出的部分。离散情形有
  H(p,q)=H(p)+KL(p||q)。固定真实分布时，最小化 cross entropy 等价于最小化这个方向的 KL，但 KL 不是对称距离。
tags:
  - Machine Learning
  - probability
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'SciPy: Shannon Entropy and Relative Entropy'
    url: >-
      https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.entropy.html
    type: primary
  - title: 'SciPy: Stable Log-Sum-Exp'
    url: >-
      https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.logsumexp.html
    type: primary
---

这三个量可以放在同一个问题里理解：结果实际来自 p，我们却用 q 来分配概率。p 本身有多少不确定性用熵表示；用 q 猜这些结果的平均代价是 cross entropy；猜错分布多付的代价就是 KL。

对离散概率分布，在相同支持集上取自然对数，定义为

$$
H(p)=-\sum_xp(x)\log p(x),\qquad
H(p,q)=-\sum_xp(x)\log q(x),
$$

$$
D_{\mathrm{KL}}(p\|q)=\sum_xp(x)\log\frac{p(x)}{q(x)}
=H(p,q)-H(p).
$$

$p(x)=0$ 的项按极限取零；若某处 $p(x)>0$ 却 $q(x)=0$，cross entropy 和该方向 KL 为无穷。对数用 e 时单位是 nat，用 2 时单位是 bit。KL 非负，且在离散分布上仅当 p、q 相同才为零。[SciPy 的熵与 relative entropy 定义](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.entropy.html)也采用这些公式，并允许指定对数底。

比如真实硬币是 $p=(0.5,0.5)$，预测却是 $q=(0.9,0.1)$。按 bit 算，$H(p)=1$，cross entropy 是 $-0.5\log_2 0.9-0.5\log_2 0.1\approx1.737$，KL 约为 0.737。模型过分相信某一面，每当另一面出现时就付出更大的负对数代价。

监督分类的一条 one-hot 标签只有真类概率为 1，经验 cross entropy 就变成 $-\log q(y)$。数据集上平均这个损失，是在经验标签分布上拟合 q；它不代表我们已经知道真实总体的条件分布。实际实现还要使用稳定的 `log_softmax`，其 normalization 可以用 [log-sum-exp](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.logsumexp.html) 计算，避免先算出极小概率再取对数。

## 追问

**为什么说 KL 不是距离？**
它一般不对称，且不满足距离要求的三角不等式。交换 p 和 q 后，期望的 sampling 分布和惩罚方向都变了。

**把 H(p) 去掉，会改变分类训练的梯度吗？**
p 固定且与模型参数无关时不会，H(p) 是常数。所以最小化 cross entropy 和最小化 KL(p||q) 的优化目标相同；若 p 也在变化，就要重新检查。

**连续变量的熵也一定非负吗？**
不一定。连续情形用微分熵，密度和坐标尺度会影响它，微分熵可以为负；适当定义的 KL 仍然非负，别把离散熵的结论直接搬过去。

---
id: ml101-semisupervised-gmm
section: unsupervised
order: 9
level: A
title: 已知各类 embedding 近似高斯分布，怎样同时利用少量标签和无标签样本？
quick: 可以构造半监督高斯混合模型：有标签样本固定属于对应类别，无标签样本根据当前参数计算属于各类的责任度，再一起更新均值、协方差和类别比例。标签让混合成分与语义类别建立联系。这个方案依赖高斯分布等假设，训练后仍要用独立标签验证，不能把聚类编号直接当成真实类别。
companies:
  - google
tags:
  - Machine Learning
  - Semi-supervised Learning
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: Google 候选人面经：符号 embedding 的高斯分布与标签联合利用
    url: https://www.1point3acres.com/interview/thread/786697
    type: secondary
  - title: scikit-learn Gaussian Mixture Models
    url: https://scikit-learn.org/stable/modules/mixture.html
    type: primary
  - title: scikit-learn Semi-supervised Learning
    url: https://scikit-learn.org/stable/modules/semi_supervised.html
    type: primary
---

可以把有标签样本的类别固定下来，对无标签样本估计软归属，再联合更新分布参数。这是半监督学习：训练既用了已知类别，也用了无标签输入的分布信息。

原帖场景是符号识别：部分符号少见且没有标签，已有识别网络某层的向量据称分别服从不同的多维高斯分布，协方差为对角阵，参数未知。面试官追问如何同时利用标签与这些分布性质。以下固定 embedding、每类一个高斯成分的推导是手册重构方案；原帖没有确认面试官期待的唯一解，也没有给出联合训练 CNN 的完整要求。

记向量为 z，类别为 c。模型用类别比例 $\pi_c$ 和高斯密度 $\mathcal N(z;\mu_c,\Sigma_c)$ 表示联合分布。L 为有标签样本集合，U 为无标签样本集合，可最大化观测数据的对数似然：

$$
\ell=\sum_{i\in L}\log\left[\pi_{y_i}\mathcal N(z_i;\mu_{y_i},\Sigma_{y_i})\right]
+\sum_{i\in U}\log\left[\sum_c\pi_c\mathcal N(z_i;\mu_c,\Sigma_c)\right].
$$

有标签部分直接使用真实类别，无标签部分把潜在类别求和。这里假设二者来自相同目标分布，标签是可靠的，标注选择机制允许使用这个简单似然；若各类标注比例是人为控制的，就要重新处理先验和采样偏差。

EM 的 E 步对无标签样本计算责任度，也就是当前模型下属于某类的后验概率：

$$
r_{ic}=\frac{\pi_c\mathcal N(z_i;\mu_c,\Sigma_c)}{\sum_j\pi_j\mathcal N(z_i;\mu_j,\Sigma_j)}.
$$

有标签样本则设 $r_{ic}=1$ 当 c 等于真实标签，其余为 0。M 步令 $N_c=\sum_i r_{ic}$，用这些权重更新 $\mu_c=\sum_i r_{ic}z_i/N_c$ 和 $\pi_c=N_c/N$；N 为全部训练样本数。若使用对角协方差，第 a 个维度的方差为

$$
\sigma^2_{ca}=\frac{\sum_i r_{ic}(z_{ia}-\mu_{ca})^2}{N_c}.
$$

例如某个一维类别有两个已标注向量 0、2，另有无标签向量 4，对它的责任度为 0.5。那么该类的有效样本数是 2.5，更新后的均值为 $(0+2+0.5\times4)/2.5=1.6$。无标签样本以软权重参与，不需要先硬塞进某一类。

实际计算应在 log 域求密度并使用 log-sum-exp；对极小方差添加正则，避免协方差退化。某类有效样本数接近零时，需要重初始化或其他明确处理。固定对角协方差表示给定类别后的维度独立假设，一般会损失特征相关性，必须验证它是否足够。

**为什么有标签样本有帮助？**
无监督混合模型交换成分编号后，密度并不改变。可靠标签能把成分与语义类别对应起来，并约束参数估计；新符号如果完全没有标签，仍需要额外办法解释该成分的语义。

**一定要训练 CNN 吗？**
不一定。可以先固定预训练表示，只拟合上面的概率模型。若要更新网络，可以把相应目标写成可微损失并使用优化器，但这已经改变训练问题，需要额外验证表示是否退化、标签是否足够，以及分布假设是否仍成立。

---
id: ml101-bayesian-frequentist
section: probability
order: 16
level: A
title: 频率学派与贝叶斯怎样解释参数、不确定性和区间？
quick: >-
  频率学派通常把参数视为固定未知量，通过重复抽样评价估计方法与区间覆盖率；贝叶斯用先验和似然得到参数的后验分布，表达给定模型与数据后的不确定性。95%
  confidence interval 描述方法的长期覆盖，95% 可信区间描述 posterior probability
  质量，二者即使数值相近也不能交换解释。
tags:
  - ML Fundamentals
  - Statistics
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-23T00:00:00.000Z
sources:
  - title: 'CMU 36-705, Bayesian inference lecture 33'
    url: 'https://www.stat.cmu.edu/~siva/teaching/705/lec33.pdf'
    type: primary
  - title: 'Pishro-Nik, Bayesian interval estimation'
    url: >-
      https://www.probabilitycourse.com/chapter9/9_1_9_bayesian_interval_estimation.php
    type: primary
---

两种方法都可以从数据估计参数，但不确定性的概率解释不同。频率学派关心重复使用某个方法时表现如何；贝叶斯关心给定先验、模型和这次数据后，参数还可能取哪些值。

频率学派通常把 $\theta$ 视为固定未知量，抽样数据 D 随机，所以估计量和由数据构造的区间也随机。一个覆盖率为 95% 的区间程序，在相应模型与抽样条件下重复使用，约 95% 的区间会覆盖固定真实参数。观察到某一个具体区间后，这个覆盖率本身没有为参数提供一个后验分布。

贝叶斯指定先验 $p(\theta)$ 和似然 $p(D\mid\theta)$，更新为

$$
p(\theta\mid D)=\frac{p(D\mid\theta)p(\theta)}{\int p(D\mid u)p(u)\,du}.
$$

对参数设置分布，可以表示对未知量的知识状态，不要求现实中的物理参数在每次观测时随机改变。95% 可信区间是在这个后验分布下包含 95% 概率质量的区间；它的解释以先验和模型为条件。

用一个可算的例子比较：假设三个观测 [1,2,3] 独立来自 $\mathcal N(\mu,1)$，方差 1 已知。频率学派均值估计为 2，95% 正态 confidence interval 约为 $2\pm1.96/\sqrt3$，即 [0.868,3.132]。若贝叶斯先验为 $\mu\sim\mathcal N(0,1)$，后验为 $\mathcal N(1.5,0.25)$，95% 对称可信区间约为 [0.52,2.48]。先验把估计向 0 收缩，改变了中心和区间宽度。

两个区间分别对应不同程序与条件，不能仅凭哪个更窄就认定哪个更好。应检查模型、先验是否合理，以及需要的是后验决策、长期覆盖还是预测性能。

**可信区间一定有 95% 的频率覆盖吗？**
不一定。后验质量的定义不自动保证对每个固定参数都有相同覆盖率。可以额外用模拟或理论分析该贝叶斯程序的频率性质。

**频率学派不能用贝叶斯公式吗？**
可以使用条件概率和贝叶斯公式。区别在于是否对待估参数设置先验并据此作后验推断；使用贝叶斯公式处理已知分布，不足以把所有分析都归为贝叶斯参数推断。

**数据很多时，两者总会一致吗？**
在一些正则模型、合适先验和可辨识条件下，结果可能接近。模型错设、boundary parameters、高维或很强先验都可能让这种近似失效，不能当成无条件结论。

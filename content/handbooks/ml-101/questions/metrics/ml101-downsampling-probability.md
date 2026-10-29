---
id: ml101-downsampling-probability
section: metrics
order: 12
level: A
title: 负例 downsampling 后，怎样把预测概率修正回真实人群？
quick: >-
  若正负例分别按固定概率 s1、s0 随机保留，且模型学到 sampling 人群中的条件概率 q，则真实 odds 等于 sampling odds 乘
  s0/s1。所有正例保留、只留 r 比例负例时，真实概率为 rq/(1−q+rq)。修正依赖已知保留率、类内随机抽样和 sampling 概率已
  calibration；hard-negative mining 或已加逆概率权重时不能直接重复套用。
tags:
  - ML Fundamentals
  - Calibration
  - Sampling
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-23T00:00:00.000Z
sources:
  - title: 'Google Rules of Machine Learning, sampling and importance weighting'
    url: 'https://developers.google.com/machine-learning/guides/rules-of-ml'
    type: primary
  - title: 'Google ML Crash Course, class-imbalanced datasets'
    url: >-
      https://developers.google.com/machine-learning/crash-course/overfitting/imbalanced-datasets
    type: primary
---

downsampling 改变了训练人群的正负比例，模型直接输出的概率可能对应 sampling 后的分布。若只改变类别的保留概率，可以通过贝叶斯公式恢复原来的 odds；这一步是分布修正，不能替代对模型本身 calibration 误差的检查。

设 S=1 表示样本被保留，真实概率为 $p=P(Y=1\mid X=x)$，sampling 人群概率为 $q=P(Y=1\mid X=x,S=1)$。假设 $P(S=1\mid X=x,Y=1)=s_1$、$P(S=1\mid X=x,Y=0)=s_0$，两个保留率均为正且只依赖类别，则

$$
q=\frac{s_1p}{s_1p+s_0(1-p)},\qquad
\frac{p}{1-p}=\frac{s_0}{s_1}\frac{q}{1-q}.
$$

解得

$$
p=\frac{s_0q}{s_1(1-q)+s_0q},\qquad
\operatorname{logit}(p)=\operatorname{logit}(q)+\log(s_0/s_1).
$$

例如保留全部正例，只随机保留 10% 负例，模型在 sampling 人群中预测 q=0.5。代入得到 $p=0.1\times0.5/(0.5+0.05)=1/11\approx0.0909$，不是 0.05。直接把概率乘 0.1 忽略了 normalization 分母；在概率很小时才可能接近这种近似。

也可以利用训练目标中的逆保留率权重，让 sampling 样本对原分布风险作估计。若训练已经正确使用这类权重，且输出对应原分布，就不应再按上述“sampling 分布 q”公式修正一次。先确认 loss、权重和输出概率的含义，再选处理方式。

**修正之后排序会变吗？**
若 s0/s1 对所有输入都是同一正数，修正是严格单调变换，理论上保持排序及相应排序指标，但阈值、概率误差与业务成本的解释改变。浮点饱和或后处理舍入也可能影响实际平票。

**hard-negative mining 能直接修正吗？**
不能直接用一个全局负例保留率。难例选择依赖 X 或模型分数，sampling 后的类条件分布也改变。若每个输入的选择概率已知且正，可以讨论输入相关的权重或修正；没有覆盖的区域无法凭这个公式恢复信息。

**怎样检验是否有效？**
在保留真实比例的独立评估集上检查可靠性曲线、log loss、Brier score 和业务阈值表现。即使 sampling 规则完全已知，模型错设、有限样本或上线分布漂移仍会产生 calibration 误差。

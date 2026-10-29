---
id: ml101-bootstrap
section: probability
order: 7
level: A
title: Bootstrap 怎么估计不确定性？什么情况下会失效？
quick: >-
  Bootstrap 把当前样本当作经验总体，有放回抽取同样大小的样本，反复计算统计量，用 resampling 波动估计标准误和区间。它需要样本与
  resampling 单位能代表原 sampling 机制，不能修复 selection bias；相关数据、极值和退化样本都要特别处理。
tags:
  - Machine Learning
  - probability
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'SciPy: Bootstrap Confidence Intervals'
    url: >-
      https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html
    type: primary
---

Bootstrap 用“从现有样本再抽很多次”近似“重新采集很多份数据”，估计某个统计量会怎样波动。它适合解析标准误不好推、但能清楚定义 resampling 单位的问题。

对 n 个近似独立同分布观测，每轮有放回地抽 n 个，计算目标统计量 $\hat\theta_b^*$。做 B 轮后，用这些值的标准差估计标准误：

$$
\widehat{\mathrm{SE}}_{\mathrm{boot}}
=\sqrt{\frac{1}{B-1}\sum_{b=1}^B(\hat\theta_b^*-\bar\theta^*)^2},\qquad
\bar\theta^*=\frac1B\sum_{b=1}^B\hat\theta_b^*.
$$

这里的 B 是计算重复次数，n 才是原始样本量。百分位区间取 resampling 统计量的分位数；BCa 还会调整偏差和不对称，具体适用性要检查。[SciPy bootstrap 文档](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html)区分了 percentile、basic 和 BCa，也提醒退化分布可能让 BCa 返回无效结果。

比如有 200 个独立用户，要估计平均使用时长的误差，就 resampling 用户后求均值。若同一用户有 50 次会话，不能把一万条会话都当独立样本抽；可以按用户整组 resampling，再按原目标重新计算统计量。比较两个模型时，应在同一批测试对象上成对 resampling，保留两者的对应关系。

Bootstrap 只重复现有经验分布。样本没有覆盖的长尾或流失用户，它也抽不到；极端分位数、最大值等统计量的普通 bootstrap 可能近似很差。时间序列还需要保留依赖结构的块 resampling 等设计，不能直接逐点打乱。

## 追问

**把 B 加到很大，区间就一定准确吗？**
不会。它主要减少 resampling 计算本身的 Monte Carlo 误差，原数据太少或抽样有偏的问题仍在。

**Bootstrap 区间有 95% 覆盖率保证吗？**
通常是依赖条件和渐近近似的目标，有限样本不保证恰好 95%。需要检查统计量、样本规模和方法，不能把 resampling 次数当成保证。

**评估已训练模型时，要不要每轮重新训练？**
取决于想量什么。只 resampling 测试集得到的是固定模型下测试抽样的不确定性；要包括训练数据变化造成的波动，就需要 resampling 训练过程并重新拟合，代价也更高。

---
id: ml101-lln-clt
section: probability
order: 5
level: A
title: 大数定律和中心极限定理分别说明什么？
quick: >-
  大数定律说明样本均值会靠近总体期望；中心极限定理说明按 √n 放大的均值误差，在适当条件下接近正态。经典版本要求独立同分布，CLT
  还要求有限且非零的方差；它们不保证有偏样本能代表目标总体。
tags:
  - Machine Learning
  - probability
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'Pishro-Nik: Law of Large Numbers'
    url: 'https://www.probabilitycourse.com/chapter7/7_1_1_law_of_large_numbers.php'
    type: primary
  - title: 'Pishro-Nik: Central Limit Theorem'
    url: 'https://www.probabilitycourse.com/chapter7/7_1_2_central_limit_theorem.php'
    type: primary
---

大数定律回答“平均值最终会靠近哪里”，中心极限定理回答“围绕那个位置的误差大致怎样波动”。前者给一致性，后者帮助估计标准误和构造近似区间。

令 $X_1,\ldots,X_n$ 独立同分布，均值为 $\mu$、有限方差为 $\sigma^2$，记 $\bar X_n=n^{-1}\sum_iX_i$。一个常用的弱大数定律版本是，对任意 $\varepsilon>0$，

$$
P(|\bar X_n-\mu|>\varepsilon)\longrightarrow0.
$$

它讲的是偏离固定误差带的概率越来越小，不要求均值每多加一个样本都更接近真值。这里采用有限方差这个足够条件，更一般的大数定律还有更弱条件，见[大数定律](https://www.probabilitycourse.com/chapter7/7_1_1_law_of_large_numbers.php)。

若 $0<\sigma^2<\infty$，经典中心极限定理给出

$$
\frac{\sqrt n(\bar X_n-\mu)}{\sigma}\ \xrightarrow{d}\ N(0,1).
$$

箭头表示分布收敛。原始数据不必正态，接近正态的是 standardization 均值；有限样本近似好不好，还受偏斜、尾部和相关性影响。[CLT 教材](https://www.probabilitycourse.com/chapter7/7_1_2_central_limit_theorem.php)明确给出了这些经典假设。

比如独立点击的概率为 0.2，1000 次展示的点击率均值仍是 0.2，标准误约为 $\sqrt{0.2\cdot0.8/1000}\approx0.0126$。扩大样本能缩小随机误差；如果只采了活跃用户，估计可能稳定收敛到活跃用户的点击率，仍然不能代表全体用户。

## 追问

**样本量达到 30 就能放心用正态近似吗？**
没有统一的这个 threshold。高度偏斜、稀有事件或重尾数据可能需要更多样本，要结合分布和目标统计量检查。

**时间序列有相关性怎么办？**
经典独立版本不能直接套。要用适合依赖结构的极限定理和标准误估计，或按时间块处理，不能把每条记录都当作独立信息。

**无限方差会怎样？**
上面按 $\sqrt n$ 缩放的经典 CLT 不再有保证。部分分布会收敛到其他极限分布，不能继续用样本标准差机械套正态区间。

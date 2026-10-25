---
id: ml101-expectation-variance
section: probability
order: 3
level: A
title: "期望、方差和协方差有哪些常用性质？"
quick: "期望对加法是线性的，不需要独立；方差衡量围绕均值的平方波动，缩放 a 倍会变成 a² 倍。两项相加的方差还要加上两倍协方差，只有协方差为零时才能直接相加。"
tags:
  - Machine Learning
  - probability
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Pishro-Nik: Expectation"
    url: https://www.probabilitycourse.com/chapter3/3_2_2_expectation.php
    type: primary
  - title: "Pishro-Nik: Covariance and Correlation"
    url: https://www.probabilitycourse.com/chapter5/5_3_1_covariance_correlation.php
    type: primary
---

算期望时可以先拆和，算方差时要先检查协方差。这能避免把“期望的线性”错误地套到方差上。下面默认涉及的期望存在，方差和协方差讨论要求二阶矩有限。

对常数 $a,b,c$，有

$$
E[aX+bY+c]=aE[X]+bE[Y]+c,
$$

$$
\operatorname{Var}(X)=E[X^2]-E[X]^2,\qquad
\operatorname{Var}(aX+b)=a^2\operatorname{Var}(X).
$$

期望是按概率加权的平均，所以加法可以直接拆开；方差把偏差平方，缩放量也要平方。[期望教材](https://www.probabilitycourse.com/chapter3/3_2_2_expectation.php)给出了加权平均和线性性质。

两项同时变化时，要额外计算

$$
\operatorname{Cov}(X,Y)=E[XY]-E[X]E[Y],\qquad
\operatorname{Var}(X+Y)=\operatorname{Var}(X)+\operatorname{Var}(Y)+2\operatorname{Cov}(X,Y).
$$

正协方差会放大总波动，负协方差会抵消一部分。比如 $X$ 以相同概率取 0、1，令 $Y=X$，两者方差都是 $1/4$。总和其实是 $2X$，方差为 1；忽略协方差会误算成 $1/2$。这些等式可从平方展开得到，见[协方差及和的方差](https://www.probabilitycourse.com/chapter5/5_3_1_covariance_correlation.php)。

## 追问

**独立样本的均值为什么更稳定？**
若 n 个样本独立同分布、方差为 $\sigma^2$，样本均值的方差就是 $\sigma^2/n$，标准差为 $\sigma/\sqrt n$。存在相关性时要把各项协方差加回来，不能直接除以 n。

**E[XY] 能写成 E[X]E[Y] 吗？**
独立且相关期望可积时可以。一般情况二者相差的就是协方差，不能随意拆乘积。

**协方差大小能直接比较相关程度吗？**
不能跨单位直接比较。把长度从米改成厘米，协方差也会放大；相关系数除以两个标准差后才消除了这种尺度影响，且标准差必须非零。

---
id: ml101-independence
section: probability
order: 2
level: A
title: "独立、不相关和条件独立有什么区别？"
quick: "独立表示联合分布能拆成边缘分布的乘积；不相关只表示协方差为零，只排除了线性关联。条件独立是在给定 Z 后才成立的独立关系，既不能自动推出无条件独立，也不一定由无条件独立推出。"
tags:
  - Machine Learning
  - probability
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Pishro-Nik: Covariance and Correlation"
    url: https://www.probabilitycourse.com/chapter5/5_3_1_covariance_correlation.php
    type: primary
  - title: "Pishro-Nik: Conditional Independence"
    url: https://www.probabilitycourse.com/chapter1/1_4_4_conditional_independence.php
    type: primary
---

独立比不相关强：独立排除了整个分布层面的依赖，不相关只说明协方差为零。条件独立则要先固定一个条件变量，再看剩下的两个变量是否还有依赖。

对离散变量，独立写成 $P(X=x,Y=y)=P(X=x)P(Y=y)$，所有取值都要满足；连续变量用联合密度或事件概率表达。二阶矩存在时，独立能推出 $\operatorname{Cov}(X,Y)=0$，反向一般不成立。[协方差教材](https://www.probabilitycourse.com/chapter5/5_3_1_covariance_correlation.php)明确区分了独立和零协方差。

比如让 $X$ 等概率取 $-1,0,1$，令 $Y=X^2$。此时 $E[X]=E[XY]=0$，所以协方差为零；但知道 $X=0$ 就确定 $Y=0$，知道 $X=1$ 就确定 $Y=1$，显然存在依赖。这是“线性相关系数看不见非线性关系”的小例子。

条件独立 $X\perp Y\mid Z$ 表示，对有正概率的每个 $z$，有 $P(x,y\mid z)=P(x\mid z)P(y\mid z)$。例如先随机选一个硬币种类 Z，再用这枚硬币独立抛两次。给定硬币种类后，两次结果独立；不知道种类时，第一次正面会提高“选到偏正面硬币”的可能性，进而影响第二次正面的概率。[条件独立的定义](https://www.probabilitycourse.com/chapter1/1_4_4_conditional_independence.php)要求在相同条件下比较这两个概率。

## 追问

**什么情况下不相关足以推出独立？**
联合高斯变量可以，但仅仅各自边缘分布是高斯还不够，需要联合高斯这个条件。

**特征相关系数接近零，就能删掉交叉特征吗？**
不能据此决定。上面的平方关系已经说明，非线性依赖可能很强，需要结合任务和验证集检查交叉信息。

**给变量加一个条件，总能消除依赖吗？**
不能。条件化也可能引入依赖。例如两个独立的二值变量，在知道它们的和为 1 后，一个是 1 就意味着另一个是 0。

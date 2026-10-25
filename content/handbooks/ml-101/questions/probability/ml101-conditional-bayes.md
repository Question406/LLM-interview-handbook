---
id: ml101-conditional-bayes
section: probability
order: 1
level: A
title: "条件概率和贝叶斯公式怎么用？"
quick: "条件概率是在已知条件发生的范围内重新计算概率；贝叶斯公式用先验和似然把条件方向反过来。计算时先写清事件，再用全概率公式算分母，避免把 P(A|B) 当成 P(B|A)。"
tags:
  - Machine Learning
  - probability
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Pishro-Nik: Conditional Probability"
    url: https://www.probabilitycourse.com/chapter1/1_4_0_conditional_probability.php
    type: primary
  - title: "Pishro-Nik: Bayes’ Rule"
    url: https://www.probabilitycourse.com/chapter1/1_4_3_bayes_rule.php
    type: primary
---

条件概率是缩小观察范围后重新算概率；贝叶斯公式让我们从“某类数据容易出现什么信号”，反推“看到信号后更可能是哪一类”。两者都要先明确条件是谁，条件事件的概率必须大于零。

对事件 $A,B$，定义和反向换算是

$$
P(A\mid B)=\frac{P(A\cap B)}{P(B)},\qquad
P(A\mid B)=\frac{P(B\mid A)P(A)}{P(B)}.
$$

第一式把 $B$ 当作新的样本空间，第二式把联合概率分别按两种顺序展开。$P(A)$ 是先验，$P(B\mid A)$ 是似然，$P(A\mid B)$ 是后验。若 $A$ 与其补集覆盖全部情况，分母为 $P(B)=P(B\mid A)P(A)+P(B\mid A^c)P(A^c)$。[条件概率](https://www.probabilitycourse.com/chapter1/1_4_0_conditional_probability.php)与[贝叶斯公式](https://www.probabilitycourse.com/chapter1/1_4_3_bayes_rule.php)的定义都从联合概率得到。

比如做垃圾邮件识别。假设 1000 封里有 100 封垃圾邮件；规则能命中其中 90 封，又误报其余 900 封中的 90 封。看到“被规则命中”后，垃圾邮件占 $90/(90+90)=50\%$。规则的召回率虽然是 $90\%$，命中后的可信程度仍受垃圾邮件本来占多少影响。

## 追问

**先验很低时，为什么误报会这么明显？**
非目标样本很多，少量误报率也会积累成大量误报。先把概率换成同一批样本里的实际数量，再比较通常最直观。

**贝叶斯公式要求 A 和 B 独立吗？**
不要求。如果独立，$P(B\mid A)=P(B)$，后验正好等于先验，观察 B 就没有提供关于 A 的新信息。

**连续特征怎么处理？**
用条件密度和边缘密度做同样的换算。在密度模型适用、分母非零的位置计算，不能把单点密度当成某个精确数值出现的概率。

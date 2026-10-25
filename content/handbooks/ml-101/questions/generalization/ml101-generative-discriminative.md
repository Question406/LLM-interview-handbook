---
id: ml101-generative-discriminative
section: generalization
order: 4
level: A
title: "生成式模型和判别式模型有什么区别？"
quick: "判别式方法直接学习给定输入时的标签概率或决策边界；经典生成式分类器先学习类别先验和每类的输入分布，再用贝叶斯公式分类。朴素贝叶斯属于后者，逻辑回归属于前者；生成式模型也能完成分类。"
tags:
  - ML101
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Stanford CS229: Generative learning algorithms"
    url: https://see.stanford.edu/materials/aimlcs229/cs229-notes2.pdf
    type: primary
---

判别式方法直接学怎样根据输入预测标签；经典生成式分类器先描述每个类别会产生怎样的输入，再反过来判断样本属于哪类。区别在所建模的概率对象，生成式方法同样可以做分类。Stanford CS229 的生成式学习讲义用高斯判别分析和朴素贝叶斯作例子。[Stanford CS229: Generative learning algorithms](https://see.stanford.edu/materials/aimlcs229/cs229-notes2.pdf)。

设输入是 $x$、类别是 $y$。逻辑回归直接建模 $p(y\mid x)$；生成式分类器建模先验 $p(y)$ 和类条件分布 $p(x\mid y)$，得到联合分布，再用贝叶斯公式：

$$
p(y\mid x)=\frac{p(x\mid y)p(y)}{\sum_{y'}p(x\mid y')p(y')}.
$$

分子表示这个类别产生当前输入的相对可能性，分母把所有类别归一化。仅为选最大概率类别时，可以比较分子，因为分母对各类别相同。

比如识别垃圾邮件，朴素贝叶斯先统计垃圾邮件比例，以及垃圾邮件和正常邮件各自的词出现模式；新邮件来了，比较哪一类更可能生成这些词。逻辑回归则直接学习各词怎样改变「是垃圾邮件」的概率。前者对输入分布作了更多假设，假设合适时有帮助，假设错了也会影响结果。

## 追问

**生成式一定能生成逼真的样本吗？**
不一定。经典生成式分类器描述了数据分布，但其简化假设可能无法生成逼真的文本或图像；建模联合分布和输出质量是不同问题。

**SVM 没有概率输出，也算判别式吗？**
算。直接学习分类边界或分类分数也属于判别式思路，并不要求一定输出校准概率。

**哪一类一定更准确？**
没有统一答案。要看分布假设、数据量、目标和误差代价，用同一独立评测协议比较，不能仅凭生成式或判别式的名称判断。

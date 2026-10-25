---
id: ml101-feature-interactions
section: data
order: 10
level: A
title: "什么情况下需要构造交互特征或多项式特征？"
quick: "当一个特征的作用取决于另一个特征，或线性模型残差显示有曲线关系时，可以构造交互项或低阶多项式项。先用业务假设限定候选，再在训练折内生成、缩放和正则化；高阶展开会快速增加维度和过拟合风险。"
tags:
  - ML101
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: PolynomialFeatures"
    url: https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.PolynomialFeatures.html
    type: primary
---

如果基础模型无法表达「一个变量的效果取决于另一个变量」，可以加入交互项；如果效果随单个变量弯曲变化，可以试平方项等多项式特征。它们让简单模型能表达更丰富的关系，但要用独立验证确认收益。scikit-learn 的 PolynomialFeatures 支持多项式与仅交互展开，也提醒高阶展开容易过拟合。[scikit-learn: PolynomialFeatures](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.PolynomialFeatures.html)。

以线性模型为例，只有温度和湿度两列时，它们各自的斜率固定。加入温度乘湿度后，温度的影响可以随湿度变化；加入温度平方后，可以表达一定的弯曲。模型仍对新特征的系数线性，所以「线性模型」也能拟合原始输入上的非线性关系。

例如预测用电量，温度极高或极低时需求都可能升高，单一温度斜率难以表达这种形状，可以比较加入平方项后的验证误差。若高湿度会改变高温下的用电关系，再试温度与湿度的乘积。这里是说明建模思路的示意，是否适用要靠数据检查。

我会先查看基线残差和业务机制，只展开少量候选；在训练折内完成变换和缩放，再配合正则化。特征数和阶数增大时，生成的列数会迅速增长；外推到训练范围之外时，多项式也可能给出很极端的预测。

## 追问

**交互项和平方项有什么不同？**
交互项描述不同输入的共同作用，例如温度乘湿度；平方项描述同一输入的曲率。仅交互展开通常不包含单个变量的高次幂。

**树模型还需要手工交互吗？**
不一定需要，树可以通过连续分裂学习交互。但受深度、数据量和训练限制，有业务依据的特征仍可试验，最终看验证与维护成本。

**训练误差下降就保留吗？**
不够。新增列通常更容易拟合训练数据，要同时看独立验证、尾部预测、稳定性和线上计算成本。

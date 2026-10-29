---
id: ml101-target-encoding
section: data
order: 7
level: A
title: 目标编码怎么避免标签泄漏？
quick: >-
  先划分外层训练和验证，再在训练集内部做折外目标编码：每行只用其他折的标签统计。验证与测试使用整个外层训练集学到的映射；高基数和小样本类别还需平滑，时间或用户相关数据要按相应
  split 构造 encoding。
tags:
  - ML101
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'scikit-learn: TargetEncoder'
    url: >-
      https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.TargetEncoder.html
    type: primary
---

目标编码要让每条训练样本的表示看不到自己的标签，也看不到验证或未来标签。我会先切开外层训练和验证，再只在训练部分内部做交叉拟合，也叫折外编码。scikit-learn 的 TargetEncoder 明确区分了使用交叉拟合的 `fit_transform` 和直接 `fit` 后再 `transform` 同一批数据。[scikit-learn: TargetEncoder](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.TargetEncoder.html)。

假设用商家平均转化率作为特征，如果某商家只有一条记录，这条记录的标签就会直接变成它的特征。模型在训练里很容易学到这种对应，线上却拿不到当天的结果。交叉拟合把训练集分成若干折，编码某一折时，只用其他折统计；小类别再向训练部分的整体均值平滑，减少偶然波动。

例如一个训练折中商家 A 的其他记录有 10 条、2 次转化，那么待编码行可使用由这 10 条估出的统计量，不能把待编码行自身的转化结果加进去。验证阶段，则用全部外层训练集重新学到的类别映射转换验证行，整个过程都不读验证标签。

如果要预测未来，普通随机折仍可能把未来标签带到过去，应该按时间计算当时可用的统计。若目标是泛化到新用户或新商家，也要按对应实体分组。编码的隔离单位必须和评估目标一致，平滑只能减少方差，无法修复标签泄漏。

## 追问

**先在全量数据上算好目标编码，再交叉验证行吗？**
不行。验证标签已经进入特征，后面的切分无法撤销泄漏。每个外层训练折都要单独拟合编码与模型。

**训练折外编码和测试全训练映射不同，会不会出问题？**
它们统计的数据量不同，这是需要验证的差异。折外编码避免训练行自泄漏，测试映射则利用当时合法可用的训练标签；可以通过平滑和验证控制不稳定性。

**只有每个类别一条样本，目标编码还能学什么？**
可复用的类别统计很弱。应更多依赖整体先验或其他特征，不能把单条标签当作可靠的类别属性。

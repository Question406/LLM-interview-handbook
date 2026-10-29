---
id: ml101-dataset-shift
section: diagnosis
order: 4
level: A
title: 协变量漂移、标签漂移和概念漂移怎么区分？
quick: >-
  协变量漂移是 P(x) 变、P(y|x) 不变；标签漂移是 P(y) 变、P(x|y) 不变；概念漂移是输入到标签的关系 P(y|x)
  改变。它们是不同假设，可能混合发生，只看输入分布或预测分数变化不足以确定是哪一种。
tags:
  - ML101
  - diagnosis
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-22'
sources:
  - title: 'Dive into Deep Learning: Environment and Distribution Shift'
    url: >-
      https://d2l.ai/chapter_linear-classification/environment-and-distribution-shift.html
    type: primary
---

这几种漂移按联合分布哪一部分变化来区分。协变量漂移假设输入分布 $P(x)$ 改变，条件关系 $P(y\mid x)$ 不变；标签漂移假设类别比例 $P(y)$ 改变，而 $P(x\mid y)$ 不变；概念漂移通常指 $P(y\mid x)$ 改变。 [Dive into Deep Learning: Environment and Distribution Shift](https://d2l.ai/chapter_linear-classification/environment-and-distribution-shift.html)

例如固定人群内，信用规则不变但来申请的年龄结构变了，可以先怀疑协变量漂移；某类商品占比变了、各类商品特征分布相同，是标签漂移的示意；相同特征组合在新环境下对应不同违约概率，则涉及概念漂移。这些例子都要用数据验证，现实中可能同时变化。

我会对齐训练与线上数据的时间、定义与切片，先查特征缺失、范围、类别比例和服务管道，再用成熟标签比较各切片的条件误差。输入漂移是排查信号，不能单凭它断言准确率已经下降，也不能从预测类别比例反推真实标签比例。

## 追问

**没有标签能发现概念漂移吗？**
只能得到间接预警。要确认相同输入下标签关系变化，通常还需标签、人工抽查或额外结构假设。

**发现漂移就重训吗？**
先查管道错误和影响。字段编码错了应修管道，真实分布变化才评估重训、重加权或阈值调整。

**标签漂移时 P(y|x) 也会变吗？**
可能会。贝叶斯公式里类别先验变了，后验也会跟着变，因此这些概念不能简单按互斥标签来理解。

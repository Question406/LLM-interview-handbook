---
id: ml101-inductive-bias
section: generalization
order: 6
level: A
title: 什么是归纳偏置？为什么所有模型都带有假设？
quick: >-
  归纳偏置是模型面对没见过的输入时，用来偏好某些解释的假设。模型结构、特征、regularization
  和训练算法都能带来偏置；有限训练样本无法唯一确定所有新输入的答案，所以泛化需要这些偏好。
tags:
  - ML101
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'Tom Mitchell: The Need for Biases in Learning Generalizations'
    url: 'https://www.cs.cmu.edu/~tom/pubs/NeedForBias_1980.pdf'
    type: primary
---

归纳偏置就是学习器在多个都能解释训练数据的规则之间，会优先选择哪一种。有限样本只能约束已经出现的位置，对没见过的输入还需要额外假设。Mitchell 的原文把偏置来源分成可表达的假设空间和搜索这个空间时的偏好。[Tom Mitchell: The Need for Biases in Learning Generalizations](https://www.cs.cmu.edu/~tom/pubs/NeedForBias_1980.pdf)。

比如训练数据里的几个点落在一条直线上，既可以画一条直线，也可以画出穿过这些点却在中间剧烈弯曲的函数。两者训练误差都可能为零，却给新位置不同答案。选直线，就是相信关系较简单、能延续到附近位置；这个信念来自模型限制，训练点本身不能证明它必然正确。

偏置也会藏在训练方法里。限制函数形式会排除一些解；regularization 会偏好较小或较稀疏的系数；特征设计会决定哪些关系更容易表达。因此「模型很灵活」也不代表完全没有假设。

我会检查这些假设是否符合任务，再看独立验证的表现。偏置贴近真实结构时，可以减少所需数据；如果任务包含直线表达不了的变化，强行限制成直线就会产生系统性误差。

## 追问

**归纳偏置就是模型的不公平偏见吗？**
不是同一个概念。这里说的是泛化时对假设的偏好；公平性语境的偏见讨论某些人群受到的差异影响，两者可能相互作用，但定义不同。

**训练误差为零，就证明偏置选对了吗？**
没有。很多函数都可能拟合训练点，还要用符合目标场景的独立数据检查它在新输入上的表现。

**去掉 regularization，就没有归纳偏置了吗？**
仍然有。函数族、特征表示和搜索过程都还在限制或偏好某些答案，regularization 只是其中一种来源。

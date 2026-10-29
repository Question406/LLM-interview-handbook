---
id: ml101-kernel
section: classical-models
order: 2
level: A
title: 核技巧是什么？RBF 核的 gamma 有什么影响？
quick: 假设两类点在原来的二维平面里无法用直线分开，但换一种特征表示后可能可以。Kernel trick 让算法直接计算高维特征的内积，而不用显式构造全部特征。
tags:
  - Machine Learning
  - classical-models
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: 'scikit-learn: Support Vector Machines'
    url: 'https://scikit-learn.org/stable/modules/svm.html'
    type: primary
---

## 回答思路

> **问题与场景：** 假设两类点在原来的二维平面里无法用直线分开，但换一种特征表示后可能可以。
>
> **做法与原因：** RBF kernel 用距离表示相似度。
>
> **检查与取舍：** 我会先 standardization 特征，再联合选择 gamma 与 C。

## 可以这样回答

假设两类点在原来的二维平面里无法用直线分开，但换一种特征表示后可能可以。Kernel trick 让算法直接计算高维特征的内积，而不用显式构造全部特征。

RBF kernel 用距离表示相似度。两点距离平方为 1 时，gamma 为 0.1，相似度约 0.905；gamma 为 10，就接近零。所以 gamma 越大，影响越局部。

我会先 standardization 特征，再联合选择 gamma 与 C。Kernel 省掉显式展开，不保证大规模训练便宜，还需要看样本数与实际计算。

## 技术备查

核技巧把“先映射到高维再求内积”合成一个相似度计算。算法只需要这些内积时，就能学出原输入空间里的非 linear decision boundary，无需真的存下所有高维特征。

若映射为 $\phi(x)$，核函数满足 $K(x,z)=\phi(x)^\top\phi(z)$。常用 RBF 核是：

$$K(x,z)=\exp(-\gamma\lVert x-z\rVert^2).$$

$x,z$ 是两个样本，$\gamma>0$ 控制距离的作用。两点距离平方为 1 时，$\gamma=0.1$ 的相似度约为 0.905，$\gamma=10$ 时约为 0.000045，所以更大的 gamma 会让影响迅速变得局部，decision boundary 也可能更曲折。

实际先 standardization，再在对数尺度搜索 gamma 和 C。核方法省掉的是显式特征展开，并不保证计算便宜；训练要处理大量样本之间的关系，规模大时可以考虑线性模型或近似核。

## 面试追问

**任意相似度都能直接做 SVM 核吗？**
标准核 SVM 通常要求核矩阵对称且半正定，保证对应某个内积并得到预期的凸优化问题。任意自定义相似度不自动满足。

**gamma 很小一定 underfitting 吗？**
它倾向于产生更平缓的相似度变化，但表现还依赖 C、数据尺度和分布。应联合调参，避免把单个参数当作绝对诊断。

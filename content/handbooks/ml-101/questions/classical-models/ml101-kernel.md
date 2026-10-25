---
id: ml101-kernel
section: classical-models
order: 2
level: A
title: "核技巧是什么？RBF 核的 gamma 有什么影响？"
quick: "核技巧通过直接计算特征映射后的内积，在不显式展开高维特征的情况下学习非线性边界。RBF 核用距离衡量相似性，gamma 越大，单个样本影响范围越局部；要先处理尺度，再和 C 一起验证，核 SVM 大样本训练也可能很贵。"
tags:
  - Machine Learning
  - classical-models
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Support Vector Machines"
    url: https://scikit-learn.org/stable/modules/svm.html
    type: primary
---

核技巧把“先映射到高维再求内积”合成一个相似度计算。算法只需要这些内积时，就能学出原输入空间里的非线性边界，无需真的存下所有高维特征。

若映射为 $\phi(x)$，核函数满足 $K(x,z)=\phi(x)^\top\phi(z)$。常用 RBF 核是：

$$K(x,z)=\exp(-\gamma\lVert x-z\rVert^2).$$

$x,z$ 是两个样本，$\gamma>0$ 控制距离的作用。两点距离平方为 1 时，$\gamma=0.1$ 的相似度约为 0.905，$\gamma=10$ 时约为 0.000045，所以更大的 gamma 会让影响迅速变得局部，边界也可能更曲折。

实际先标准化，再在对数尺度搜索 gamma 和 C。核方法省掉的是显式特征展开，并不保证计算便宜；训练要处理大量样本之间的关系，规模大时可以考虑线性模型或近似核。

## 面试追问

**任意相似度都能直接做 SVM 核吗？**
标准核 SVM 通常要求核矩阵对称且半正定，保证对应某个内积并得到预期的凸优化问题。任意自定义相似度不自动满足。

**gamma 很小一定欠拟合吗？**
它倾向于产生更平缓的相似度变化，但表现还依赖 C、数据尺度和分布。应联合调参，避免把单个参数当作绝对诊断。

---
id: ml101-svm
section: classical-models
order: 1
level: S
title: SVM 为什么最大化间隔？C 控制什么？
quick: >-
  SVM 在分类正确的同时，希望 decision boundary 离附近样本更远，减少小扰动导致的翻转。软间隔允许部分样本进入间隔或分错，用 C
  权衡这些违例与 decision-boundary complexity；C 大更重视训练违例，C 小约束更强。
tags:
  - Machine Learning
  - classical-models
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'scikit-learn: Support Vector Machines'
    url: 'https://scikit-learn.org/stable/modules/svm.html'
    type: primary
---

SVM 选择能留出较大分类间隔的 decision boundary。两条线都分对训练样本时，离样本更远的那条通常对小范围扰动更稳定；这是一种模型偏好，最终泛化仍要验证。

令标签 $y_i\in\{-1,1\}$、线性分数为 $w^\top x_i+b$。软间隔目标可以写成：

$$\min_{w,b}\frac12\lVert w\rVert^2+C\sum_i\max(0,1-y_i(w^\top x_i+b)).$$

当样本的带符号分数小于 1 时，hinge loss 会产生惩罚；分对但距离 decision boundary 很近，也可能有惩罚。在 standardization 的约束下，两条 margin boundaries 的距离是 $2/\lVert w\rVert$，所以缩小 $\lVert w\rVert$ 对应扩大间隔。

例如少数误标点远离主体时，过大的 C 可能让 decision boundary 为它们明显转动。较小 C 愿意接受一些违例，保持更平滑的 decision boundary。使用时先关注特征尺度，再联合验证 C 和核参数。

## 面试追问

**支持向量是不是所有分错的点？**
包含分错或进入间隔的点，也可能包含恰好在 margin boundaries 上的点。它们在对偶表示中有非零系数，共同决定决策函数。

**SVM 分数能直接当概率吗？**
不能。distance to decision boundary 没有自动对应发生率，需要额外概率估计或 calibration；分类决策与概率质量要分别验证。

---
id: ml101-cross-entropy
section: linear-models
order: 4
level: S
title: "交叉熵为什么适合逻辑回归？梯度怎么推？"
quick: "逻辑回归假设标签服从伯努利分布，对其似然取负对数就得到二元交叉熵。单样本对线性分数的梯度是预测概率减真实标签，既有明确概率解释，也便于稳定优化；实现应直接使用 logits 形式的损失。"
tags:
  - Machine Learning
  - linear-models
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Google ML Crash Course: Logistic regression loss and regularization"
    url: https://developers.google.com/machine-learning/crash-course/logistic-regression/loss-regularization
    type: primary
---

交叉熵来自逻辑回归的概率假设。真实标签 $y\in\{0,1\}$，模型预测正类概率为 $p$，一次观察的概率是 $p^y(1-p)^{1-y}$。取负对数，就得到：

$$\ell=-y\log p-(1-y)\log(1-p).$$

如果真实标签是 1，预测 0.9 的损失约为 0.105，预测 0.1 的损失约为 2.303。越自信地报错，代价越大。

设线性分数 $z=w^\top x+b$，$p=\sigma(z)$。链式法则给出：

$$\frac{\partial\ell}{\partial z}=p-y,\qquad\nabla_w\ell=(p-y)x.$$

所以模型把正例预测得过低时，更新会把它的分数向上推。多个独立样本的负对数似然相加或取平均，就形成训练目标。代码通常从 $z$ 直接计算稳定的 logistic loss，避免先求极小概率再取对数造成溢出或无穷值。

## 面试追问

**用 sigmoid 后的 MSE 也能训练吗？**
能，但通常得到不同的优化性质。它的梯度还乘上 sigmoid 的导数，在极端错误但饱和的分数上可能更新很小；逻辑回归的交叉熵梯度更直接。

**交叉熵下降，准确率一定提高吗？**
不一定。概率从 0.6 改为 0.8 可以降低损失，但两者在 0.5 阈值下都判正，准确率不变。两种指标关注不同方面。

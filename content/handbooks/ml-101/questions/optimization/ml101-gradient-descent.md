---
id: ml101-gradient-descent
section: optimization
order: 1
level: S
title: "梯度下降为什么沿负梯度走？学习率怎么选？"
quick: "梯度给出局部变化最快的上升方向，所以足够小的一步沿负梯度移动会降低可微目标。学习率控制步长，太大可能震荡或发散，太小收敛慢；应先检查特征尺度和损失曲线，再选择初始值与衰减策略。"
tags:
  - Machine Learning
  - optimization
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Google ML Crash Course: Gradient descent"
    url: https://developers.google.com/machine-learning/crash-course/linear-regression/gradient-descent
    type: primary
---

梯度下降每次按当前目标的局部变化方向调整参数。对可微目标 $J(\theta)$，做小位移 $\Delta$ 时，一阶近似是：

$$J(\theta+\Delta)\approx J(\theta)+\nabla J(\theta)^\top\Delta.$$

取 $\Delta=-\eta\nabla J(\theta)$，右边的变化项变为 $-\eta\lVert\nabla J(\theta)\rVert^2$，当学习率 $\eta>0$ 且足够小时就会下降。步子大到一阶近似失效，下降不再有保证。

例如 $J(w)=w^2/2$，更新为 $w_{t+1}=(1-\eta)w_t$。在这个特定例子里，$0<\eta<2$ 会收敛，$\eta=2$ 会在正负之间来回跳，过大则发散。这个范围取决于目标曲率，不能直接搬到所有问题。

实际先尝试几个数量级的学习率，观察有限步内损失是否稳定下降；必要时 standardization 特征、降低学习率或使用调度。比较时还应看总计算量和验证表现。

## 面试追问

**梯度为零就找到最小值了吗？**
不一定。非凸目标里还可能是局部极大值或鞍点。凸可微问题的零梯度点是全局最优，但是否唯一还取决于目标性质。

**训练损失偶尔上升一定有 bug 吗？**
不一定。小批量梯度有噪声，单步或单批次损失可以波动。持续发散、非有限值或多次重复都无法拟合小样本时才需要进一步排查。

---
id: ml101-convex-local
section: optimization
order: 5
level: A
title: "凸优化和非凸优化的局部最优有什么区别？"
quick: "在凸可行域上最小化凸函数时，任何局部最优也是全局最优；非凸问题没有这个保证。凸不代表最优解一定存在或唯一，严格凸且最优解存在时才能保证唯一。神经网络通常非凸，梯度小还可能处于鞍点，不能直接宣称找到了全局最优。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Dive into Deep Learning: Convexity"
    url: https://d2l.ai/chapter_optimization/convexity.html
    type: primary
---

凸问题的局部最小值就是全局最小值，前提是目标函数和可行域都满足凸性。非凸问题可能有优劣不同的局部最小值，也可能出现梯度为零却不是最小值的鞍点。

凸性表示任意两点间连线上的函数值，不超过两端函数值的线性插值。如果局部最小点之外还有更低的可行点，沿连接两点的方向走很小一步，就应该变得更低，这与“局部已经最小”矛盾。这里可行域必须凸，连线上的点才能继续可行。证明见 [D2L 凸性一节](https://d2l.ai/chapter_optimization/convexity.html#local-minima-are-global-minima)。

例如 $f(x)=(x-1)^2$ 在 x=1 的局部最小就是全局最小；但 $e^x$ 虽然凸，在整个实数轴上只会越来越接近零，没有达到最小值。一个有平坦底部的凸函数也可以有很多最优点，所以凸性只排除“比别处差的局部最优”。

## 追问

**梯度为零就代表最优吗？**
无约束、可微凸函数的驻点是全局最小；一般非凸函数不成立。有约束问题还要用适当的可行方向或最优性条件判断。

**神经网络非凸，为什么还用梯度法？**
梯度仍提供局部下降方向，实践中能得到有用解；是否训练好、泛化好，要靠实际结果，不能借用凸问题的全局保证。

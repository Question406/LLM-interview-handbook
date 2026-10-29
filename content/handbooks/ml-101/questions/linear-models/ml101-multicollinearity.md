---
id: ml101-multicollinearity
section: linear-models
order: 6
level: A
title: "多重共线性会影响预测还是系数解释？"
quick: "多重共线性首先让系数不稳定、难以解释，预测是否变差还取决于新数据是否保持相同关系。相近特征能互相替代，模型很难分清各自贡献；完全线性相关时，普通最小二乘（OLS）的系数不唯一。可以按目标删合重复信息，或用 Ridge 稳定估计，再在独立数据上评估预测。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Ordinary Least Squares"
    url: https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares
    type: primary
---

多重共线性对系数解释的影响通常比对同分布预测更直接。两个特征几乎表达同一件事，模型很难确定贡献该分给谁，轻微扰动就可能让系数大幅变化。

例如面积同时用平方米和平方英尺表示，两列完全成比例，可以用很多组系数组合给出同样预测。若只是高度相关，解可能唯一，但特征矩阵 X 的 $X^\top X$ 接近奇异，系数方差会很大。预测还留在这些相关特征常见的组合上时，彼此抵消仍可能给出稳定结果；换到相关关系不同的新数据上，就更容易出错。

我会先看特征定义、矩阵秩或条件数，再按目的处理。需要解释独立贡献，就合并或删除重复测量，并报告不确定性；主要追求预测，可以比较 Ridge 与原模型的验证误差。Ridge 缩小了系数波动，也会引入偏差。机制见 [scikit-learn 线性模型说明](https://scikit-learn.org/stable/modules/linear_model.html#ordinary-least-squares)。

## 追问

**standardization 能消掉共线性吗？**
不能。它改变尺度，不会让两列之间的线性关系消失，但可能改善尺度造成的数值问题。

**高相关一定要删一个特征吗？**
不一定。预测任务要看留出集效果；解释任务则要承认数据可能无法识别各自的独立作用。

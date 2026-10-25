---
id: p3a-meta-ml-foundations-optimizers-scaling-law-clustering
section: meta
order: 815
level: A
title: "Meta ML Foundations：优化器、Scaling Law、K-Means 与 GMM"
quick: "这组题要把机制和适用条件一起讲：交叉熵给分类器什么梯度，Adam 怎样调整更新尺度，缩放律能外推多远，以及 K-Means 硬分配和 GMM 软分配怎样影响重叠样本。"
companies:
  - meta
tags:
  - 场景参考答案
  - 1Point3Acres
  - Frontier-2026-10
  - meta
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Meta ML Foundations：优化器、Scaling Law、K-Means 与 GMM"
    url: https://www.1point3acres.com/interview/problems/company/meta/ml-foundations-optimizers-scaling-law-clustering
    type: secondary
---

## 题目

ML 基础口述题，主题包括优化器、缩放律（scaling law）和聚类。面试官会追问每个概念背后的假设，以及它在什么条件下会失效。

> 来源：一亩三分地 Meta 题卡摘要（2026-10-18 读取），只公开了主题层面的口述清单，没有披露完整问法，也未核实原帖；网站收录不代表公司官方确认，公司内不同岗位之间不要互相套用。下面的具体问法和推导是手册自选的练习，不要把它们或其中的常数归到面试官身上。

## 思路

这组题按机制回答，再说明条件和失败边界。优化器讲更新怎样由梯度算出来；缩放律讲拟合范围和外推验证；聚类则用两个重叠簇说明，一个点硬归一个簇与按概率分给多个簇会有什么区别。每一项都准备一个能手算或验证的小例子。

## 完整非编程练习（参考回答与追问）

### 练习题

把练习固定为四个可以回答的小问：交叉熵为什么能训练分类器（作为讨论优化器时的铺垫）；Adam 和 SGD 的区别；怎么理解缩放律；K-Means 和 GMM 的区别。

### 参考回答

**为什么交叉熵可以训练分类器？**
交叉熵是目标分布 $y$ 下模型负对数概率的期望：$L = -\sum_k y_k \log p_k$。标签是 one-hot 时，它就是正确类别的负 log 概率。设 $p = \mathrm{softmax}(z)$，对 logits 的梯度是 $\partial L / \partial z = p - y$。实现时要说明 mask 和归一化方式。

**Adam 和 SGD 有什么区别？**
SGD 直接沿梯度方向更新。Adam 维护梯度的一阶和二阶指数滑动平均，并做偏差校正：

$$m_t = \beta_1 m_{t-1} + (1 - \beta_1) g_t,\quad v_t = \beta_2 v_{t-1} + (1 - \beta_2) g_t^2$$

$$\theta_t = \theta_{t-1} - \eta \frac{m_t / (1 - \beta_1^t)}{\sqrt{v_t / (1 - \beta_2^t)} + \epsilon}$$

所以每个参数的更新尺度会被历史梯度平方的大小缩放。权重衰减和把 L2 项直接加进 Adam 的梯度，效果不一样：后者也会被 $\sqrt{v_t}$ 缩放，梯度大的参数反而衰减得少。AdamW 把衰减从梯度里解耦出来，直接对参数做衰减。

**怎么理解缩放律？**
它是在指定的数据、模型家族和训练设置下，拟合出来的损失随参数量、数据量或计算量变化的经验关系，不是适用于任意训练预算的物理定律。外推之前要确认数据质量和优化状态与拟合时一致，比如每个规模的学习率是否都调过。

**K-Means 和 GMM 有什么区别？**
K-Means 最小化每个点到所属中心的平方距离，每个点硬分配给一个簇。GMM 最大化混合高斯的似然，用后验责任度做软分配，并且每个簇可以有不同的协方差。GMM 可能出现协方差退化，需要正则和初始化。比较时要明确硬分配、软分配和协方差假设各自的影响。

练习时可以手算两个样本的交叉熵梯度和一轮 Adam 更新，再用留出数据点检验缩放律预测误差，最后画两个重叠簇，比较软分配与硬分配。

### 面试追问与参考回答

**什么时候 SGD 比 Adam 更好？**
一些视觉任务上，调好学习率的 SGD 加动量泛化表现可以和 Adam 持平甚至更好，而且不需要存二阶矩，省一份优化器状态的显存。Transformer 训练中各参数的梯度尺度差异大，Adam 这类自适应方法通常更稳。回答时要说明这是经验观察，依赖具体任务。

**缩放律拟合出来以后，怎么判断能不能往外推？**
留出最大的一两个规模不参与拟合，用拟合曲线预测它们的损失，看误差有多大。如果误差随规模增大而变大，说明外推不可靠，可能是数据开始重复或优化设置没跟上。

**K-Means 和 GMM 有什么联系？**
当 GMM 所有分量的协方差都是相同的 $\sigma^2 I$、且 $\sigma \to 0$ 时，后验责任度会变成 0 或 1，EM 的步骤就退化成 K-Means。所以 K-Means 可以看作 GMM 的一个硬分配极限。

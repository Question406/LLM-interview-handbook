---
id: tesla-hydra-nets
section: xai
order: 7
level: A
title: Tesla：HydraNets 多任务共享骨干，损失权衡和任务干扰
quick: "共享骨干让多任务只提取一次特征，头可独立微调，固定骨干时还能缓存特征。车道、占用等任务可能梯度冲突，先分任务评测，再考虑不确定度加权、冻结骨干、PCGrad 或分组共享；这些通用方法不等于 Tesla 内部配方。"
tags:
  - Tesla
  - HydraNets
  - Multi-task
  - Loss Balancing
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Tesla AI Day 2021
    url: https://www.youtube.com/watch?v=j0z4FweCy4M
    type: primary
  - title: Tesla AI
    url: https://www.tesla.com/AI
    type: primary
  - title: Multi-Task Learning Using Uncertainty to Weigh Losses for Scene Geometry and Semantics
    url: https://arxiv.org/abs/1705.07115
    type: primary
  - title: Gradient Surgery for Multi-Task Learning
    url: https://arxiv.org/abs/2001.06782
    type: primary
---

HydraNets 用共享骨干降低多任务推理成本，但不同任务会争夺特征，需要分别平衡损失和验证质量。比如车道依赖细边缘，占用依赖体积，一个任务的梯度可能损害另一个任务。

Tesla AI Day 2021 公开的 HydraNet 包含共享骨干（讲过 RegNet 一类）、BiFPN 和物体、车道、信号灯、占用相关几何等任务头。这里讨论公开架构与通用训练方法，Kendall 的不确定度加权和 PCGrad 都可作参考，但不能称作 Tesla 内部超参。CVPR 2018 另一篇同名 HydraNets 动态网络论文也需要分开看。

车上要在固定延迟里跑多任务，见 `tesla-latency-slo`。共享骨干公开讲过的好处：

1. 摊推理。八路相机的特征抽一次，多个头共用。
2. 头可独立微调。改车道头不必重训全部。
3. 骨干特征可缓存到盘。微调头时不必每次从图像重算。

检测还依赖实例特征；当这些需求在骨干上产生相反梯度时，多任务共享就可能出现负迁移。

输出上要分清图像空间头和向量空间头。公开栈先把相机特征变到向量空间，再进入 Hydra trunk；Occupancy 的几何层见 `tesla-occupancy-net`。公开材料未给出的 head 总数不补写。

朴素写法 $L=\sum_i \lambda_i L_i$，不同任务的尺度和优先级会使 $\lambda$ 很难手工选择。Kendall 把每个任务看成带噪声的似然，学 $\sigma_i$：

$$
L \approx \sum_i \frac{1}{2\sigma_i^2} L_i + \log \sigma_i.
$$

回归用高斯噪声，分类用温度化的 softmax，形式略不同，思想一样：难任务或高噪声任务自动降权，但不能靠把 $\sigma$ 学爆来逃损失，所以有 $\log \sigma$ 正则。因此权重既反映噪声，也受正则约束。

干扰还在时：

- 冻骨干，只训新头。数据引擎来了一个新失败模式时，先确认是头的问题还是特征的问题。见 `tesla-data-engine`。
- 梯度手术（PCGrad）。若 $\nabla_i\cdot\nabla_j < 0$，把冲突分量投影掉。算力更贵，当 follow-up。
- 可以把几何和语义任务分组，增加组内共享、减少组间共享。
- 任务相关的采样。稀有灯态 clip 过采样，避免损失被高速公路主导。这是数据问题，不是再加大 $\lambda$。

发布前每个头都要有冻结评测集。检测 mAP 提高不能证明占用也提高，直接相加 loss 也会掩盖尺度差异。微调新头时，骨干若仍用从头训练的学习率，可能让其他头退化，需要单独控制。

## 追问

**新任务一定要挂到同一骨干吗？**
不一定。若梯度总是冲突，独立小网络可能更便宜，只要延迟预算还在。共享不是教条。
**缓存特征过期怎么办？**
骨干一改，磁盘上的特征全废。所以骨干发布节奏要慢于头。这是工程约束，不是 trivia。
**不确定度加权会不会让模型放弃难任务？**
会，若没有 $\log \sigma$ 和评测约束。要把稀有类 交并比（IoU，即两个区域的交集与并集之比） / 灯态召回单独拉闸，不能只看总 loss。
**和占用网络的关系？**
Occupancy 可以是 Hydra 上的几何头，也可以是更独立的体积网络。公开演讲把它当几何底层。面试先分层，再谈是否共享全部权重。

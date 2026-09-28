---
id: tesla-hydra-nets
section: xai
order: 7
level: A
title: Tesla：HydraNets 多任务共享骨干，损失权衡和任务干扰
quick: >-
  共享骨干摊推理；任务头可独立微调，骨干特征能缓存。损失不要手调一堆 $\lambda$，用不确定度加权或梯度手术处理干扰。先承认车道和占用会抢特征，再讲冻骨干、分组、或拆头。
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

## 题怎么来的

Tesla AI Day 2021 把视觉栈画成 HydraNet：共享骨干（公开讲过 RegNet 一类）加 BiFPN，再分出一堆任务头——物体、车道、信号灯、占用相关几何等。面试问的是：为什么共享、损失怎么加权、任务互相踩的时候怎么办。这是公开架构题，不是内部超参泄露。学术里 Kendall 的不确定度加权和 PCGrad 是可以说名的工具；不要把 CVPR 2018 另一篇也叫 HydraNets 的动态网络论文当成 Tesla 那套。

## 为什么共享，以及共享的代价

车上要在固定延迟里跑多任务，见 `tesla-latency-slo`。共享骨干公开讲过的好处：

1. 摊推理。八路相机的特征抽一次，多个头共用。
2. 头可独立微调。改车道头不必重训全部。
3. 骨干特征可缓存到盘。微调头时不必每次从图像重算。

代价是任务干扰。车道要细边缘，占用要体积，检测要实例。梯度在骨干里可能反向：一个头的最优特征对另一个头是噪声。多任务不一定正迁移。

输出侧：图像空间头和向量空间头不是同一张图。公开栈是先把相机特征变到向量空间，再进 Hydra 的 trunk。Occupancy 作为几何层，见 `tesla-occupancy-net`。我不会编 Tesla 有多少个 head。

## 损失：先别手调 $\lambda$

朴素写法 $L=\sum_i \lambda_i L_i$，$\lambda$ 会变成周会政治。Kendall 把每个任务看成带噪声的似然，学 $\sigma_i$：

$$
L \approx \sum_i \frac{1}{2\sigma_i^2} L_i + \log \sigma_i.
$$

回归用高斯噪声，分类用温度化的 softmax，形式略不同，思想一样：难任务或高噪声任务自动降权，但不能靠把 $\sigma$ 学爆来逃损失，所以有 $\log \sigma$ 正则。这够应付「你怎么设权重」的第一问。

干扰还在时：

- 冻骨干，只训新头。数据引擎来了一个新失败模式时，先确认是头的问题还是特征的问题。见 `tesla-data-engine`。
- 梯度手术（PCGrad）。若 $\nabla_i\cdot\nabla_j < 0$，把冲突分量投影掉。算力更贵，当 follow-up。
- 分组。几何一组、语义一组，只在组内共享，组间少共享。比「一个骨干打天下」诚实。
- 任务相关的采样。稀有灯态 clip 过采样，避免损失被高速公路主导。这是数据问题，不是再加大 $\lambda$。

错法：把所有任务 loss 直接加起来；用检测 mAP 涨了当占用也涨了；微调一个头却把骨干学习率开得和从头训一样，把别的头打崩。发布前要有各头冻结评测集，不能只看一个联合 loss。

## 追问

- **新任务一定要挂到同一骨干吗？** 不一定。若梯度总是冲突，独立小网络可能更便宜，只要延迟预算还在。共享不是教条。
- **缓存特征过期怎么办？** 骨干一改，磁盘上的特征全废。所以骨干发布节奏要慢于头。这是工程约束，不是 trivia。
- **不确定度加权会不会让模型放弃难任务？** 会，若没有 $\log \sigma$ 和评测约束。要把稀有类 IoU / 灯态召回单独拉闸，不能只看总 loss。
- **和占用网络的关系？** Occupancy 可以是 Hydra 上的几何头，也可以是更独立的体积网络。公开演讲把它当几何底层。面试先分层，再谈是否共享全部权重。

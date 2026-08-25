---
id: gdm-ml-design
section: google
order: 1
level: A
title: Google DeepMind：分子（或其它科学）数据怎么做 ML design？
quick: >-
  先钉任务：预测、生成还是检索；再钉监督信号、泄漏和评测单位（分子 / 构象 / scaffold）。模型选择（图网络、3D
  encoder、语言模型）放在数据约束后面。DeepMind 这轮要的是实验设计，不是套 ResNet。
tags:
  - Google
  - DeepMind
  - ML Design
  - Evaluation
realInterview: true
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: DeepMind ML Design 面经
    url: https://www.1point3acres.com/bbs/thread-1141657-1-1.html
    type: candidate-first-hand
  - title: Highly accurate protein structure prediction with AlphaFold
    url: https://www.nature.com/articles/s41586-021-03819-2
    type: primary
---

## 真题记录

- 公司：Google DeepMind
- 岗位：Machine Learning Engineer
- 来源：一亩三分地 2025 帖「DeepMind - ML Design 面」。公开可见部分：chemistry molecule dataset，字段从 `molecu` 截断；评分 Average / Waitlist
- 同系列：DeepMind coding 非 LC，有候选人说是游戏策略 + BFS/DFS

分子字段被论坛隐藏了，下面按科学 ML design 的通用骨架写。现场以面试官给的 schema 为准，不要背 AlphaFold 当万能答案。

## 先问数据单位，再选模型

科学数据常见坑是把「一张表」当成 i.i.d. 样本。分子任务至少分清：

- 一条样本是分子图、3D 构象，还是带条件的反应？
- 标签是分类、回归（结合能、溶解度）还是生成？
- 切分必须按 scaffold / 时间 / 目标蛋白，随机切会把相似结构泄漏到测试集，线下 RMSE 很好、实验室复现很差。

泄漏比模型选择更致命。白板先画 train/val/test 的切分原则，再画模型。

输入表示：

- 图：原子为点、键为边，适合性质预测。
- 3D：坐标或点云，适合构象 / 对接。坐标和能量对平移旋转要等变或不变，别直接 flatten 成 MLP。
- 串：SMILES / SELFIES，适合生成和语言模型。SMILES 对同一分子不唯一，评测要用 canonical 或图匹配。

DeepMind 风格是：你能不能把归纳偏置说成对数据对称性的约束，而不是「GNN 更先进」。

## 评测要能进实验室

不要只报 accuracy。性质预测用 MAE + 校准；生成用 validity / uniqueness / novelty，再加和训练集的 scaffold 距离。生成模型很容易复制训练分子，novelty 为 0 仍可能「看起来合法」。

若标签贵（湿实验），主动学习、模拟器打分、人类专家抽查要写进 pipeline。AlphaFold 的教训是：关键在数据、等价性、和能在独立结构上评；不是更深的网络名字。

系统题：训练是否要物理模拟在环、batch 怎么按图大小 padding、3D 对齐的计算开销。MLE 岗会追这些，RS 岗会追能量函数和评测是否过拟合 CASP 式公开集。

## 追问

- **为什么不能随机 split？** 相似 scaffold 泄漏。应用要的是新结构上的泛化。
- **和推荐系统 ML design 同构吗？** 同构的是「切分、泄漏、离线指标不等于线上」。不同构的是对称性和实验成本。
- **没有 3D 坐标怎么办？** 先图模型或 SMILES；需要构象再上生成式 3D 或商用构象工具，不要假装 2D 图能替代立体化学。

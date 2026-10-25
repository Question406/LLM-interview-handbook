---
id: gdm-ml-design
section: google
order: 1
level: A
title: Google DeepMind：分子（或其它科学）数据怎么做 ML design？
quick: "先确认任务、样本单位、监督信号和切分方式，再选图网络、3D encoder 或语言模型。科学数据容易因相似结构泄漏而高估效果，评测要落到独立结构、置信度和实验验证上。"
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

## 题目描述

公开面经的分子数据字段被截断；下面仅是手册重构的科学 ML 设计练习，不能据此声称已还原原题数据 schema。

### 场景与目标

为科学数据建立机器学习方案。公开面经只披露 chemistry/molecule dataset，字段不完整，因此本练习允许先选择并声明具体任务，例如由分子结构预测一个数值性质。

### 需要满足的功能

- 先给出样本单位、可用字段、标签来源、输出目标及模型使用者。
- 设计训练、验证和独立测试的完整流程，并解释如何验证新结构或新时间段上的泛化。
- 若选择生成任务，应另定义合法性、新颖性及后续实验验证，而不是沿用回归指标。

### 约束与交付物

缺失的分子字段、数据量、目标性质及实验预算均需明确作为假设。要处理同一分子的不同表示、结构相似样本间的泄漏、标签成本和所选任务所需的几何对称性。

请给出需求边界、对外接口及返回语义、核心数据对象、主要请求的完整生命周期、故障与恢复行为，以及能验证设计是否达标的指标。题目不预先指定数据库、模型或调度算法；需要解释自己作出的选择与代价。

### 请求与结果示例

若练习选择“由分子图预测溶解度”，输入是带原子/键属性的分子，输出是带单位和适用范围的预测；测试应能区分真正的新骨架泛化与仅记住相似训练分子的表现。

## 解题思路与参考答案

做分子等科学数据的 ML design，我会先定义任务和评测单位，再选模型。首先确认一条样本是分子图、3D 构象还是带条件的反应，目标是分类、回归、生成还是检索，标签又来自哪里。比如结合能、溶解度的回归，与生成新分子，监督信号和验收方式就不同。

切分应尽早定下来。科学数据未必是 i.i.d. 样本，随机拆分可能让相似 scaffold 同时进入训练和测试，线下 RMSE 很好，实验室却复现不了。应根据目标按 scaffold、时间或目标蛋白切 train/val/test，把新结构上的泛化作为验收内容。

表示方式跟数据约束走。原子作点、化学键作边的图适合性质预测；坐标或点云适合构象 / 对接，模型需要处理平移旋转下的等变性或不变性，直接 flatten 成 MLP 会丢掉这些约束。SMILES / SELFIES 适合生成与语言模型，同一分子却可能有多个 SMILES，评测要 canonical 化或做图匹配。GNN、3D encoder 的选择，应解释为满足数据的对称性。

性质预测可以报 MAE 与校准；生成评 validity、uniqueness、novelty，再看与训练集的 scaffold 距离。生成结果即使合法，novelty 为 0 仍说明可能只是在复制训练分子。湿实验标签贵时，把主动学习、模拟器打分和专家抽查放进 pipeline。AlphaFold 提醒我们，数据、等价性与独立结构评测都影响科学结论。

系统设计还要考虑物理模拟是否在训练环内、按图大小如何 batch / padding，以及 3D 对齐的计算成本。MLE 岗可能展开这些问题，RS 岗则可能进一步问能量函数，或是否过拟合 CASP 式公开集。

## 追问

**没有 3D 坐标怎么办？**
先用图模型或 SMILES，需要构象时再考虑生成式 3D 或商用构象工具。2D 图无法直接代替立体化学信息。

**和推荐系统的 ML design 有哪些共同点？**
都要处理切分、泄漏和离线指标与实际效果的差距。科学任务还要额外考虑对称性和实验成本。


## 真题记录

- 公司：Google DeepMind
- 岗位：Machine Learning Engineer
- 来源：一亩三分地 2025 帖「DeepMind - ML Design 面」。公开可见部分：chemistry molecule dataset，字段从 `molecu` 截断；评分 Average / Waitlist
- 同系列：DeepMind coding 非 LC，有候选人说是游戏策略 + BFS/DFS

分子字段被论坛隐藏了，下面按科学 ML design 的通用骨架写。现场以面试官给的 字段和类型规范（schema） 为准，不要背 AlphaFold 当万能答案。

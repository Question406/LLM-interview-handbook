---
id: google-alphafold-eval
section: google
order: 14
level: A
title: DeepMind：AlphaFold 类科学 ML 怎么定义评测，不能只报 loss
quick: >-
  科学主张是「结构对不对」，不是训练 FAPE / 交叉熵降了多少。要用独立结构上的 GDT-TS、lDDT，按蛋白家族 /
  时间切分，并报告置信度是否诚实。CASP 那种盲测才接近实验室。设计骨架见 `gdm-ml-design`。
tags:
  - Google
  - DeepMind
  - AlphaFold
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Highly accurate protein structure prediction with AlphaFold
    url: https://www.nature.com/articles/s41586-021-03819-2
    type: primary
  - title: AlphaFold — a solution to a 50-year-old grand challenge in biology
    url: https://www.deepmind.com/blog/alphafold-a-solution-to-a-50-year-old-grand-challenge-in-biology
    type: secondary
---

DeepMind 科学 ML / AlphaFold 后续岗。`gdm-ml-design` 是分子题的设计骨架；本题收在评测协议：把「能发论文的指标」和「训练 loss」拆开。

## 主张是结构，loss 只是优化器看到的数

AlphaFold2 训练有 FAPE、辅助扭转角、蒸馏等。这些告诉你梯度在走。它们不等于「我们解决了折叠」。折叠的公开主张用的是：

- **GDT-TS**（CASP 主指标）：相对实验结构，多少 $C_\alpha$ 落在若干 Å 阈值内，再平均。对整体折叠敏感。
- **lDDT / pLDDT：** 局部原子环境。pLDDT 是模型自己的逐残基置信度，既是产品（用户看哪里可信），也是评测（高置信是否真更准）。
- **RMSD：** 对齐后的均方根，对整体平移旋转后的大误差敏感，单独报容易被一个 loop 带偏。

Nature 文和 CASP14 比的是当时尚未公开的实验结构，不是训练集上的 FAPE。面试第一句：指标必须对应科学声明。声明是坐标，就评坐标；声明是结合亲和，就评亲和，别拿重建 loss 顶替。

## 切分和泄漏比网络名字致命

蛋白质不是 i.i.d. 序列。随机按序列划 train/test，同源蛋白、同一超家族会漏过去，测试 RMSE 很好，新折叠一塌糊涂。正确方向：

- 按序列聚类 / 超家族切，测试是训练没见过的折叠类型。
- 时间切分：训练只用某日期前的 PDB，之后解析的结构当测试。CASP 本质是时间 + 盲测。
- 多序列比对（MSA）不能含测试结构对应的泄漏序列处理；模板更要挡。否则模型在抄库，不是预测。

没有这条，报 SOTA 是刷公开集。DeepMind 风格是你能不能说出「评测单位是一条链、一个复合物、还是一个构象」。复合物和单体的泄漏模式不同。分子性质预测同构，见 `gdm-ml-design`。

## 置信度是评测的一部分，不是装饰

AlphaFold 能用，很大程度因为 pLDDT / PAE 告诉你哪段别信。科学 ML 要校准：pLDDT 高的残基，lDDT 是否真高。只报全局 GDT、不报「模型知道自己不知道」，实验室会在乱 loop 上做实验。

失败模式也要进协议：无序区、新折叠、抗体 CDR、配体。平均 GDT 可以被大量简单球蛋白抬上去。切片报：易 / 难 CASP 难度档、有无模板、长度。这和搜索要切头腰尾是同一纪律，见 `google-search-quality`。

系统题：推理要跑多久、要不要 MSA 搜索、能量最小化后处理算不算模型的一部分。评测必须冻结这套 pipeline。训练 loss 不含搜索步骤，所以不能用 loss 代替端到端。

错法：只给验证集 FAPE；用 PDB 随机 split；把 pLDDT 当准确率本身（它是置信度，要单独校准）；声称「有了 AlphaFold 就不用实验结构了」：盲测和实验仍是锚。

FAPE 是训练时对局部坐标系的误差，便于回传；GDT-TS 是评测时相对实验结构的全局重合。两者相关，但 FAPE 低不等于 CASP 高，尤其在没有模板的新折叠上。面试把这两个字母说成一个东西会扣分。

## 追问

- **为什么不用训练 loss 当论文主表？** Loss 不可跨架构比较，也不对应 Å。审稿人和生物学家要的是结构度量。CASP 盲测的意义就是提交时看不见实验结构；训练集 FAPE 再漂亮也代替不了这一刀。
- **没有实验结构怎么评生成模型？** 物理可行性、与已知家族的距离、湿实验 / 模拟器抽样。novelty 为 0 说明在复制训练集。
- **CASP 还能当唯一锚吗？** 公开后会过拟合竞赛风格。要持续时间切分和外部实验室复现，不能只刷一届 CASP。
- **和推荐离线指标同构吗？** 同构的是「代理 ≠ 真实主张」。不同构的是：这里的真实主张是物理结构，不是点击。
- **pLDDT 高能不能当准确率？** 不能。它是置信度，要单独做可靠性图。湿实验贵，评测协议就是产品的一部分：哪些残基可以进实验。把置信度当准确率，实验室会在乱 loop 上开工。

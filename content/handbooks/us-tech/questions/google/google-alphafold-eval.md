---
id: google-alphafold-eval
section: google
order: 14
level: A
title: DeepMind：AlphaFold 类科学 ML 怎么定义评测，不能只报 loss
quick: "AlphaFold 类任务要用独立实验结构评估 GDT-TS、lDDT 等结构指标，并检查 pLDDT 是否校准。训练 loss 只说明优化进展；按家族和时间切分、CASP 式盲测及实验室复现，才能检验新结构上的泛化。"
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

AlphaFold 类科学 ML 应按科学主张评测：声称坐标准，就与独立实验结构比较；声称结合亲和准，就评亲和。训练 loss 降了只能说明优化有进展，无法直接代替这些结论。比如一个不可靠的 loop，若模型却给出高置信度，实验室据此开展实验就可能走错方向。

AlphaFold2 训练涉及 FAPE、辅助扭转角、蒸馏等目标。FAPE 测局部坐标系的误差，便于回传；GDT-TS 则衡量相对实验结构的全局重合，是 CASP 主指标，把 $C_\alpha$ 落在若干 Å 阈值内的比例再平均。两者相关，FAPE 低却不保证没有模板的新折叠上 CASP 成绩高。Nature 文和 CASP14 对照的是当时未公开的实验结构，盲测时提交者看不到答案。

还要看局部环境的 lDDT，以及模型逐残基置信度 pLDDT。pLDDT 与 PAE 让用户知道哪些位置不可靠，评测时要检查高 pLDDT 的残基是否真的有高 lDDT，并单独画可靠性图。RMSD 是对齐后的均方根误差，对大偏差敏感，单独报告可能被一个 loop 左右。训练 loss 不能直接跨架构比较，也不直接对应 Å 尺度，因此论文主表需要结构指标。

蛋白质不是 i.i.d. 序列，随机按序列划 train/test，会让同源蛋白或同一超家族泄漏。可以按序列聚类 / 超家族切分，让测试包含训练未见的折叠，或按时间只用某日期前的 PDB，之后解析的结构作测试。模板和 MSA 的处理也要挡住测试结构相关泄漏。还应明确评测单位是一条链、复合物还是构象，单体与复合物的泄漏方式不同。

指标按无序区、新折叠、抗体 CDR、配体，以及 CASP 易 / 难档、有无模板、长度拆开。大量简单球蛋白会抬高平均 GDT，掩盖难例。公开 CASP 也可能被逐渐过拟合，所以持续时间切分和外部实验室复现仍然需要，实验结构不会因模型出现而失去作用。

系统评测要冻结整套 pipeline：推理耗时、MSA 搜索、能量最小化后处理是否计入，都应说清。训练 loss 不包含搜索步骤，无法代表端到端成本或效果。

## 追问

**没有实验结构，怎么评生成模型？**
先看物理可行性、与已知家族距离，再安排湿实验或模拟器抽样。Novelty 为 0 提示可能复制了训练集，合法结构本身不足以证明有新发现。

**和推荐离线评测有什么共同点？**
都要区分代理指标与真正主张。这里要验证的是物理结构，因此置信度校准、实验和盲测也是产品可用性的一部分。

相关：`gdm-ml-design`、`google-search-quality`

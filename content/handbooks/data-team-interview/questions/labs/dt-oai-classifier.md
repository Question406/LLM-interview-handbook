---
id: dt-oai-classifier
section: labs
order: 41
level: S
title: OpenAI 高频笔试：现场训分类器、摸数据集，data 岗怎么开口？
quick: "先了解字段、标签来源和缺失，再按文档或近重复簇划分训练、开发、固定评测。建立简单基线，按语言、长度、来源分析误差并校准阈值。只调用 fit、报告总体 AUC，不足以证明分类器可用于数据过滤。"
companies:
  - apple
tags:
  - OpenAI
  - Classifier
  - Data Quality
  - Apple
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Classifier Training and Analysis (AceOffer, OpenAI reports)
    url: https://aceoffer.app/interviews/oai_classifier_training_and_analysis
    type: secondary
  - title: FineWeb-Edu
    url: https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-edu
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

这类现场题不仅要求训练分类器，还要解释数据和标签是否可靠。先了解表，再划分数据、拟合模型。AceOffer 将它记录为 OpenAI 高频 ML coding：在 Colab 用 pandas、numpy、sklearn 或 torch 训练分类器并分析数据集。

数据岗可以把它看成小规模质量分类器问题：种子标签从哪来，模型是否按语言校准，假阳性会不会误删好代码。不要一开始就 `fit()`，也不要把整张表作为训练集。

## 编码顺序

1. 检查 schema：哪列是标签、谁标注、缺多少值，类别是否接近 99:1。
2. 按文档 id 哈希划分。近重复簇不能跨训练和开发；命中评测 n-gram 的行先放隔离区。
3. 建立多数类、长度和词袋基线。新模型如果不如长度规则，先分析原因再考虑 transformer。
4. 按语言、长度和来源报告误差。总体 F1 高，不代表低资源语言可用。
5. 检查停止训练与上线条件：开发集校准 ECE 改善，同时固定切片没有退步，再判断能否用于过滤。

## 在苹果场景中的来源与校准

正例可以来自评测失败分析、许可研究集和已验证合成，不默认使用用户对话。按语言、数据域调阈值，代码分组不用网页教育价值头。需要能画校准曲线和切片错误表。评测内容如果进入特征或标签，比较就失效，见 `dt-hash-split-code`、`dt-quality-clf-synth`。

AceOffer 记录过 19 次，最近报道到 2026 年 9 月。招聘邮件表述是现场写机器学习代码、训练分类器、探索数据集。

## 追问

- 标签是模型打的怎么办？当弱监督，先人抽查校准。直接当金标可能让分类器学教师文风，见 `dt-quality-clf-synth`。
- 只看准确率够吗？过滤时还要关注误删有用 token 的代价，优先检查精确率；召回与配额一起考虑。
- 与 CoderPad 质量过滤题有什么关系？一题解释模型分如何训练，另一题实现启发式与模型分的组合。

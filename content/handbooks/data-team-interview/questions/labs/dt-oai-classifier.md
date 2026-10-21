---
id: dt-oai-classifier
section: labs
order: 41
level: S
title: OpenAI 高频笔试：现场训分类器、摸数据集，data 岗怎么开口？
quick: "先看清字段、标签来源和缺失，再按文档或近重复簇划分训练、开发和固定评测集，然后建简单基线，按语言、长度、来源分析误差并校准阈值。这道题考的是数据和标签是否可靠：只调用 fit、报一个总体 AUC，证明不了分类器能拿去做数据过滤。"
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

这道现场题要训一个分类器，考的重点是你能不能判断数据和标签是否可靠。所以顺序是先看表，再划分数据，最后才拟合模型。直接对整张表 `fit()`，近重复和评测泄漏会让开发集分数虚高。

对数据岗来说，可以把它当成一个小规模质量分类器问题：种子标签从哪来，模型有没有按语言校准，假阳性会不会误删好代码。

## 编码顺序

1. **检查 schema。** 哪列是标签、谁标的、缺多少值，类别比例是不是接近 99:1。
2. **按文档 id 哈希划分。** 近重复簇不能跨训练集和开发集；命中评测 n-gram 的行先放进隔离区。
3. **建基线。** 多数类、长度规则、词袋各做一个。新模型如果还不如长度规则，先分析原因，再考虑上 transformer。
4. **切片报误差。** 按语言、长度、来源分别报。总体 F1 高，不代表低资源语言可用。
5. **判断能否上线。** 开发集上的校准 ECE 有改善，同时固定切片没有退步，才考虑用于过滤。

## 实践中的变化

正例可以来自评测失败分析、许可研究集和验证过的合成数据。阈值按语言和数据域分别调，代码分组单独训分类头，网页教育价值的分类头用在代码上会失准。现场要能画出校准曲线和切片错误表。如果评测内容进了特征或标签，所有比较都会失效，见 `dt-hash-split-code`、`dt-quality-clf-synth`。

## 题目来源

AceOffer 把它记为 OpenAI 高频 ML coding 题，记录过 19 次，最近一次报道在 2026 年 9 月：在 Colab 里用 pandas、numpy、sklearn 或 torch 训练分类器并分析数据集。招聘邮件的说法是现场写机器学习代码、训练分类器、探索数据集。

## 追问

- **标签是模型打的怎么办？** 当弱监督用，先人工抽查校准。直接当金标，分类器可能学到教师模型的文风，见 `dt-quality-clf-synth`。
- **只看准确率够吗？** 不够。过滤时还要算误删有用 token 的代价，优先检查精确率；召回率和配额一起考虑。
- **和 CoderPad 质量过滤题有什么关系？** 这题解释模型分怎么训出来，那题实现启发式规则和模型分的组合。

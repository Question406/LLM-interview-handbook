---
id: dt-oai-classifier
section: labs
order: 41
level: S
title: OpenAI 高频笔试：现场训分类器、摸数据集，data 岗怎么开口？
quick: >-
  先看清字段、标签来源和缺失，再按文档或 near-duplicates cluster 划分训练、开发和固定 evaluation set，然后建简单
  baseline，按语言、长度、来源分析误差并对 threshold 做 calibration。这题考的是数据和标签靠不靠得住：只调用 fit、报一个总体
  AUC，说明不了分类器能拿去过滤数据。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: 'Classifier Training and Analysis (AceOffer, OpenAI reports)'
    url: 'https://aceoffer.app/interviews/oai_classifier_training_and_analysis'
    type: secondary
  - title: FineWeb-Edu
    url: 'https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-edu'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

这道现场题表面上是训分类器，考的是你能不能判断数据和标签靠不靠得住。所以顺序是先看表，再划分数据，最后才拟合模型。直接对整张表 `fit()`，near-duplicates 和 evaluation leakage 会让 development set 分数虚高。

比如拿到的表里，标签列几乎全是 0，同一篇文档换了个标题出现了好几次，有的在 training set、有的在 development set。这时候准确率和 development set 分数都会很好看，模型其实什么都没学到。

对数据岗来说，可以把它当成一个小规模的质量分类器问题：seed 标签从哪来，模型有没有按语言做 calibration，假阳性会不会误删好代码。

动手时我先查 schema：哪列是标签、谁标的、缺多少值、类别比例是不是接近 99:1。然后按文档 id 哈希划分，near-duplicates cluster 不能跨 training set 和 development set，命中评测 n-gram 的行先放进隔离区。接着建几个 baseline，多数类、长度规则、词袋各做一个；新模型如果还不如长度规则，先分析原因，再考虑上 transformer。误差按语言、长度、来源分别报，总体 F1 高，不代表 low-resource 语言能用。development set 上的 calibration ECE 有改善，同时固定 evaluation slices 没有退步，才考虑拿去过滤。现场要能画出 calibration curve 和 evaluation slices 错误表。

正例可以来自评测失败分析、许可研究集和验证过的 synthetic data。阈值按语言和数据域分别调，代码分组单独训分类头，网页教育价值的分类头用在代码上会失准。评测内容要是进了特征或标签，所有比较都会失效，见 `dt-hash-split-code`、`dt-quality-clf-synth`。

## 追问

**这题出现得多吗？**
很多。AceOffer 把它记为 OpenAI 高频 ML coding 题，记录过 19 次，最近一次报道在 2026 年 9 月：在 Colab 里用 pandas、numpy、sklearn 或 torch 训练分类器并分析数据集。招聘邮件的说法是现场写机器学习代码、训练分类器、探索数据集。

**标签是模型打的怎么办？**
当弱监督用，先人工抽查 calibration。直接当 gold labels，分类器可能学到 teacher model 的文风，见 `dt-quality-clf-synth`。

**只看准确率够吗？**
不够。过滤时还要算误删有用 token 的代价，优先检查精确率；召回率和配额一起考虑。

**和 CoderPad 质量过滤题有什么关系？**
这题讲模型分怎么训出来，那题实现启发式规则和模型分的组合。

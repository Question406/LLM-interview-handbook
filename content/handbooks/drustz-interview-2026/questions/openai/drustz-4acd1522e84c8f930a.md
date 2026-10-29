---
id: drustz-4acd1522e84c8f930a
section: openai
order: 99
level: A
title: 'Dataset Exploration: Detect Label Noise and Choose Metrics'
quick: >-
  original-structured-preparation-guide · Dataset Exploration: Detect Label
  Noise and Choose Metrics
companies:
  - openai
tags:
  - DrustZ
  - original-structured-preparation-guide
  - OpenAI · 题库与复习指南
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: DrustZ / Mingrui Zhang · pinned source
    url: >-
      https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json
    type: primary
  - title: 作者记录的原始来源
    url: >-
      https://www.1point3acres.com/interview/problems/efbf2b5a-6863-4c73-947f-003612c370f3
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 数据探索：发现标签噪声并选择评估指标

> 内容定位：当前标题指向“数据探索、标签噪声、指标选择”，本地笔记也确认了 noisy-data 题族；但没有证据表明下面的列结构、阈值或样例就是原题。以下是依据已知主题编写的原创准备指南，不是会员题面复原。

## 题目要做什么

拿到一个包含特征、观测标签和可选标注者信息的数据集后，先做探索性分析，判断问题是否来自缺失值、重复样本、类别失衡或错标，再为分类任务选择合适的离线指标。重点不是“调用一个模型就结束”，而是用可复现证据解释数据问题。

## 数据或需求

建议把输入抽象为 `sample_id, features..., observed_label, annotator_id`。需要输出：数据质量摘要、疑似错标样本的排序列表、推荐指标及理由、一个不泄漏的训练/验证切分方案。若没有人工金标，结论只能叫“疑似噪声”，不能叫“确定错标”。

## 例子

若 10,000 条数据中正类只有 5%，全预测为负也有 95% accuracy，却完全找不到正类。此时 PR-AUC、正类 recall、precision@k 或按业务成本加权的指标更有意义。又如同一图片哈希在训练集和验证集各出现一次，即使标签相同也会造成数据泄漏。

## 解法

按固定顺序检查，避免看到模型结果后再随意挑指标：

```text
schema -> missing/range -> exact & near duplicates
       -> class/annotator/time slices -> split leakage
       -> out-of-fold probabilities -> suspicious-label ranking
```



先验证类型、取值范围和唯一键；再统计每类数量、每位标注者覆盖率与冲突矩阵。对文本或图像可用 embedding 近邻检查“内容相似但标签相反”的样本。模型侧必须用 out-of-fold 概率：若模型对另一标签高度确信、多个独立模型一致、且近邻标签也相反，才把样本排到复核队列前面。指标选择由代价决定：类别均衡且代价对称可用 accuracy；长尾多分类用 macro-F1；稀有正类检索用 PR-AUC；概率要进入下游决策时还要看 log loss、Brier score 与 calibration curve。

## 复杂度

基础统计为 `O(ND)`；哈希去重通常为 `O(N)` 时间和空间；朴素两两近邻为 `O(N²)`，大数据应使用近似最近邻。K 折 out-of-fold 训练成本约为单次训练的 `K` 倍。

## 边界与验证

- 在全量数据上预处理后再切分会泄漏；
- 时间漂移数据应按时间切分，而非随机切分；
- 模型低置信度可能代表真正的难样本，不一定是错标；
- macro 与 micro 指标应同时展示，避免平均数掩盖长尾类别；
- 阈值要在验证集确定，最终测试集只评一次。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/efbf2b5a-6863-4c73-947f-003612c370f3)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

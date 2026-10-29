---
id: drustz-2499cef4b20de93acd
section: openai
order: 71
level: A
title: Human Labeling and Training a Classifier (ML Coding)
quick: >-
  original-structured-preparation-guide · Human Labeling and Training a
  Classifier (ML Coding)
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
      https://www.1point3acres.com/interview/problems/22767524-0d52-4710-9b9f-88894be4a71a
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 人工标注数据与分类器训练

> 内容定位：本地笔记能确认“Human-Data 分类器 / 多标注员噪声”这一题族，但没有保存当前 UUID 的逐字题面、函数签名或数据文件。下面把它整理成一套可直接练习的原创版本；它是同方向准备题，不应当当作会员原文。

## 题目要做什么

给定样本特征 `X`，以及若干条 `(sample_id, annotator_id, label)` 人工标注，先把同一样本的多个标签聚合成训练目标，再训练一个简单分类器。除了给出模型分数，还要说明怎样发现不可靠的标注者，以及清洗前后的差异是否可信。

## 数据或需求

- 同一样本可能有 1 个或多个标注，部分标注缺失或冲突；
- 标签可以先按二分类处理，扩展到多分类时使用每类概率；
- 应保留一小份专家金标集，只用于calibration和最终评估；
- 至少报告 accuracy 之外的一项指标，并避免用测试集选择阈值。

## 例子

样本 `s1` 被 A、B、C 标成 `[1, 1, 0]`，多数票为 1；`s2` 为 `[0, 0, 1]`。若 C 在大量重叠样本上都与可靠共识相反，可以降低 C 的权重，但不能仅凭两条记录断定 C 是坏标注者。

## 解法

第一版先做多数票，并计算每位标注者与“排除自己后的多数票”之间的一致率，避免把自己的票同时放进答案与评分：

```text
for sample in samples:
    soft_label[sample] = normalized_vote_counts(sample)
for annotator in annotators:
    score = agreement(label, consensus_without_this_annotator)
    weight = shrink_toward_global_mean(score, number_of_labels)
train classifier on soft_label, using sample confidence as weight
```



小样本标注者的分数要向总体均值收缩；类别不平衡时还应分标签计算 precision/recall，防止“永远标多数类”的人得到虚高准确率。进阶方案可以交替估计真实标签与标注者混淆矩阵，思想类似 Dawid–Skene。最后用固定金标验证集比较 baseline 与清洗版，报告差值、bootstrap confidence interval和按类别切片结果。

## 复杂度

设标注总数为 `A`、样本数为 `N`、特征维数为 `D`。投票与一致率统计为 `O(A)` 时间、`O(N + R)` 空间，`R` 是标注者数；分类器训练复杂度取决于模型，线性模型每轮约为 `O(ND)`。

## 边界与验证

- 单个标注的样本不能用于可靠地评价该标注者；
- 专家也可能出错，金标应有复核流程；
- 不要把“与多数票不同”直接等价为恶意或低质量；
- 清洗前后必须使用相同的数据切分与随机种子；
- 若过滤后分数上涨但少数类召回下降，应视为失败而非改进。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/22767524-0d52-4710-9b9f-88894be4a71a)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

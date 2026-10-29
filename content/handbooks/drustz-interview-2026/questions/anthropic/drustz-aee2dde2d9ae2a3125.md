---
id: drustz-aee2dde2d9ae2a3125
section: anthropic
order: 47
level: A
title: Debug / Fix an Extremely Randomized Trees (ExtraTrees) Implementation in NumPy
quick: >-
  original-structured-preparation-guide · Debug / Fix an Extremely Randomized
  Trees (ExtraTrees) Implementation in NumPy
companies:
  - anthropic
tags:
  - DrustZ
  - original-structured-preparation-guide
  - Anthropic · 题库与复习指南
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
      https://www.1point3acres.com/interview/problems/84071144-2958-4ae1-aeca-131436139171
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# 调试 NumPy ExtraTrees 实现

> 完整 starter code 没有公开。旧资料误挂了 Anthropic 申请/OA 流程，现已移除；下面是与标题一致的原创调试指南。

## ExtraTrees 应该做什么

Extremely Randomized Trees 与随机森林相近，但通常会为候选特征随机生成切分阈值，再从这些随机切分中选择 impurity 改善最大的一个。多棵树独立训练，分类取投票或平均概率，回归取预测均值。

## 逐层检查

1. **bootstrap 语义**：ExtraTrees 常默认使用全部样本而不是 bootstrap，必须按题目参数实现；
2. **特征sampling**：每个节点只考虑 `max_features` 个特征，且应无放回抽样；
3. **阈值范围**：阈值必须位于该节点当前样本的 feature min/max 之间；
4. **空子树**：随机阈值可能让一侧为空，应resampling或跳过；
5. **impurity 加权**：左右 impurity 要按样本数加权；
6. **停止条件**：纯节点、最大深度、最小样本数和没有有效 split；
7. **随机性**：每棵树和每个节点使用可复现但不同的 RNG stream；
8. **预测聚合**：类别标签不能直接数值平均，应投票或平均 class probability。

## 调试方法

先用只有一个特征、四五个样本的小数据，打印每个节点的样本索引、阈值和左右分支；再与 sklearn 的趋势而非逐节点结构比较，因为随机切分不会完全一致。固定 seed，覆盖 constant feature、重复值和单类标签。

## 复杂度

若有 `T` 棵树、`n` 个样本、每节点考察 `m` 个特征，实际成本取决于深度与阈值评估方式。平衡树的常见粗略训练量级是 `O(T × m × n log n)`；预测单样本约为 `O(T × depth)`。

## 边界

NaN、全常数特征、空数组、类别不是连续整数、tie vote、最大深度为 0，以及复制数组导致的峰值内存过高。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/84071144-2958-4ae1-aeca-131436139171)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

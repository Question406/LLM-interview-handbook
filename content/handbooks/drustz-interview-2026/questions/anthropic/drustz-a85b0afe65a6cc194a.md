---
id: drustz-a85b0afe65a6cc194a
section: anthropic
order: 28
level: A
title: Mech Interp Take Home
quick: original-structured-preparation-guide · Mech Interp Take Home
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
      https://www.1point3acres.com/interview/problems/company/anthropic/mech-interp-take-home
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

# Mechanistic Interpretability Take-Home：复现 Double Descent

> 修正说明：旧正文讲的是 Anthropic 如何设计 AI-resistant take-home，而不是公开摘要所说的 double-descent 实验，已经移除。

## 可以确认的任务

设计并运行一个小模型实验，复现 sample-aspect double descent；解释为什么会出现 double descent，并提出后续实验。公开页面没有给出数据集、模型和时间预算的完整细节。

## 最小可复现实验

一种清晰方案是使用合成回归：

1. 固定特征维度 `p` 和带噪声的真实线性规律；
2. 改变训练样本数 `n`，让比例 `n/p` 从远小于 1 扫到远大于 1；
3. 对每个 `n` 训练同一种模型到相同停止条件；
4. 在固定、足够大的测试集上测 MSE；
5. 每个点使用多个随机种子，画均值和误差条；
6. 同时记录 train error、test error、参数范数和最小奇异值。

```python
for n in sample_sizes:
    for seed in seeds:
        X_train, y_train = make_data(n=n, p=p, seed=seed)
        model = fit_model(X_train, y_train)
        record(n, train_mse(model), test_mse(model), parameter_norm(model))
```



预期在接近 interpolation threshold 的区域出现测试误差峰值：模型刚好有能力把训练噪声也拟合掉，解对数据扰动非常敏感；继续增加样本后，估计变稳定，测试误差再次下降。

## 如何让解释更有说服力

- 用无噪声数据做对照，观察峰值是否减弱；
- 改变 label noise，检查峰值高度；
- 改变regularization或 early stopping；
- 观察设计矩阵谱和 condition number；
- 区分改变样本数、参数数和训练时间产生的不同 double-descent 现象。

## 复杂度

若每个点用 closed-form least squares，单次成本取决于 `n` 与 `p`，常见上界约为 `O(min(np², n²p))`；使用梯度训练则应按步数、batch 和模型 forward 成本分析。整个 sweep 还要乘以样本规模点数与随机种子数。

## 边界

必须固定测试分布和预处理，避免每个 `n` 使用不同难度数据；误差峰值可能被单次随机噪声伪造，所以必须报告多随机种子。结果没有出现峰值时也应诚实分析，而不是挑选图形。

### 来源与内容类型

- Content kind: `original-structured-preparation-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/company/anthropic/mech-interp-take-home)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

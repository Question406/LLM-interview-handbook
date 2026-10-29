---
id: drustz-7a7c541d8ae9fa5ced
section: openai
order: 58
level: A
title: Reproduce Double Descent in Linear Regression
quick: external-concept-guide · Reproduce Double Descent in Linear Regression
companies:
  - openai
tags:
  - DrustZ
  - external-concept-guide
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
      https://www.1point3acres.com/interview/problems/a5c37bda-f1a1-528d-b6aa-0968b57e250a
    type: secondary
---
> DrustZ 整理的复习指南。公司与轮次信息沿用作者的来源记录。

## Double Descent 复现实验准备指南（非当前 OJ 逐字题面）

构造可复现的合成回归数据，并让模型维度从欠参数化逐步跨过插值阈值进入过参数化区域。对每个维度使用相同训练/测试协议，记录训练误差和测试 MSE；在线性回归无唯一解时使用最小范数解或伪逆。

预期现象是：测试误差先下降，在参数量接近样本量、模型刚好能插值训练集时上升形成峰值，随后在更宽的过参数化区域再次下降。实验必须固定随机种子、重复多个 seed，并分别改变噪声强度、样本数和regularization强度，以区分真正的 double-descent 曲线与随机波动。

实现时应检查矩阵 shape、数值稳定性和奇异矩阵处理，并绘制模型复杂度对训练/测试误差的曲线。外部概念资料可帮助理解实验设计，但当前 UUID 的精确输入输出仍应以官方页面为准。

### 来源与内容类型

- Content kind: `external-concept-guide`
- [原始来源](https://www.1point3acres.com/interview/problems/a5c37bda-f1a1-528d-b6aa-0968b57e250a)

---

来源：[DrustZ / Mingrui Zhang · 1acre3points_crawl/data/questions.json](https://github.com/DrustZ/ai_interview_prep_2026/blob/04316c111d0e4b75ca2ab8de0e6b42379727946e/1acre3points_crawl/data/questions.json)。作者整理资料；许可和第三方来源范围见阅读指南。

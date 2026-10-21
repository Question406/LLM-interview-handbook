---
id: dt-doremi-mix
section: labs
order: 5
level: A
title: DoReMi：小模型 Group DRO 学出的配比，能不能直接拿来训大模型？
quick: "不能直接用，适合当核心预训练配比的初值。DoReMi 优化的是相对参考模型的最坏域损失，目标里没有摘要人评或工具成功率，所以仍要在大模型和下游切片上验证。另外要先清理并合理划分数据域，否则最差域是垃圾时会被持续加权。"
companies:
  - apple
tags:
  - DoReMi
  - Data Mix
  - Google
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "DoReMi: Optimizing Data Mixtures Speeds Up Language Model Pretraining"
    url: https://arxiv.org/abs/2305.10429
    type: primary
  - title: Data Mixing Laws
    url: https://arxiv.org/abs/2403.16952
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

不能直接拿来用，适合当起点。DoReMi 给核心预训练提供配比初值，尤其是网页、书籍、代码等域的损失可以互相比较时；下游任务和人评仍需要实际尝试不同配比后再定。

## 为什么它能迁移

Xie et al. 的公开实验用 280M 代理做 Group DRO，再用所得权重训练 8B。在 The Pile 上，平均 few-shot 比默认权重高 6.5 点，达到基线准确率所需的步数减少约 2.6×；在 GLaM 数据上，结果接近用下游任务调过的权重。也就是说，论文验证过约 30× 的规模迁移。

## 为什么不能直接用

DoReMi 最小化的是相对参考模型的最坏域额外损失（worst-case excess loss），优化目标里没有摘要人评这类下游指标。把 280M 代理学到的 $r$ 直接当成大模型配方，可能与最终目标不一致。

它对域的划分也很敏感。如果最差域主要是垃圾页，DRO 会不断增加垃圾的权重；把代码和网页混成同一个域，也会扭曲它学到的权重。

公开报告里的配比也不来自 DRO，例如 AFM 报告的多语 8%→30%、视觉 60 / 10 / 28.5 / 1.5。

## 怎么用代理结果

1. 先对各域做质量检查，解决垃圾问题之后再跑 DRO。
2. 合理分域：许可数据和验证过的合成数据各自成域，和大批网页分开。
3. 在大模型上用下游切片确认，见 `dt-data-mix-quota`。Mixing law 拟合 $L_i(r)$，DoReMi 学习 $r$，两者都依赖小代理，都需要这一步。
4. 不同规模的模型能力边界不同，同一个 $r$ 不能保证对小模型和大模型都合适。可以分别跑代理，或者用退火做小规模测试来验证新来源，见 `dt-llama-anneal`。

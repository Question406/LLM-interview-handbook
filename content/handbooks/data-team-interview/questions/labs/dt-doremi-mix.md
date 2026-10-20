---
id: dt-doremi-mix
section: labs
order: 5
level: A
title: DoReMi：小模型 Group DRO 学出的配比，能不能直接拿来训大模型？
quick: "DoReMi 的小模型 DRO 权重可用作核心预训练配比初值，但仍要在大模型和产品切片上验证。它优化域损失，不直接优化摘要人评或工具成功率。先清理并合理划分数据域，避免最差域是垃圾、反而被持续加权。"
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

DoReMi 可以为核心预训练提供配比起点，尤其是网页、书籍、代码等域的损失可比较时。产品任务和人评仍需要实际尝试不同配比。AFM 公开的多语 8%→30%、视觉 60 / 10 / 28.5 / 1.5 等比例，不是 DRO 自动给出的结果。

DoReMi 最小化相对参考模型的最坏域额外损失（worst-case excess loss），不是直接优化通知摘要人评。把 280M 代理学到的 $r$ 直接当成大模型配方，可能与最终目标不一致。若最差域主要是垃圾页，DRO 会增加垃圾权重；把代码和网页混成同一域，也会影响它学到的权重。

## 怎么使用代理结果

先对各域做质量检查，再用 DRO 学配比。许可数据和验证合成可分别成域，不要与大批网页直接合为一个分组。

Mixing law 拟合 $L_i(r)$，DoReMi 学习 $r$，两者都依赖小代理。大模型仍需要下游切片确认，见 `dt-data-mix-quota`。端侧与 server 的能力边界不同，可以分别跑代理，或通过退火小规模测试新来源，见 `dt-llama-anneal`。

Xie et al. 的公开实验用 280M 代理做 Group DRO，再用所得权重训练 8B。在 The Pile 上，平均 few-shot 比默认权重高 6.5 点，达到基线准确率所需步数减少约 2.6×。GLaM 数据上的结果接近用下游任务调过的权重。

## 追问

- 最差域始终是垃圾页怎么办？先解决质量问题，再做 DRO，否则算法可能持续增加垃圾权重。
- 同一 $r$ 能用于 3B 和 server 吗？论文验证过约 30× 的规模迁移，但不能保证所有产品目标相同。分别验证，或先做小规模退火实验。

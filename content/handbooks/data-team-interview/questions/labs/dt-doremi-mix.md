---
id: dt-doremi-mix
section: labs
order: 5
level: A
title: DoReMi：小模型 Group DRO 学出的配比，能不能直接拿来训大模型？
quick: "不能直接用，拿来当核心预训练配比的初值比较合适。DoReMi 优化的是相对参考模型的最坏域损失，目标里没有摘要人评或工具成功率，所以还要在大模型和下游切片上验证。另外要先清理并合理划分数据域，否则最差域是垃圾时它会被一直加权。"
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

不能直接拿来用，当起点合适。DoReMi 能给核心预训练一个配比初值，尤其是网页、书籍、代码这些域的损失可以互相比较的时候；下游任务和人评还得实际试几种配比再定。

它能当起点，是因为迁移效果确实不错。Xie et al. 的公开实验用 280M 代理做 Group DRO，再拿学到的权重训 8B。在 The Pile 上，平均 few-shot 比默认权重高 6.5 点，达到基线准确率所需的步数少了约 2.6×；在 GLaM 数据上，结果接近用下游任务调过的权重。

不能直接用，是因为它优化的目标和你最终要的不一样。DoReMi 最小化的是相对参考模型的最坏域额外损失（worst-case excess loss），目标里没有摘要人评这类下游指标，把 280M 代理学到的 $r$ 直接当成大模型配方，可能和最终目标对不上。

它对域的划分也很敏感。举个例子，网页里最差的那个域如果主要是垃圾页，DRO 看到它的额外损失一直降不下来，就会不断给垃圾加权重。把代码和网页混成同一个域，学到的权重也会被扭曲。

所以我会先对各域做质量检查，把垃圾清掉再跑 DRO。分域时，许可数据和验证过的合成数据各自成域，和大批网页分开。跑完之后在大模型上用下游切片确认，见 `dt-data-mix-quota`。

## 追问

**DoReMi 和 mixing law 是什么关系？**
两者都靠小代理。Mixing law 拟合 $L_i(r)$，DoReMi 学习 $r$，最后都要在大模型的下游切片上确认。

**同一个 $r$，小模型和大模型都能用吗？**
不能保证。不同规模的模型能力边界不同，可以分别跑代理，或者用退火做小规模测试来验证新来源，见 `dt-llama-anneal`。

**公开报告里的配比是 DRO 学出来的吗？**
不是。比如 AFM 报告的多语 8%→30%、视觉 60 / 10 / 28.5 / 1.5，都不来自 DRO。

**代理该多小？**
论文用的是 280M 代理配 8B 目标，验证过的规模迁移大约是 30×。目标模型更大时，同样要在下游切片上确认。

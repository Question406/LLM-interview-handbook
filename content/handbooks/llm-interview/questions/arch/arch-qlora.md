---
id: arch-qlora
section: arch
order: 12
level: A
title: QLoRA 的 NF4、Double Quantization、Paged Optimizer 是什么？
quick: >-
  QLoRA 以 4-bit NF4 保存冻结 base weights，只训练 LoRA；NF4 针对近似正态权重设计量化 levels，Double
  Quantization 再压量化常数，Paged Optimizer 缓解显存峰值。
tags:
  - QLoRA
  - Quantization
realInterview: false
status: published
format: markdown
provenance: legacy-handbook-v2
updatedAt: 2026-08-21
sources:
  - title: ↗ QLoRA
    url: 'https://arxiv.org/abs/2305.14314'
    type: legacy-reference
---

常见误区是：把 QLoRA 说成「整个训练都是 INT4 算术」，或「和 GPTQ 一样是推理量化」。核心节省来自冻结基座用 4-bit 存、不为 full base 保存 Adam 状态；前向通常仍把量化权重解到更高精度再乘激活。LoRA 更新仍是 $\Delta W=\frac{\alpha}{r}BA$，只是 $W$ 以 NF4 驻留。

## NF4：按正态分位数摆 levels

预训练权重近似零均值正态。均匀 4-bit 在尾部太疏、中心太密。NF4（NormalFloat4）按标准正态定义 $2^4-1$ 个分位，让离散格子匹配该分布，再对每个 block 做缩放。面试一句话：同样 4 bit，格子按数据分布而不是按均匀网格切。

这与 MoE / SwiGLU / RoPE 正交：量化的是线性权重存储；门控 $\mathrm{SiLU}(xW_1)\odot xW_2$ 和旋转 $R_{\theta,m}$ 仍在解量化后的计算里发生。

## Double Quantization 与 Paged Optimizer

每个 block 的 scale（以及可能的零点）本身也占 FP32 / FP16。参数量大时，这些常数加起来可观。Double Quantization 再把量化常数做一次低比特量化，省的是「元数据」而不是再砍一遍权重精度。

Adam 一类优化器对每个可训练参数存 $m,v$，全参微调时状态是权重的数倍。QLoRA 只给 LoRA 的 $A,B$ 建状态，基座无优化器状态。即便如此，长序列激活 + 优化器仍可能顶满。Paged Optimizer 用统一内存把优化器页在 CPU/GPU 间换入换出，削峰值，不改变算法。

## 和普通 LoRA / 推理量化的边界

QLoRA 是训练期显存技巧：冻结基座，用 4-bit 保存权重，只训练低秩适配器。GPTQ / AWQ 是推理权重量化，服务期不必有 LoRA。合并 adapter 后若要再量化，是另一步，不要说成 QLoRA 自动给出 4-bit 部署模型。

## 追问

- **NF4 和 INT4 哪个准？** 对近似正态权重，NF4 通常更贴；最终看下游，不是名字。
- **能不能训 MoE 专家？** 可以挂在专家线性层上，但路由 logits 量化误差会放大负载不均，要单独看 overflow。
- **Paged Optimizer 是不是 offload 全部模型？** 不是。它分页的是优化器状态，权重仍按 QLoRA 路径在 GPU 上解量化计算。
